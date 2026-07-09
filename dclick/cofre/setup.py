# std
import typing, certifi, functools
# interno
import dclick
from dclick.cofre import modelos
# externo
import bot
from bot.formatos import Unmarshaller
from bot.estruturas import DictNormalizado

@functools.cache
def client_singleton () -> dclick.http.ClienteHttp:
    """Criar o http `Client` configurado com o `host`, `token` e timeout
    - O Client ficará aberto após a primeira chamada na função devido ao `@cache`"""
    host, apikey = bot.config.cofre.obter("host", "apikey")
    return dclick.http.ClienteHttp(
        base_url = host,
        headers  = {
            "x-api-key": apikey,
            "x-real-ip": bot.config.cofre.obter_ou("x-real-ip", default="")
        },
        timeout  = 120,
        verify   = certifi.where(),
        follow_redirects = True,
    )

@bot.erro.adicionar_prefixo(lambda args, _: f"Falha ao consultar segredo({args[0]}) no Cofre")
def consultar_segredo[T: Unmarshaller | DictNormalizado | dict] (nome: str, *, fields: type[T] = DictNormalizado[str]) -> modelos.Segredo[T]:
    """Consultar o segredo `nome` e retornar uma classe modelo de resposta

    - Por padrão o campo `fields` é uma classe no estilo `dict`
    ```python
    segredo = dclick.cofre.consultar_segredo("EMAIL_CREDENTIALS")
    username: str | None = segredo.fields.get("username", default=None)
    ```

    - Utilizar `fields` com uma classe anotada para validar os campos esperados
    ```python
    from bot.formatos import Unmarshaller

    class Fields (Unmarshaller):
        username: str
        password: str

    segredo = dclick.cofre.consultar_segredo("EMAIL_CREDENTIALS", fields=Fields)
    print(segredo.fields.username, segredo.fields.password)
    ```

    - Variáveis utilizadas `[cofre] -> host, apikey, [x-real-ip: ""]`
        - `x-real-ip`: opcional `<IP da máquina>`, mas importante para a auditoria"""
    dclick.logger.debug(f"Consultando segredo({nome}) no Cofre")

    _segredo = (
        client_singleton()
        .get(f"/api/vault/get/{nome}")
        .esperar_status_code(200)
        .esperar_tipo_conteudo("json")
        .unmarshal(modelos._Segredo)
    )
    segredo = modelos.Segredo[T]()
    segredo.__dict__ = _segredo.as_dict()

    try:
        if issubclass(fields, Unmarshaller):
            segredo.fields = fields.Unmarshal(_segredo.fields)
            return segredo

        mapping = (dict, DictNormalizado)
        origin = typing.get_origin(fields)
        if fields in mapping or origin in mapping:
            return segredo

        raise AssertionError(f"fields inesperado: {fields}")

    except Exception as erro:
        # dclick.erros.api.RespostaJson.erro(erro) TODO
        raise

__all__ = [
    "consultar_segredo"
]