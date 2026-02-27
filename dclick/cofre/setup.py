# std
import certifi
from functools import cache
# interno
import dclick
from dclick.cofre import modelos
# externo
import bot
from bot.estruturas import DictNormalizado

@cache
def client_singleton () -> bot.http.Client:
    """Criar o http `Client` configurado com o `host`, `token` e timeout
    - O Client ficará aberto após a primeira chamada na função devido ao `@cache`"""
    host, apikey = bot.configfile.obter_opcoes_obrigatorias("cofre", "host", "apikey")
    return bot.http.Client(
        base_url = host,
        headers  = {
            "x-api-key": apikey,
            "x-real-ip": bot.configfile.obter_opcao_ou("cofre", "x-real-ip", default="")
        },
        timeout  = 120,
        verify   = certifi.where(),
        follow_redirects = True,
    )

@bot.erro.adicionar_prefixo(lambda args, _: f"Falha ao consultar segredo({args[0]}) no Cofre")
def consultar_segredo[T] (nome: str, fields: type[T] = DictNormalizado[str]) -> modelos.Segredo[T]:
    """Consultar o segredo `nome` e retornar uma classe modelo de resposta

    - Por padrão o campo `fields` é uma classe no estilo `dict`
    ```python
    segredo = dclick.cofre.consultar_segredo("EMAIL_CREDENTIALS")
    username: str | None = segredo.fields.get("username", default=None)
    ```

    - Utilizar `fields` com uma classe anotada para validar os campos esperados
    ```python
    class Fields:
        username: str
        password: str
    segredo = dclick.cofre.consultar_segredo("EMAIL_CREDENTIALS", Fields)
    print(segredo.fields.username, segredo.fields.password)
    ```

    - Variáveis utilizadas `[cofre] -> host, apikey, [x-real-ip: ""]`
        - `x-real-ip`: opcional `<IP da máquina>`, mas importante para a auditoria"""
    dclick.logger.informar(f"Consultando segredo({nome}) no Cofre")

    response = client_singleton().get(f"/api/vault/get/{nome}")
    assert response.status_code == 200, f"Status code '{response.status_code}' diferente do esperado"

    segredo: modelos.Segredo = (
        bot.formatos.Unmarshaller(modelos._Segredo)
        .parse(response.json())
    ) # type: ignore
    segredo.fields = (
        fields(segredo.fields) # type: ignore
        if isinstance(fields(), (dict, DictNormalizado))
        else bot.formatos.Unmarshaller(fields).parse(segredo.fields)
    )

    return segredo

__all__ = [
    "consultar_segredo"
]