# std
from datetime import datetime
from email.message import Message
from email.parser import HeaderParser
import base64, certifi, mimetypes, functools
from typing import Any, Self, Literal, Callable
# interno
import dclick
from dclick.holmes import modelos
# externo
import bot
from bot.estruturas import Caminho
from bot.tipagem import SupportsBool
from bot.formatos import Unmarshaller

@functools.cache
def client_singleton () -> dclick.http.ClienteHttp:
    """Criar o http `Client` configurado com o `host`, `token` e timeout
    - O Client ficará aberto após a primeira chamada na função devido ao `@cache`"""
    host, token = bot.config.holmes.obter("host", "token")
    return dclick.http.ClienteHttp(
        base_url = host,
        headers  = { "api_token": token },
        timeout  = 120,
        verify   = certifi.where(),
    )

class Processo (Unmarshaller):
    """Modelo de um processo no Holmes
    ### Utilizar `Processo.Consultar()` para realizar a consulta"""

    id: str
    name: str
    status: modelos.STATUS
    identifier: str
    solution_id: str
    created_at: datetime
    current_activities: list[modelos.Activity]

    @classmethod
    @bot.erro.adicionar_prefixo(lambda args, _: f"Falha Processo.Consultar(id_processo={args[1]!r}) no Holmes")
    def Consultar (cls, id_processo: str) -> "Processo":
        """Consultar o processo `id_processo`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Consultando processo({id_processo}) no Holmes")
        return (
            client_singleton()
            .get(f"/v1/processes/{id_processo}")
            .esperar_status_code(200)
            .unmarshal(Processo)
        )

    def __repr__ (self) -> str:
        return f"<holmes.Processo id={self.id!r} status={self.status!r}>"

    def __eq__ (self, other: object) -> bool:
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__ (self) -> int:
        return hash(self.id)

    def obter_atividade (self, filtro: Callable[[modelos.Activity], SupportsBool]) -> modelos.Activity | None:
        """Obter a atividade do `processo` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for atividade in self.current_activities:
            try:
                if filtro(atividade): return atividade
            except Exception: pass

    def Detalhes (self) -> list[modelos.DetalhesProcesso]:
        """Consultar o campo `property_values` nos detalhes do processo `self.id`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Consultando detalhes do processo({self.id}) no Holmes")
        property_values = (
            client_singleton()
            .get(f"/v1/processes/{self.id}/details")
            .esperar_status_code(200)
            .json(esperar=dict[str, dict[str, Any]])
                .get("instance", {})
                .get("property_values", [])
        )
        return modelos.DetalhesProcesso.UnmarshalMany(property_values)

    def Historico (self) -> list[modelos.HistoryItem]:
        """Consultar o histórico do processo `self.id`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Consultando histórico do processo({self.id}) no Holmes")
        histories = (
            client_singleton()
            .get(f"/v1/processes/{self.id}/history")
            .esperar_status_code(200)
            .json(esperar=dict[str, list[dict[str, Any]]])
            .get("histories", [])
        )
        return modelos.HistoryItem.UnmarshalMany(histories)

    def Documentos (self) -> list[modelos.DocumentItem]:
        """Consultar os documentos do processo `self.id`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Consultando documentos do processo({self.id}) no Holmes")
        documents = (
            client_singleton()
            .get(f"/v1/processes/{self.id}/documents")
            .esperar_status_code(200)
            .json(esperar=dict[str, list[dict[str, Any]]])
            .get("documents", [])
        )
        return modelos.DocumentItem.UnmarshalMany(documents)

class Documento:
    """Modelo com conteúdo de um arquivo de Documento no Holmes
    ### Utilizar `Documento.Consultar()` para realizar a consulta
    ### Utilizar `Documento.Remover()` para remover um documento
    ### Utilizar `Documento.Upload()` para criar um documento
    ### Utilizar `Documento.Classificacao()` para consultar a classificação de um documento"""

    conteudo: bytes
    """Conteúdo do documento em bytes"""
    __message: Message

    @classmethod
    def Consultar (cls, document_id: str) -> "Documento":
        """Consultar o documento `document_id`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Consultando documento({document_id}) no Holmes")
        response = (
            client_singleton()
            .get(f"/v1/documents/{document_id}/download")
            .esperar_status_code(200, f"Falha ao consultar documento({document_id}) no Holmes")
        )
        return Documento(response.content, response.headers_dict)

    @classmethod
    def Remover (cls, document_id: str, descricao: str | None = None) -> None:
        """Remover o documento `document_id`
        - `descricao` para informar o motivo da remoção
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Removendo documento({document_id}) no Holmes")
        (
            client_singleton()
            .delete(
                url = f"/v1/documents/{document_id}",
                query = { "description": descricao } if descricao else None
            )
            .esperar_status_code(204, f"Falha ao remover documento({document_id}) no Holmes")
        )

    @classmethod
    def Classificacao (cls, document_id: str) -> modelos.ClassificacaoDocumento:
        """Consultar a classificação do documento `id_documento`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Consultando classificação do documento({document_id}) no Holmes")
        return (
            client_singleton()
            .get(f"/v1/documents/{document_id}/classify")
            .esperar_status_code(200)
            .unmarshal(modelos.ClassificacaoDocumento)
        )

    @classmethod
    def Upload (cls, nome_extensao: str,
                     conteudo: str | bytes,
                     *,
                     classificacao: modelos.ClassificacaoDocumentoDict | None = None) -> modelos.UploadDocumento:
        """Realizar o upload do documento `nome_extensao` via `base64`
        - `conteudo=bytes` transformado para `base64`
        - `conteudo=str` esperado como `base64`
        - `classificacao` aplicar classificação no documento
            - `{ "nature_id": "60f862d9f5a395000da95cf2", "property_values": [] }`
            - `{ "nature_id": "60f862d9f5a395000da95cf2", "property_values": [{ "id": "cnpj", "value": "03095314000618" }] }`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Realizando upload de documento({nome_extensao}) no Holmes")
        return ( 
            client_singleton()
            .post(
                url = "/v1/documents",
                json = {
                    "classification": classificacao or {},
                    "document": {
                        "filename": nome_extensao,
                        "base64_file": (
                            conteudo
                            if isinstance(conteudo, str)
                            else base64.b64encode(conteudo).decode()
                        )
                    }
                }
            )
            .esperar_status_code(200, "Falha ao realizar upload de documento no Holmes")
            .unmarshal(modelos.UploadDocumento)
        )

    def __init__ (self, conteudo: bytes, headers: dict[str, str]) -> None:
        self.conteudo = conteudo
        self.__message = HeaderParser().parsestr("\n".join(
            f"{header}: {valor}"
            for header, valor in headers.items()
        ))

    def __repr__ (self) -> str:
        return f"<holmes.Documento nome={self.__message.get_filename('blob')!r} tipo={self.tipo!r}>"

    @property
    def tipo (self) -> str:
        return self.__message.get_content_type()

    @property
    def tamanho (self) -> int:
        return len(self.conteudo)

    @property
    def charset (self) -> str | None:
        return self.__message.get_content_charset() or None

    def nome_arquivo (self, default="blob") -> str:
        """Obter o nome do arquivo com o valor do header `Content-Disposition`
        - `default` caso não encontrado"""
        return self.__message.get_filename(default)

    def salvar (self, diretorio: Caminho) -> Caminho:
        """Salvar o conteúdo no `diretório`, conforme charset, e retornar o caminho"""
        charset = self.charset
        mode = "wb" if not charset else "w"
        destino = diretorio / self.nome_arquivo()
        with open(destino.path, mode, encoding=charset) as writer:
            writer.write(self.conteudo.decode(charset) if charset else self.conteudo)
        return destino

