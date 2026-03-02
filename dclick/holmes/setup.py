# std
import base64, certifi, mimetypes, functools
from typing import Callable, Generator, Literal, Self
# interno
import dclick
from dclick.holmes import modelos
# externo
import bot

@functools.cache
def client_singleton () -> dclick.http.ClienteHttp:
    """Criar o http `Client` configurado com o `host`, `token` e timeout
    - O Client ficará aberto após a primeira chamada na função devido ao `@cache`"""
    host, token = bot.configfile.obter_opcoes_obrigatorias("holmes", "host", "token")
    return dclick.http.ClienteHttp(
        base_url = host,
        headers  = { "api_token": token },
        timeout  = 120,
        verify   = certifi.where(),
    )

class QueryTaskV2:
    """Classe para realizar a construção da Query das tasks e iteração sobre os resultados obtidos
    - Versão `v2` do `/search`
    - Variáveis utilizadas `[holmes] -> host, token`
    - Variáveis dinâmicas para aplicação dos termos conforme seção `[holmes.QueryTaskV2.termos]`
        - `{ "field": "nome_opção", "type": "is", "value": "valor_opção"` }"""

    _from: int = 0
    size: int = 50
    sort: str = "due_date"
    order: Literal["asc", "desc"] = "asc"
    terms: list[dict[str, str]]

    def __init__ (self) -> None:
        dclick.logger.informar("Iniciando a QueryTask para buscar tarefas no Holmes")
        secao = "holmes.QueryTaskV2.termos"
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

    @bot.erro.adicionar_prefixo("Falha ao consultar tarefas no Holmes")
    def consultar (self) -> modelos.RaizQueryTaskV2:
        """Realizar a consulta da query conforme `query_body`"""
        raiz = (
            client_singleton()
            .post("/v2/search", json=self.query_body)
            .esperar_sucesso()
            .unmarshal(modelos.RaizQueryTaskV2)
        )

        dclick.logger.debug(f"Consulta da Query resultou em '{len(raiz.docs)}' tarefa(s) de um total de '{raiz.total}'")
        return raiz

    def paginar_query (
            self,
            filtro: Callable[[modelos.DocQueryTaskV2], bot.tipagem.SupportsBool] | None = None,
            limite = 50,
        ) -> Generator[modelos.DocQueryTaskV2, None, None]:
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
                except Exception: pass

            # não há mais páginação
            if quantidade < self.size: break

    def paginar_tarefas_query (
            self,
            filtro: Callable[[modelos.Tarefa], bot.tipagem.SupportsBool] | None = None,
            limite = 50,
        ) -> Generator[modelos.Tarefa, None, None]:
        """Realizar a consulta das tarefas da query com paginação até a quantidade `limite`
        - `filtro` para obter apenas tarefas que satisfaçam a condição informada"""
        tarefa = modelos.Tarefa()
        def filtro_query (doc: modelos.DocQueryTaskV2) -> bool:
            nonlocal tarefa, filtro
            tarefa = consultar_tarefa(doc.id)
            try: return bool(filtro(tarefa) if filtro else True)
            except Exception: return False

        for _ in self.paginar_query(filtro_query, limite):
            yield tarefa

class QueryDocumentV2:
    """Classe para realizar a construção da Query dos documents e iteração sobre os resultados obtidos
    - Versão `v2` do `/search`
    - Variáveis utilizadas `[holmes] -> host, token`
    - Variáveis dinâmicas para aplicação dos termos conforme seção `[holmes.QueryDocumentV2.termos]`
        - `{ "field": "nome_opção", "type": "is", "value": "valor_opção"` }"""

    _from: int = 0
    size: int = 50
    sort: str = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    terms: list[dict[str, str]]

    def __init__ (self) -> None:
        dclick.logger.informar("Iniciando a QueryDocument para buscar por documentos no Holmes")
        secao = "holmes.QueryDocumentV2.termos"
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
                "context": "document",
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

    @bot.erro.adicionar_prefixo("Falha ao consultar documentos no Holmes")
    def consultar (self) -> modelos.RaizQueryDocumentV2:
        """Realizar a consulta da query conforme `query_body`"""
        raiz = (
            client_singleton()
            .post("/v2/search", json=self.query_body)
            .esperar_sucesso()
            .unmarshal(modelos.RaizQueryDocumentV2)
        )

        dclick.logger.debug(f"Consulta da Query resultou em '{len(raiz.docs)}' documento(s) de um total de '{raiz.total}'")
        return raiz

    def paginar_query (
            self,
            filtro: Callable[[modelos.DocQueryDocumentV2], bot.tipagem.SupportsBool] | None = None,
            limite = 50,
        ) -> Generator[modelos.DocQueryDocumentV2, None, None]:
        """Realizar a consulta da query com paginação até a quantidade `limite`
        - `filtro` para obter apenas documentos que satisfaçam a condição informada"""
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
                except Exception: pass

            # não há mais páginação
            if quantidade < self.size: break

    def paginar_documentos_query (
            self,
            filtro: Callable[[modelos.DocQueryDocumentV2], bot.tipagem.SupportsBool] | None = None,
            limite = 50,
        ) -> Generator[modelos.Documento, None, None]:
        """Realizar a consulta dos documentos da query com paginação até a quantidade `limite`
        - `filtro` para obter apenas documentos que satisfaçam a condição informada"""
        for doc in self.paginar_query(filtro, limite):
            yield consultar_documento(doc.document_id)

