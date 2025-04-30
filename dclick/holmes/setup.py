# std
from functools import cache
from typing import Callable, Generator, Literal, Self
# interno
from . import modelos
# externo
import bot

@cache
def client_singleton () -> bot.http.Client:
    """Criar o http `Client` configurado com o `host`, `token` e timeout
    - O Client ficará aberto após a primeira chamada na função devido ao `@cache`"""
    host, token = bot.configfile.obter_opcoes_obrigatorias("holmes", "host", "token")
    return bot.http.Client(
        base_url = host,
        headers  = { "api_token": token },
        timeout  = 120,
    )

class QueryTaskV2:
    """Classe para realizar a construção da Query das tasks e iteração sobre os resultados obtidos
    - Versão `v2` do `/search`
    - Variáveis utilizadas `[holmes] -> "host", "token"`
    - Variáveis dinâmicas para aplicação dos termos conforme seção `[holmes.QueryTask.termos]`
        - `{ "field": "nome_opção", "type": "is", "value": "valor_opção"` }"""

    _from: int = 0
    size: int = 50
    sort: str = "due_date"
    order: Literal["asc", "desc"] = "asc"
    terms: list[dict[str, str]]

    def __init__ (self) -> None:
        secao = "holmes.QueryTask.termos"
        opcoes = bot.configfile.opcoes_secao(secao) if bot.configfile.possui_secao(secao) else []
        self.terms = [
            {
                "field": opcao,
                "type": "is",
                "value": bot.configfile.obter_opcao_ou(secao, opcao)
            }
            for opcao in opcoes
        ]

    @property
    def query_body (self) -> dict:
        """Body de requisição. Alterar as propriedades abaixo no `self` para alteração
        - `_from, size` início e fim da janela de quantidade de itens máximos no retorno
        - `sort` campo que será feito o sort
        - `order` ordem que será feito o sort
        - `terms` termos de filtro do resultado"""
        return {
            "query": {
                "context": "task",
                "from": self._from,
                "size": self.size,
                "sort": self.sort,
                "order": self.order,
                "groups": [
                    {
                        "terms": self.terms
                    }
                ]
            }
        }

    def adicionar_termo (self, **kwargs: str) -> Self:
        """Adicionar termo de filtro no `terms`
        - Informar no `kwargs` os campos e seus valores
        - Exemplo: `adicionar_termo(field="status", type="is", value="opened")`"""
        self.terms.append(kwargs)
        return self

    def adicionar_termo_status (self, value="opened") -> Self:
        """Adicionar o termo de filtro `status=value`"""
        return self.adicionar_termo(field="status", type="is", value=value)

    def consultar (self) -> modelos.QueryRaizTaskV2:
        """Realizar a consulta da query conforme `query_body`"""
        bot.logger.informar("Procurando por tarefas no Holmes")
        response = client_singleton().post("/v2/search", json=self.query_body)

        assert response.is_success, f"O status code '{response.status_code}' foi diferente do esperado"
        raiz, erro = bot.formatos.Unmarshaller(modelos.QueryRaizTaskV2).parse(response.json())
        assert not erro, f"O conteúdo da resposta não está de acordo com o esperado\n\t{erro}"

        bot.logger.informar(f"Consulta resultou em '{len(raiz.docs)}' tarefa(s) de um total de '{raiz.total}'")
        return raiz

    def paginar_query (
            self,
            filtro: Callable[[modelos.DocTaskV2], bool | bot.tipagem.SupportsBool] | None = None,
            limite = 50,
        ) -> Generator[modelos.DocTaskV2, None, None]:
        """Realizar a consulta da query com paginação até a quantidade `limite`
        - `filtro` para obter apenas tarefas que satisfaçam a condição informada"""
        assert limite >= 1, f"Limite '{limite}' inválido"

        filtro = filtro or (lambda t: True)
        while limite > 0:
            docs = self.consultar().docs
            quantidade = len(docs)
            self._from += quantidade

            for doc in docs:
                if limite <= 0: break
                try:
                    if filtro(doc):
                        limite -= 1
                        yield doc
                except: pass

            # não há mais páginação
            if quantidade < self.size: break

    def paginar_tarefas_query (
            self,
            filtro: Callable[[modelos.Tarefa], bool | bot.tipagem.SupportsBool] | None = None,
            limite = 50,
        ) -> Generator[modelos.Tarefa, None, None]:
        """Realizar a consulta das tarefas da query com paginação até a quantidade `limite`
        - `filtro` para obter apenas tarefas que satisfaçam a condição informada"""
        tarefa = modelos.Tarefa()
        def filtro_query (doc: modelos.DocTaskV2) -> bool:
            nonlocal tarefa, filtro
            tarefa = consultar_tarefa(doc.id)
            try: return filtro(tarefa) if filtro else True
            except: return False

        for _ in self.paginar_query(filtro_query, limite):
            yield tarefa

