# std
import certifi, functools
from typing import Any, Self, Literal
from datetime import datetime as Datetime
# interno
import dclick
# externo
import bot
from bot.formatos import Unmarshaller

type STATUS = Literal["nova", "pendente", "concluida", "erro", "cancelada"]
type STATUS_EVENTO = Literal["sucesso", "erro"]

@functools.cache
def client_singleton () -> dclick.http.ClienteHttp:
    """Criar o http `Client` configurado com o `host`, `apikey` e timeout
    - O Client ficará aberto após a primeira chamada na função devido ao `@cache`"""
    host, apikey = bot.config.central_processamento.obter("host", "apikey")
    return dclick.http.ClienteHttp(
        base_url = host,
        headers  = { "x-api-key": apikey },
        timeout  = 30,
        verify   = certifi.where(),
        follow_redirects = True,
    )

class Evento (Unmarshaller, rename="camel"):
    message: str
    """Mensagem do evento"""
    status: STATUS_EVENTO
    """Status do evento"""
    created_at: Datetime
    """Data de criação"""

class Solicitacao (Unmarshaller, rename="camel"):
    """Modelo de uma solicitação na Cental de Processamento
    ### Utilizar `Solicitacao.Consultar()` para realizar a consulta"""

    id: str
    """ID único"""
    identification: str
    """Nome identificador"""
    data: dict[str, Any]
    """Dados adicionais de criação"""
    output_data: dict[str, Any] | None
    """Dados de saída"""
    status: STATUS
    """Status atual da solicitação
    - `nova` Status inicial de uma solicitação recém-criada (terminal: não)
    - `pendente` Solicitação aguardando ou em processamento (terminal: não)
    - `concluida` Solicitação finalizada com sucesso (terminal: sim)
    - `erro` Solicitação finalizada com erro (terminal: sim)
    - `cancelada` Solicitação cancelada pelo usuário (terminal: sim)"""
    created_at: Datetime
    """Data de criação"""
    updated_at: Datetime | None
    """Data da última atualização"""
    completed_at: Datetime | None
    """Data de conclusão
    - `status = terminal()`"""
    retry_count: int
    cancelled_by: str | None
    """ID do usuário que cancelou
    - `status=cancelada`"""
    cancellation_reason: str | None
    """Motivo do cancelamento
    - `status=cancelada`"""
    events: list[Evento] = []
    """Eventos (mais recente primeiro)"""

    def __repr__ (self) -> str:
        return f"<central.Solicitacao id={self.id!r} status={self.status!r}>"

    @classmethod
    def Consultar (cls, requestTypeCode: str | None = None,
                        status: STATUS | None = None,
                        excludeTerminal: bool = True,
                        startDate: Datetime | None = None,
                        endDate: Datetime | None = None,
                        dataFilter: str | None = None,
                        limit: int = 50,
                        offset: int = 0) -> list["Solicitacao"]:
        """Consultar as solicitações de acordo com os parâmetros
        - Variáveis utilizadas `[central_processamento] -> host, apikey`

        ### Parâmetros
        - `requestTypeCode` Filtra por código do tipo de solicitação
        - `status` Filtra por status específico
        - `excludeTerminal` Exclui status terminais (padrão: True)
        - `startDate` Data de criação mínima
        - `endDate` Data de criação máxima
        - `dataFilter` Filtro JSONB nos dados da solicitação
        - `limit` Máximo de resultados (padrão: 50) (máximo: 200)
        - `offset` Offset para paginação (padrão: 0)"""
        dclick.logger.debug("Consultando as solicitações na Central de Processamento")
        query = {
            "limit": limit,
            "offset": offset,
            "status": status,
            "dataFilter": dataFilter,
            "excludeTerminal": excludeTerminal,
            "requestTypeCode": requestTypeCode,
            "startDate": startDate.isoformat(timespec="seconds") if startDate is not None else None,
            "endDate":  endDate.isoformat(timespec="seconds") if endDate is not None else None,
        }
        return (
            client_singleton()
            .get("/api/request-center/requests",
                query = { k: v for k, v in query.items() if v is not None })
            .esperar_sucesso("Resposta inesperada ao consultar solicitações na Central de Processamento")
            .unmarshal_many(Solicitacao)
        )

    def pendente (self) -> bool:
        """Checar se a solicitação está pendente
        - `status = nova | pendente`"""
        return self.status in ("nova", "pendente")

    def terminal (self) -> bool:
        """Checar se a solicitação está concluída
        - `status = concluida | erro | cancelada`"""
        return not self.pendente()

    def possui_evento (self, mensagem: str, status: STATUS_EVENTO | None = None) -> bool:
        """Checar se a solicitação possui um evento com a `mensagem`"""
        return any(
            mensagem == evento.message and (
                status is None
                or
                status == evento.status
            )
            for evento in self.events
        )