@bot.erro.adicionar_prefixo(lambda args, _: f"Falha ao consultar a tarefa({args[0]}) no Holmes")
def consultar_tarefa (id_tarefa: str) -> modelos.Tarefa:
    """Consultar a tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Consultando tarefa({id_tarefa}) no Holmes")
    return (
        client_singleton()
        .get(f"/v1/tasks/{id_tarefa}")
        .esperar_sucesso()
        .unmarshal(modelos.Tarefa)
    )

def tomar_acao_tarefa (
        id_tarefa: str,
        id_acao: str,
        propriedades: list[dict[Literal["id", "value", "text"], str]] | None = None
    ) -> None:
    """Tomar `acao` na `tarefa`
    - `propriedades` caso seja necessário informar algum adicional (motivo de pendência)
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Tomando ação({id_acao}) na tarefa({id_tarefa}) no Holmes")
    (
        client_singleton()
        .post(
            url = f"/v1/tasks/{id_tarefa}/action",
            json = {
                "task": { 
                    "action_id": id_acao,
                    "confirm_action": True,
                    "property_values": propriedades or []
                }
        })
        .esperar_status_code(200, f"Falha ao ação na tarefa({id_tarefa}) no Holmes")
    )

def assumir_tarefa (id_tarefa: str) -> None:
    """Assumir a tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> host, token, id_usuario`"""
    dclick.logger.informar(f"Assumindo tarefa({id_tarefa}) no Holmes")
    usuario = bot.configfile.obter_opcoes_obrigatorias("holmes", "id_usuario")[0]
    (
        client_singleton()
        .put(
            url = f"/v1/tasks/{id_tarefa}/assign",
            json = { "user_id": usuario }
        )
        .esperar_status_code(200, f"Falha ao assumir tarefa({id_tarefa}) no Holmes")
    )

def consultar_documento_tarefa (id_tarefa: str, id_documento: str) -> modelos.Documento:
    """Consultar o documento `id_documento` da tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Consultando documento({id_documento}) da tarefa({id_tarefa}) no Holmes")
    response = (
        client_singleton()
        .get(f"/v1/tasks/{id_tarefa}/documents/{id_documento}")
        .esperar_status_code(200, f"Falha ao consultar documento da tarefa({id_tarefa}) no Holmes")
    )
    return modelos.Documento(response.conteudo, dict(response.headers))

def anexar_documento_tarefa (id_tarefa: str,
                             id_documento: str,
                             documento: tuple[str, bytes],
                             mime_type: str | None = None) -> None:
    """Realizar upload do documento `id_documento` na tarefa `id_tarefa`
    - `documento` sendo o `(nome_extensão, conteúdo)`
    - `mime_type` para informar manualmente o tipo do conteúdo
    - `mime_type=None` feito o advinho do tipo com base na extensão com fallback para `application/octet-stream`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Anexando documento id({id_documento}) nome({documento[0]}) na tarefa({id_tarefa}) no Holmes")
    nome_extensao, conteudo = documento
    mime = (mime_type or mimetypes.guess_type(nome_extensao)[0]) or "application/octet-stream"
    (
        client_singleton()
        .post(
            url = f"/v1/tasks/{id_tarefa}/documents/{id_documento}",
            arquivos = { "file": (nome_extensao, conteudo, mime) }
        )
        .esperar_status_code(204, f"Falha ao anexar documento na tarefa({id_tarefa}) do Holmes")
    )