def consultar_tarefa (id_tarefa: str) -> modelos.Tarefa:
    """Consultar a tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando tarefa({id_tarefa}) no Holmes")

    response = client_singleton().get(f"/v1/tasks/{id_tarefa}")
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"
    tarefa, erro = bot.formatos.Unmarshaller(modelos.Tarefa).parse(response.json())
    assert not erro, f"O conteúdo da resposta não está de acordo com o esperado\n\t{erro}"

    return tarefa

def consultar_documento_tarefa (id_tarefa: str, id_documento: str) -> modelos.DocumentoTarefa:
    """Consultar o documento `id_documento` da tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando documento({id_documento}) da tarefa({id_tarefa}) no Holmes")

    response = client_singleton().get(f"/v1/tasks/{id_tarefa}/documents/{id_documento}")
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"

    return modelos.DocumentoTarefa(response.content, dict(response.headers))

def consultar_processo (id_processo: str) -> modelos.Processo:
    """Consultar o processo `id_processo`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando processo({id_processo}) no Holmes")

    response = client_singleton().get(f"/v1/processes/{id_processo}")
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"
    processo, erro = bot.formatos.Unmarshaller(modelos.Processo).parse(response.json())
    assert not erro, f"O conteúdo da resposta não está de acordo com o esperado\n\t{erro}"

    return processo

def consultar_detalhes_processo (id_processo: str) -> modelos.DetalhesProcesso:
    """Consultar os detalhes do processo `id_processo`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando detalhes do processo({id_processo}) no Holmes")

    response = client_singleton().get(f"/v1/processes/{id_processo}/details")
    body = response.json()
    body = body.get("instance", {}) if isinstance(body, dict) else {}
    body["property_values"] = [body["property_values"].pop(0)]
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"
    detalhes, erro = bot.formatos.Unmarshaller(modelos.DetalhesProcesso).parse(body)
    assert not erro, f"O conteúdo da resposta não está de acordo com o esperado\n\t{erro}"

    return detalhes

def consultar_itens_tabela_tarefa (
        id_tarefa: str,
        id_tabela: str,
        page: int = 1,
        per_page: int = 100
    ) -> modelos.ItensTabelaTarefa:
    """Consultar itens da tabela `id_tabela` da tarefa `id_tarefa`
    - `page, per_page` realizar a paginação. Default: Primeiros 100
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando itens da tabela({id_tabela}) da tarefa({id_tarefa}) no Holmes")

    response = client_singleton().get(
        url = f"/v1/tasks/{id_tarefa}/tables/{id_tabela}/table_items",
        params = { "page": page, "per_page": per_page }
    )
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"
    itens, erro = bot.formatos.Unmarshaller(modelos.ItensTabelaTarefa).parse(response.json())
    assert not erro, f"O conteúdo da resposta não está de acordo com o esperado\n\t{erro}"

    return itens

def tomar_acao_tarefa (
        tarefa: modelos.Tarefa,
        acao: modelos.Action,
        propriedades: list[dict[Literal["id", "value", "text"], str]] | None = None
    ) -> None:
    """Tomar `acao` na `tarefa`
    - `propriedades` caso seja necessário um adicional (motivo de pendência)
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    assert isinstance(tarefa, modelos.Tarefa), f"Tipo inesperado para a Tarefa: '{tarefa}'"
    assert isinstance(acao, modelos.Action), f"Tipo inesperado para a Ação: '{acao}'"
    assert isinstance(propriedades, (list, type(None))), f"Tipo inesperado para as Propriedades: '{propriedades}'"

    bot.logger.informar(f"Tomando ação({acao.name}) na tarefa({tarefa.id}) do Holmes")

    response = client_singleton().post(
        f"/v1/tasks/{tarefa.id}/action",
        json = {
            "task": { 
                "action_id": acao.id,
                "confirm_action": True,
                "property_values": propriedades or []
            }
    })
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"

def assumir_tarefa (id_tarefa: str) -> None:
    """Assumir a tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> "host", "token", "id_usuario"`"""
    bot.logger.informar(f"Assumindo tarefa({id_tarefa}) no Holmes")

    usuario = bot.configfile.obter_opcoes_obrigatorias("holmes", "id_usuario")[0]
    response = client_singleton().put(
        f"/v1/tasks/{id_tarefa}/assign",
        json = { "user_id": usuario }
    )
    assert response.is_success, f"O status code '{response.status_code}' foi diferente do esperado"

__all__ = [
    "QueryTaskV2",
    "assumir_tarefa",
    "consultar_tarefa",
    "tomar_acao_tarefa",
    "consultar_processo",
    "consultar_documento_tarefa",
    "consultar_detalhes_processo",
    "consultar_itens_tabela_tarefa",
]