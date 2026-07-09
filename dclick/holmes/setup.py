# std
from typing import Literal
import base64, certifi, mimetypes, functools
# interno
import dclick
from dclick.holmes import modelos
# externo
import bot

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

@bot.erro.adicionar_prefixo(lambda args, _: f"Falha ao consultar a tarefa({args[0]}) no Holmes")
def consultar_tarefa (id_tarefa: str) -> modelos.Tarefa:
    """Consultar a tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.debug(f"Consultando tarefa({id_tarefa}) no Holmes")
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
    dclick.logger.debug(f"Tomando ação({id_acao}) na tarefa({id_tarefa}) no Holmes")
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
        .esperar_status_code(200, f"Falha ao tomar ação na tarefa({id_tarefa}) no Holmes")
    )

def assumir_tarefa (id_tarefa: str) -> None:
    """Assumir a tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> host, token, id_usuario`"""
    dclick.logger.debug(f"Assumindo tarefa({id_tarefa}) no Holmes")
    (
        client_singleton()
        .put(
            url = f"/v1/tasks/{id_tarefa}/assign",
            json = {
                "user_id": bot.config.holmes.id_usuario
            }
        )
        .esperar_sucesso(f"Falha ao assumir tarefa({id_tarefa}) no Holmes")
    )

def consultar_documento_tarefa (id_tarefa: str, id_documento: str) -> modelos.Documento:
    """Consultar o documento `id_documento` da tarefa `id_tarefa`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.debug(f"Consultando documento({id_documento}) da tarefa({id_tarefa}) no Holmes")
    response = (
        client_singleton()
        .get(f"/v1/tasks/{id_tarefa}/documents/{id_documento}")
        .esperar_status_code(200, f"Falha ao consultar documento da tarefa({id_tarefa}) no Holmes")
    )
    return modelos.Documento(response.conteudo, response.headers_dict)

def anexar_documento_tarefa (id_tarefa: str,
                             id_documento: str,
                             documento: tuple[str, bytes],
                             mime_type: str | None = None) -> None:
    """Realizar upload do documento `id_documento` na tarefa `id_tarefa`
    - `documento` sendo o `(nome_extensão, conteúdo)`
    - `mime_type` para informar manualmente o tipo do conteúdo
    - `mime_type=None` feito o advinho do tipo com base na extensão com fallback para `application/octet-stream`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.debug(f"Anexando documento id({id_documento}) nome({documento[0]}) na tarefa({id_tarefa}) no Holmes")
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
    dclick.logger.debug(f"Consultando processo({id_processo}) no Holmes")
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
    dclick.logger.debug(f"Consultando detalhes do processo({id_processo}) no Holmes")
    json = (
        client_singleton()
        .get(f"/v1/processes/{id_processo}/details")
        .esperar_status_code(200)
        .json(esperar=dict)
    )
    body = json.get("instance", {})
    return modelos.DetalhesProcesso.Unmarshal(body)

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
    dclick.logger.debug(f"Consultando itens da tabela({id_tabela}) da tarefa({id_tarefa}) no Holmes")
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
    dclick.logger.debug(f"Consultando documento({id_documento}) no Holmes")
    response = (
        client_singleton()
        .get(f"/v1/documents/{id_documento}/download")
        .esperar_status_code(200, f"Falha ao consultar documento({id_documento}) no Holmes")
    )
    return modelos.Documento(response.content, response.headers_dict)

def consultar_classificacao_documento (id_documento: str) -> modelos.ClassificacaoDocumento:
    """Consultar a classificação do documento `id_documento`
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.debug(f"Consultando classificação do documento({id_documento}) no Holmes")
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

def remover_documento (id_documento: str, descricao: str | None = None) -> None:
    """Remover o documento `id_documento`
    - `descricao` para informar o motivo da remoção
    - Variáveis utilizadas `[holmes] -> host, token`"""
    dclick.logger.debug(f"Removendo documento({id_documento}) no Holmes")
    (
        client_singleton()
        .delete(
            url = f"/v1/documents/{id_documento}",
            query = { "description": descricao } if descricao else None
        )
        .esperar_status_code(204, f"Falha ao remover documento({id_documento}) no Holmes")
    )

__all__ = [
    "assumir_tarefa",
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