@bot.erro.adicionar_prefixo(lambda args, _: f"Falha ao consultar o processo({args[0]}) no Holmes")
def consultar_processo (id_processo: str) -> modelos.Processo:
    """Consultar o processo `id_processo`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Consultando processo({id_processo}) no Holmes")
    return (
        client_singleton()
        .get(f"/v1/processes/{id_processo}")
        .esperar_status_code(200)
        .unmarshal(modelos.Processo)
    )

@bot.erro.adicionar_prefixo(lambda args, _: f"Falha ao consultar detalhes do processo({args[0]}) no Holmes")
def consultar_detalhes_processo (id_processo: str) -> modelos.DetalhesProcesso:
    """Consultar os detalhes do processo `id_processo`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Consultando detalhes do processo({id_processo}) no Holmes")
    json = (
        client_singleton()
        .get(f"/v1/processes/{id_processo}/details")
        .esperar_status_code(200)
        .json()
    )
    body = json.get("instance", {}) if isinstance(json, dict) else {}
    body["property_values"] = [body["property_values"].pop(0)]
    return bot.formatos.Unmarshaller(modelos.DetalhesProcesso).parse(body)

@bot.erro.adicionar_prefixo(lambda args, _: f"Falha ao consultar itens de tabela da tarefa({args[0]}) no Holmes")
def consultar_itens_tabela_tarefa (
        id_tarefa: str,
        id_tabela: str,
        page: int = 1,
        per_page: int = 100
    ) -> modelos.ItensTabelaTarefa:
    """Consultar itens da tabela `id_tabela` da tarefa `id_tarefa`
    - `page, per_page` realizar a paginação. Default: Primeiros 100
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Consultando itens da tabela({id_tabela}) da tarefa({id_tarefa}) no Holmes")
    return (
        client_singleton()
        .get(
            url = f"/v1/tasks/{id_tarefa}/tables/{id_tabela}/table_items",
            query = { "page": page, "per_page": per_page }
        )
        .esperar_status_code(200)
        .unmarshal(modelos.ItensTabelaTarefa)
    )

def consultar_documento (id_documento: str) -> modelos.Documento:
    """Consultar o documento `id_documento`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Consultando documento({id_documento}) no Holmes")
    response = (
        client_singleton()
        .get(f"/v1/documents/{id_documento}/download")
        .esperar_status_code(200, f"Falha ao consultar documento({id_documento}) no Holmes")
    )
    return modelos.Documento(response.content, dict(response.headers))

def consultar_classificacao_documento (id_documento: str) -> modelos.ClassificacaoDocumento:
    """Consultar a classificação do documento `id_documento`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Consultando classificação do documento({id_documento}) no Holmes")
    return (
        client_singleton()
        .get(f"/v1/documents/{id_documento}/classify")
        .esperar_status_code(200)
        .unmarshal(modelos.ClassificacaoDocumento)
    )

def upload_documento (
        nome_extensao: str,
        conteudo: str | bytes,
        classificacao: modelos.ClassificacaoDocumentoDict | None = None
    ) -> modelos.UploadDocumento:
    """Realizar o upload do documento `nome_extensao` via `base64`
    - `conteudo=bytes` transformado para `base64`
    - `conteudo=str` esperado como `base64`
    - `classificacao` aplicar classificação no documento
        - `{ "nature_id": "60f862d9f5a395000da95cf2", "property_values": [] }`
        - `{ "nature_id": "60f862d9f5a395000da95cf2", "property_values": [{ "id": "cnpj", "value": "03095314000618" }] }`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Realizando upload de documento({nome_extensao}) no Holmes")
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

def remover_documento (id_documento: str, descricao: str | None = None) -> None:
    """Remover o documento `id_documento`
    - `descricao` para informar o motivo da remoção
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.informar(f"Removendo documento({id_documento}) no Holmes")
    (
        client_singleton()
        .delete(
            url = f"/v1/documents/{id_documento}",
            query = { "description": descricao } if descricao else None
        )
        .esperar_status_code(204, f"Falha ao remover documento({id_documento}) no Holmes")
    )

__all__ = [
    "QueryTaskV2",
    "assumir_tarefa",
    "QueryDocumentV2",
    "consultar_tarefa",
    "upload_documento",
    "remover_documento",
    "tomar_acao_tarefa",
    "consultar_processo",
    "consultar_documento",
    "anexar_documento_tarefa",
    "consultar_documento_tarefa",
    "consultar_detalhes_processo",
    "consultar_itens_tabela_tarefa",
    "consultar_classificacao_documento",
]