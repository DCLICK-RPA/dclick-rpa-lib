# std
import certifi, mimetypes
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
        verify   = certifi.where(),
    )

class QueryTaskV2:
    """Classe para realizar a construção da Query das tasks e iteração sobre os resultados obtidos
    - Versão `v2` do `/search`
    - Variáveis utilizadas `[holmes] -> "host", "token"`
    - Variáveis dinâmicas para aplicação dos termos conforme seção `[holmes.QueryTaskV2.termos]`
        - `{ "field": "nome_opção", "type": "is", "value": "valor_opção"` }"""

    _from: int = 0
    size: int = 50
    sort: str = "due_date"
    order: Literal["asc", "desc"] = "asc"
    terms: list[dict[str, str]]

    def __init__ (self) -> None:
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

    @bot.util.decoradores.prefixar_erro("Falha ao consultar tarefas no Holmes")
    def consultar (self) -> modelos.RaizQueryTaskV2:
        """Realizar a consulta da query conforme `query_body`"""
        bot.logger.informar("Procurando por tarefas no Holmes")

        response = client_singleton().post("/v2/search", json=self.query_body)
        assert response.is_success, f"O status code '{response.status_code}' foi diferente do esperado"
        raiz = bot.formatos.Unmarshaller(modelos.RaizQueryTaskV2)\
                           .parse(response.json())

        bot.logger.informar(f"Consulta resultou em '{len(raiz.docs)}' tarefa(s) de um total de '{raiz.total}'")
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
    - Variáveis utilizadas `[holmes] -> "host", "token"`
    - Variáveis dinâmicas para aplicação dos termos conforme seção `[holmes.QueryDocumentV2.termos]`
        - `{ "field": "nome_opção", "type": "is", "value": "valor_opção"` }"""

    _from: int = 0
    size: int = 50
    sort: str = "updated_at"
    order: Literal["asc", "desc"] = "desc"
    terms: list[dict[str, str]]

    def __init__ (self) -> None:
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

    @bot.util.decoradores.prefixar_erro("Falha ao consultar documentos no Holmes")
    def consultar (self) -> modelos.RaizQueryDocumentV2:
        """Realizar a consulta da query conforme `query_body`"""
        bot.logger.informar("Procurando por documentos no Holmes")

        response = client_singleton().post("/v2/search", json=self.query_body)
        assert response.is_success, f"O status code '{response.status_code}' foi diferente do esperado"
        raiz = bot.formatos.Unmarshaller(modelos.RaizQueryDocumentV2)\
                           .parse(response.json())

        bot.logger.informar(f"Consulta resultou em '{len(raiz.docs)}' documento(s) de um total de '{raiz.total}'")
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

@bot.util.decoradores.prefixar_erro(lambda args, _: f"Falha ao consultar a tarefa({args[0]}) no Holmes")
def consultar_tarefa (id_tarefa: str) -> modelos.Tarefa:
    """Consultar a tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando tarefa({id_tarefa}) no Holmes")

    response = client_singleton().get(f"/v1/tasks/{id_tarefa}")
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"
    tarefa = bot.formatos.Unmarshaller(modelos.Tarefa)\
                         .parse(response.json())

    return tarefa

def consultar_documento_tarefa (id_tarefa: str, id_documento: str) -> modelos.Documento:
    """Consultar o documento `id_documento` da tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando documento({id_documento}) da tarefa({id_tarefa}) no Holmes")

    response = client_singleton().get(f"/v1/tasks/{id_tarefa}/documents/{id_documento}")
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"

    return modelos.Documento(response.content, dict(response.headers))

def consultar_documento (id_documento: str) -> modelos.Documento:
    """Consultar o documento `id_documento`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando documento({id_documento}) no Holmes")

    response = client_singleton().get(f"/v1/documents/{id_documento}/download")
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"

    return modelos.Documento(response.content, dict(response.headers))

@bot.util.decoradores.prefixar_erro(lambda args, _: f"Falha ao consultar o processo({args[0]}) no Holmes")
def consultar_processo (id_processo: str) -> modelos.Processo:
    """Consultar o processo `id_processo`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando processo({id_processo}) no Holmes")

    response = client_singleton().get(f"/v1/processes/{id_processo}")
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"
    return bot.formatos.Unmarshaller(modelos.Processo)\
                       .parse(response.json())

@bot.util.decoradores.prefixar_erro(lambda args, _: f"Falha ao consultar detalhes do processo({args[0]}) no Holmes")
def consultar_detalhes_processo (id_processo: str) -> modelos.DetalhesProcesso:
    """Consultar os detalhes do processo `id_processo`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Consultando detalhes do processo({id_processo}) no Holmes")

    response = client_singleton().get(f"/v1/processes/{id_processo}/details")
    assert response.status_code == 200, f"O status code '{response.status_code}' foi diferente do esperado"

    body = response.json()
    body = body.get("instance", {}) if isinstance(body, dict) else {}
    body["property_values"] = [body["property_values"].pop(0)]
    return bot.formatos.Unmarshaller(modelos.DetalhesProcesso)\
                       .parse(body)

@bot.util.decoradores.prefixar_erro(lambda args, _: f"Falha ao consultar itens de tabela da tarefa({args[0]}) no Holmes")
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
    return bot.formatos.Unmarshaller(modelos.ItensTabelaTarefa)\
                       .parse(response.json())

def tomar_acao_tarefa (
        id_tarefa: str,
        id_acao: str,
        propriedades: list[dict[Literal["id", "value", "text"], str]] | None = None
    ) -> None:
    """Tomar `acao` na `tarefa`
    - `propriedades` caso seja necessário informar algum adicional (motivo de pendência)
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Tomando ação({id_acao}) na tarefa({id_tarefa}) do Holmes")

    response = client_singleton().post(
        f"/v1/tasks/{id_tarefa}/action",
        json = {
            "task": { 
                "action_id": id_acao,
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

def anexar_documento_tarefa (id_tarefa: str,
                             id_documento: str,
                             documento: tuple[str, bytes],
                             mime_type: str | None = None) -> None:
    """Realizar upload do documento `id_documento` na tarefa `id_tarefa`
    - `documento` sendo o `(nome_extensão, conteúdo)`
    - `mime_type` para informar manualmente o tipo do conteúdo
    - `mime_type=None` feito o advinho do tipo com base na extensão com fallback para `application/octet-stream`
    - Variáveis utilizadas `[holmes] -> "host", "token"`"""
    bot.logger.informar(f"Anexando documento id({id_documento}) nome({documento[0]}) na tarefa({id_tarefa}) no Holmes")

    nome_extensao, conteudo = documento
    mime = mime_type or mimetypes.guess_type(nome_extensao)[0]
    response = client_singleton().post(
        f"/v1/tasks/{id_tarefa}/documents/{id_documento}",
        files = {
            "file": (nome_extensao, conteudo, mime or "application/octet-stream")
        }
    )
    assert response.status_code == 204, f"O status code '{response.status_code}' foi diferente do esperado"

__all__ = [
    "QueryTaskV2",
    "assumir_tarefa",
    "QueryDocumentV2",
    "consultar_tarefa",
    "tomar_acao_tarefa",
    "consultar_processo",
    "consultar_documento",
    "anexar_documento_tarefa",
    "consultar_documento_tarefa",
    "consultar_detalhes_processo",
    "consultar_itens_tabela_tarefa",
]