class Tarefa (Unmarshaller):
    """Modelo de uma tarefa no Holmes
    ### Utilizar `Tarefa.Consultar()` para realizar a consulta"""

    id: str
    name: str
    status: modelos.STATUS
    task_id: str
    identifier: str
    template_id: str
    assignee_id: str | None

    process_id: str
    process_name: str
    process_status: str
    process_created_at: datetime

    tables: list[modelos.Table]
    actions: list[modelos.Action]
    documents: list[modelos.Document]
    properties: list[modelos.Property]

    @classmethod
    @bot.erro.adicionar_prefixo(lambda args, _: f"Falha Tarefa.Consultar(id_tarefa={args[1]!r}) no Holmes")
    def Consultar (cls, id_tarefa: str) -> "Tarefa":
        """Consultar a tarefa `id_tarefa`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug("Consultando uma tarefa no Holmes", id_tarefa=id_tarefa)
        return (
            client_singleton()
            .get(f"/v1/tasks/{id_tarefa}")
            .esperar_sucesso()
            .unmarshal(Tarefa)
        )

    def __repr__ (self) -> str:
        return f"<holmes.Tarefa id={self.id!r} status={self.status!r}>"

    def __eq__ (self, other: object) -> bool:
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__ (self) -> int:
        return hash(self.id)

    def obter_acao (self, filtro: Callable[[modelos.Action], SupportsBool]) -> modelos.Action | None:
        """Obter a ação da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for action in self.actions:
            try: 
                if filtro(action): return action
            except Exception: pass

    def obter_propriedade (self, filtro: Callable[[modelos.Property], SupportsBool]) -> modelos.Property | None:
        """Obter a propriedade da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for propriedade in self.properties:
            try:
                if filtro(propriedade): return propriedade
            except Exception: pass

    def obter_documento (self, filtro: Callable[[modelos.Document], SupportsBool]) -> modelos.Document | None:
        """Obter o documento da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for document in self.documents:
            try:
                if filtro(document): return document
            except Exception: pass

    def obter_tabela (self, filtro: Callable[[modelos.Table], SupportsBool]) -> modelos.Table | None:
        """Obter a tabela da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for table in self.tables:
            try:
                if filtro(table): return table
            except Exception: pass

    def Processo (self) -> "Processo":
        """Consultar o processo `self.process_id`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        return Processo.Consultar(self.process_id)

    def Documento (self, id_ou_conditional: str) -> "Documento":
        """Consultar o documento pelo `id` ou pelo `conditional` da tarefa `id_tarefa`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Consultando documento({id_ou_conditional}) da tarefa({self.id}) no Holmes")

        documento = self.obter_documento(
            lambda d: id_ou_conditional == d.id
                      or id_ou_conditional.lower() in d.conditional.lower())
        assert documento is not None, f"Documento {id_ou_conditional!r} não encontrado na tarefa({self.id})"

        response = (
            client_singleton()
            .get(f"/v1/tasks/{self.id}/documents/{documento.id}")
            .esperar_status_code(200, f"Falha ao consultar documento({id_ou_conditional}) da tarefa({self.id}) no Holmes")
        )
        return Documento(response.conteudo, response.headers_dict)

    def AnexarDocumento (self, id_documento: str, documento: tuple[str, bytes], *,
                               mime_type: str | None = None) -> Self:
        """Realizar upload do documento `id_documento` com o conteúdo `documento` na tarefa
        - `documento` sendo o `(nome_extensão, conteúdo)`
        - `mime_type` para informar manualmente o tipo do conteúdo
        - `mime_type=None` feito o advinho do tipo com base na extensão com fallback para `application/octet-stream`
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Anexando documento id({id_documento}) nome({documento[0]}) na tarefa({self.id}) no Holmes")
        nome_extensao, conteudo = documento
        mime = (mime_type or mimetypes.guess_type(nome_extensao)[0]) or "application/octet-stream"
        (
            client_singleton()
            .post(url = f"/v1/tasks/{self.id}/documents/{id_documento}",
                  arquivos = { "file": (nome_extensao, conteudo, mime) })
            .esperar_status_code(204, f"Falha ao anexar documento na tarefa({self.id}) do Holmes")
        )

        if self.obter_documento(lambda d: d.id == id_documento) is None:
            self.documents = self.Consultar(self.id).documents

        return self

    def Assumir (self, id_usuario: str | None = None) -> Self:
        """Assumir a tarefa para o `id_usuario`
        - Variáveis utilizadas `[holmes] -> host, token, [id_usuario]`"""
        dclick.logger.debug(f"Assumindo tarefa({self.id}) no Holmes")
        id_usuario = id_usuario or bot.config.holmes.id_usuario
        (
            client_singleton()
            .put(url = f"/v1/tasks/{self.id}/assign",
                 json = { "user_id": id_usuario })
            .esperar_sucesso(f"Falha ao assumir tarefa({self.id}) no Holmes")
        )
        self.assignee_id = id_usuario
        return self

    def TomarAcao (self, acao: str, *,
                         propriedades: list[dict[Literal["id", "value", "text"], str]] | None = None) -> "Tarefa":
        """Tomar `ação` na tarefa
        - `acao` pode ser o `id` ou o `name`
        - `propriedades` caso seja necessário informar algum adicional (motivo de pendência)
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Tomando ação({acao}) na tarefa({self.id}) no Holmes")

        action = self.obter_acao(lambda a: acao == a.id or acao.lower() in a.name.lower())
        assert action is not None, f"Ação {acao!r} não encontrada na tarefa({self.id})"

        (
            client_singleton()
            .post(
                url = f"/v1/tasks/{self.id}/action",
                json = {
                    "task": { 
                        "action_id": action.id,
                        "confirm_action": True,
                        "property_values": propriedades or []
                    }
            })
            .esperar_status_code(200, f"Falha ao tomar ação na tarefa({self.id}) no Holmes")
        )
        return self.Consultar(self.id)

    def ItensTabela (self, id_ou_name: str, *,
                           page: int = 1,
                           per_page: int = 100) -> list[modelos.TableItem]:
        """Consultar itens da tabela pelo `id` ou `name` na tarefa `self.id`
        - `page, per_page` realizar a paginação. Default: Primeiros 100
        - Variáveis utilizadas `[holmes] -> host, token`"""
        dclick.logger.debug(f"Consultando itens da tabela({id_ou_name}) da tarefa({self.id}) no Holmes")

        tabela = self.obter_tabela(
            lambda t: id_ou_name == t.id
                      or id_ou_name.lower() in t.name.lower())
        assert tabela is not None, f"Tabela {id_ou_name!r} não encontrada na tarefa({self.id})"

        items = (
            client_singleton()
            .get(url = f"/v1/tasks/{self.id}/tables/{tabela.id}/table_items",
                 query = { "page": page, "per_page": per_page })
            .esperar_status_code(200, f"Falha ao consultar itens da tabela({id_ou_name}) da tarefa({self.id}) no Holmes")
            .json(esperar=dict[str, Any])
            .get("items", [])
        )
        return modelos.TableItem.UnmarshalMany(items)

__all__ = [
    "Tarefa",
    "Processo",
    "Documento",
]