class SolicitacaoPendente (Unmarshaller, rename="camel"):
    """Modelo de uma solicitação pendente na Cental de Processamento
    ### Utilizar `Solicitacao.Consultar()` para realizar a consulta"""

    id: str
    """ID único"""
    identification: str
    """Nome identificador"""
    data: dict[str, Any]
    """Dados adicionais de criação"""
    output_data: dict[str, Any] | None
    """Dados de saída"""
    status: Literal["nova", "pendente"]
    """Status atual da solicitação
    - `nova` Status inicial de uma solicitação recém-criada (terminal: não)
    - `pendente` Solicitação aguardando ou em processamento (terminal: não)"""
    created_at: Datetime
    """Data de criação"""
    updated_at: Datetime | None
    """Data da última atualização"""
    retry_count: int
    events: list[Evento] = []
    """Eventos (mais recente primeiro)"""

    def __repr__ (self) -> str:
        return f"<central.SolicitacaoPendente id={self.id!r} status={self.status!r}>"

    @classmethod
    def Consultar (cls, requestTypeCode: str | None = None,
                        startDate: Datetime | None = None,
                        endDate: Datetime | None = None,
                        dataFilter: str | None = None,
                        limit: int = 50,
                        offset: int = 0) -> list["SolicitacaoPendente"]:
        """Consultar as solicitações com `status = nova | pendente`
        - Variáveis utilizadas `[central_processamento] -> host, apikey`

        ### Parâmetros
        - `requestTypeCode` Filtra por código do tipo de solicitação
        - `startDate` Data de criação mínima
        - `endDate` Data de criação máxima
        - `dataFilter` Filtro JSONB nos dados da solicitação
        - `limit` Máximo de resultados (padrão: 50) (máximo: 200)
        - `offset` Offset para paginação (padrão: 0)"""
        dclick.logger.debug("Consultando as solicitações pendentes na Central de Processamento")
        query = {
            "limit": limit,
            "offset": offset,
            "dataFilter": dataFilter,
            "requestTypeCode": requestTypeCode,
            "startDate": startDate.isoformat(timespec="seconds") if startDate is not None else None,
            "endDate":  endDate.isoformat(timespec="seconds") if endDate is not None else None,
        }
        return (
            client_singleton()
            .get("/api/request-center/requests/open",
                query = { k: v for k, v in query.items() if v is not None })
            .esperar_sucesso("Resposta inesperada ao consultar solicitações pendentes na Central de Processamento")
            .unmarshal_many(SolicitacaoPendente)
        )

    def possui_evento (self, mensagem: str, *, status: STATUS_EVENTO | None = None) -> bool:
        """Checar se a solicitação possui um evento com a `mensagem`"""
        return any(
            mensagem == evento.message and (
                status is None
                or
                status == evento.status
            )
            for evento in self.events
        )

    def adicionar_evento (self, evento: str, *, sucesso: bool = True) -> Self:
        """Adicionar o `evento`, com status de sucesso ou erro, na solicitação
        - Utilizado o `status=pendente`
        - Atualizado campos de `self` com o retorno"""
        body = {
            "status": "pendente",
            "event": {
                "message": evento,
                "status": "sucesso" if sucesso else "erro"
            }
        }

        solicitacao = (
            client_singleton()
            .patch(f"/api/request-center/requests/{self.id}/status", json=body)
            .esperar_sucesso(f"Resposta inesperada ao adicionar um evento na Solicitação({self.id}) na Central de Processamento")
            .unmarshal(SolicitacaoPendente)
        )
        update = solicitacao.updated_at or Datetime.now()
        self.updated_at = update
        self.status = "pendente"
        self.output_data = solicitacao.output_data
        self.retry_count = solicitacao.retry_count
        self.events.insert(0, Evento(evento, "sucesso" if sucesso else "erro", update))

        return self

    def atualizar_output_data (self, output_data: dict[str, Any] | None, *,
                                     evento: tuple[STATUS_EVENTO, str] | None = None) -> Self:
        """Atualizar o campo `outputData` com opção para adicionar um `evento`
        - Atualizado campos de `self` com o retorno"""
        body = { "outputData": output_data }
        if evento is not None: body["event"] = {
            "status": evento[0],
            "message": evento[1],
        }

        solicitacao = (
            client_singleton()
            .patch(f"/api/request-center/requests/{self.id}/output-data", json=body)
            .esperar_sucesso(f"Resposta inesperada ao atualizar o outputData da Solicitação({self.id}) na Central de Processamento")
            .unmarshal(SolicitacaoPendente)
        )
        update = solicitacao.updated_at or Datetime.now()
        self.updated_at = update
        self.output_data = solicitacao.output_data
        self.retry_count = solicitacao.retry_count
        if evento is not None:
            self.events.insert(0, Evento(evento[1], evento[0], update))

        return self

    def Finalizar (self, evento: str, *, sucesso: bool = True) -> Solicitacao:
        """Finalizar a solicitação com `status = concluida | erro` com o `evento`
        - Retornado uma nova `Solicitacao` pois a solicitação não estará mais pendente"""
        body = {
            "status": "concluida" if sucesso else "erro",
            "event": {
                "message": evento,
                "status": "sucesso" if sucesso else "erro"
            }
        }

        solicitacao = (
            client_singleton()
            .patch(f"/api/request-center/requests/{self.id}/status", json=body)
            .esperar_sucesso(f"Resposta inesperada ao finalizar a Solicitação({self.id}) na Central de Processamento")
            .unmarshal(Solicitacao)
        )
        if not solicitacao.events:
            _evento = Evento(evento, "sucesso" if sucesso else "erro", solicitacao.updated_at or Datetime.now())
            solicitacao.events.append(_evento)
            solicitacao.events.extend(self.events)

        return solicitacao

    def Cancelar (self, motivo: str, *, evento: str | None = None) -> Solicitacao:
        """Cancelar a solicitação pelo `motivo` informado
        - `evento=None` usado a mensagem do `motivo`
        - Retornado uma nova `Solicitacao` pois a solicitação não estará mais pendente"""
        body = {
            "status": "cancelada",
            "cancellationReason": motivo,
            "event": {
                "message": evento or motivo,
                "status": "erro"
            }
        }

        solicitacao = (
            client_singleton()
            .patch(f"/api/request-center/requests/{self.id}/status", json=body)
            .esperar_sucesso(f"Resposta inesperada ao cancelar a Solicitação({self.id}) na Central de Processamento")
            .unmarshal(Solicitacao)
        )
        if not solicitacao.events:
            _evento = Evento(evento or motivo, "erro", solicitacao.updated_at or Datetime.now())
            solicitacao.events.append(_evento)
            solicitacao.events.extend(self.events)

        return solicitacao

__all__ = [
    "Solicitacao",
    "SolicitacaoPendente",
]