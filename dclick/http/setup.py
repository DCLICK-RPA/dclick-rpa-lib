# std
import typing
# externo
import httpx
import httpx._types as types
from httpx._client import USE_CLIENT_DEFAULT, UseClientDefault
from bot.estruturas import DictNormalizado
from bot.formatos import ElementoXML, Unmarshaller, validar

type METODOS_HTTP = typing.Literal["HEAD", "OPTIONS", "GET", "POST", "PUT", "PATCH", "DELETE"]

class ResponseHttp (httpx.Response):
    """Response extensão do `httpx.Response` com métodos para facilitar validação de uma resposta http"""

    @classmethod
    def New (cls, response: httpx.Response) -> typing.Self:
        obj = super().__new__(cls)
        obj.__dict__ = response.__dict__

        try: setattr(obj, "_headers", response.headers)
        except Exception: pass

        return obj

    @property
    def headers_dict (self) -> dict[str, str]:
        """Headers com chaves normalizadas
        - `Chaves` dos headers em `lower` e feito `strip()`
        - `Valores` dos headers transformados em `str`
        - Caso existam múltiplos headers de mesmo nome, os valores serão concatenados por `,`"""
        return {
            str(key).lower().strip(): str(value)
            for key, value in dict(getattr(self, "_headers", {})).items()
        }

    @property
    def headers (self) -> DictNormalizado[str]:
        """Headers com chaves normalizadas
        - Caso existam múltiplos headers de mesmo nome, os valores serão concatenados por `,`"""
        return DictNormalizado(self.headers_dict)

    def esperar_sucesso (self, mensagem: str | None = None) -> typing.Self:
        """Fazer o `assert` se o `response.status_code` de retorno é `2xx`
        - `mensagem` sobrescreve a mensagem utilizada como erro"""
        if self.is_success:
            return self

        msg_status = f"Status code de Resposta HTTP '{self.status_code}' não é de sucesso"
        if mensagem:
            erro = AssertionError(mensagem)
            erro.add_note(msg_status)
        else: erro = AssertionError(msg_status)

        # Erros.RetornoInesperado.erro(erro) TODO
        raise erro

    def esperar_status_code (self, status: int, mensagem: str | None = None) -> typing.Self:
        """Fazer o `assert` se `response.status_code == status`
        - `mensagem` sobrescreve a mensagem utilizada como erro"""
        if self.status_code == status:
            return self

        msg_status = f"Status code de Resposta HTTP '{self.status_code}' diferente do esperado '{status}'"
        if mensagem:
            erro = AssertionError(mensagem)
            erro.add_note(msg_status)
        else: erro = AssertionError(msg_status)

        # Erros.RetornoInesperado.erro(erro) TODO
        raise erro

    def esperar_tipo_conteudo (self, tipo: str, mensagem: str | None = None) -> typing.Self:
        """Fazer o `assert` se `tipo` está no `Header: Content-Type`
        - `mensagem` sobrescreve a mensagem utilizada como erro"""
        content_type = self.headers.get("Content-Type", "").lower()
        if tipo.lower() in content_type:
            return self

        msg_conteudo = f"Content-Type de Resposta HTTP '{content_type}' diferente do esperado '{tipo}'"
        if mensagem:
            erro = AssertionError(mensagem)
            erro.add_note(msg_conteudo)
        else: erro = AssertionError(msg_conteudo)

        # Erros.RetornoInesperado.erro(erro) TODO
        raise erro

    @property
    def conteudo (self) -> bytes:
        """Ler todo o conteúdo do corpo como `bytes`"""
        return self.content

    @property
    def texto (self) -> str:
        """Ler todo o conteúdo do corpo e decodificar para `str`"""
        return self.text

    def xml (self) -> ElementoXML:
        """Realizar o parse do conteúdo de resposta como um `ElementoXML`
        - `ValueError` caso ocorra erro de parse"""
        try: return ElementoXML.Parse(self.texto)
        except Exception as erro:
            # Erros.RetornoInesperado.erro(erro) TODO
            raise ValueError("Erro ao realizar o parse para XML da Resposta HTTP") from erro

    @typing.overload
    def json (self) -> typing.Any: ... # type: ignore
    @typing.overload
    def json[T] (self, esperar: type[T]) -> T: ... # type: ignore
    @typing.override
    def json[T] (self, esperar: type[T] = typing.Any) -> T | typing.Any: # type: ignore
        """Realizar o parse do conteúdo de resposta como o tipo `esperar`
        - `esperar`: `dict[str, str | int]`, `list[dict[str, str]]`
        - `ValueError` caso ocorra erro de parse"""
        try: json = super().json()
        except Exception as erro:
            # Erros.RetornoInesperado.erro(erro) TODO
            raise ValueError("Erro ao realizar o parse para JSON da Resposta HTTP") from erro

        if validar(json, esperar):
            return json

        # Erros.RespostaJson.erro(erro) TODO
        raise ValueError(f"Erro ao realizar a validação do JSON da Resposta HTTP para o tipo esperado '{esperar}'")

    def unmarshal[T: Unmarshaller] (self, cls: type[T]) -> T:
        """Realizar o Unmarshal do conteúdo `json` conforme a classe anotada `cls`
        - Resposta deve ser um json `dict`
        - `ValueError`

        ### Exemplo
        ```
        from bot.http import request
        from bot.formatos import Unmarshaller

        class Dimensions (Unmarshaller):
            width: float
            height: float
            depth: float
        class Product (Unmarshaller):
            id: int
            title: str
            category: str
            price: float
            tags: list[str]
            dimensions: Dimensions

        produto = request("GET", "https://dummyjson.com/products/1").unmarshal(Product)
        print(produto.id)
        print(produto.stringify(indent=True))
        ```
        """
        json = self.json()
        try: return cls.Unmarshal(json)
        except Exception as erro:
            # Erros.RespostaJson.erro(erro) TODO
            raise ValueError(f"Erro ao realizar o Unmarshal da Resposta HTTP para '{cls}'") from erro

    def unmarshal_many[T: Unmarshaller] (self, cls: type[T]) -> list[T]:
        """Realizar o Unmarshal do conteúdo `json` conforme a classe anotada `cls`
        - Resposta deve ser um json `list[dict]`
        - `ValueError`"""
        json = self.json()
        try: return cls.UnmarshalMany(json)
        except Exception as erro:
            # Erros.RespostaJson.erro(erro) TODO
            raise ValueError(f"Erro ao realizar o Unmarshal da Resposta HTTP para '{cls}'") from erro

class ClienteHttp (httpx.Client):
    """Criar um cliente `HTTP` para realizar requests. Extensão do `httpx.Client`
    - Realizado logs automáticos de erros de api para requests e responses com os métodos modificados
    - Veja a documentação do `request()` para informação sobre todos os parâmetros aceitos
    - Retorno dos métodos `request, get, post, put, ...` é um `ResponseHttp` com métodos adicionais ao `httpx.Response`"""

    @typing.override
    def request (self, metodo: METODOS_HTTP, # type: ignore
                       url: str,
                       query: types.QueryParamTypes | None = None,
                       headers: types.HeaderTypes | None = None,
                       *,
                       json: object | None = None,
                       conteudo: types.RequestContent | None = None,
                       dados: types.RequestData | None = None,
                       arquivos: types.RequestFiles | None = None,
                       follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
                       timeout: types.TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT) -> ResponseHttp:
        """Realizar um request informando o `método` desejado
        - `metodo` Método HTTP a ser utilizado: `HEAD, OPTIONS, GET, POST, PUT, PATCH, DELETE`
        - `url` URL de destino da requisição
            ```
            ClienteHttp().request("GET", "https://httpbin.org/get")
            ClienteHttp(base_url="https://httpbin.org").request("GET", "/get")
            ```
        - `query` Parâmetros de query adicionados à URL
            ```
            client.request("GET", "https://httpbin.org/get", query={ "page": 1, "limit": 10 })
            equivalente à "https://httpbin.org/get?page=1&limit=10"
            ```
        - `headers` Cabeçalhos HTTP enviados na requisição
            ```
            client.request(
                "GET", "https://httpbin.org/get",
                headers={ "Authorization": "Bearer TOKEN_AQUI", "X-Request-ID": "123" }
            )
            ```
        - `json` Objeto a ser serializado e enviado como JSON no corpo da requisição como `application/json`
        - `dados` Dados enviados como formulário `application/x-www-form-urlencoded`
            ```
            client.request(
                "POST", "https://api.exemplo.com/login",
                dados={ "username": "xpto", "password": "123" }
            )
            ```
        - `arquivos` Arquivos enviados como `multipart/form-data`
            ```
            client.request(
                "POST", "https://api.exemplo.com",
                arquivos = {
                    "file1": open("arquivo.txt").read(),
                    # (Nome arquivo, Bytes ou Stream, MIME Type)
                    "file2": ("foto.jpg", open("foto.jpg").read(), "image/jpeg")
                }
            )
            ```
        - `conteudo` Conteúdo bruto (bytes ou string) enviado no corpo da requisição sem o `Header: Content-Type` definido
            ```
            client.request(
                "POST", "https://api.exemplo.com/xml",
                conteudo = "<user><name>Lucas</name></user>",
                headers = { "Content-Type": "application/xml" }
            )
            ```
        - `follow_redirects` Indica se a requisição deve seguir redirecionamentos automaticamente
        - `timeout` Tempo máximo de espera pela resposta (em segundos).
        - `verify` Define se o certificado SSL deve ser verificado `True/False` ou caminho para o certificado"""
        try:
            response = super().request(
                metodo, url, params=query, headers=headers,
                json=json, content=conteudo, data=dados, files=arquivos,
                follow_redirects=follow_redirects, timeout=timeout
            )

            #  TODO
            # if response.is_success: pass
            # elif response.is_server_error: Erros.Conexao.alertar()
            # elif response.status_code in (401, 403): Erros.Autenticacao.alertar()

            return ResponseHttp.New(response)

        except httpx.TimeoutException:
            # Erros.Timeout.erro() TODO
            raise
        except httpx.ConnectError:
            # Erros.Conexao.erro() TODO
            raise

    @typing.override
    def get (self, url: str, # type: ignore
                   query: types.QueryParamTypes | None = None,
                   headers: types.HeaderTypes | None = None,
                   *,
                   follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
                   timeout: types.TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT) -> ResponseHttp:
        return self.request("GET", url, query, headers, follow_redirects=follow_redirects, timeout=timeout)

    @typing.override
    def head (self, url: str, # type: ignore
                    query: types.QueryParamTypes | None = None,
                    headers: types.HeaderTypes | None = None,
                    *,
                    follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
                    timeout: types.TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT) -> ResponseHttp:
        return self.request("HEAD", url, query, headers, follow_redirects=follow_redirects, timeout=timeout)

    @typing.override
    def options (self, url: str, # type: ignore
                       query: types.QueryParamTypes | None = None,
                       headers: types.HeaderTypes | None = None,
                       *,
                       follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
                       timeout: types.TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT) -> ResponseHttp:
        return self.request("OPTIONS", url, query, headers, follow_redirects=follow_redirects, timeout=timeout)

    @typing.override
    def delete (self, url: str, # type: ignore
                      query: types.QueryParamTypes | None = None,
                      headers: types.HeaderTypes | None = None,
                      *,
                      follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
                      timeout: types.TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT) -> ResponseHttp:
        return self.request(
            "DELETE", url, query, headers, 
            follow_redirects=follow_redirects, timeout=timeout
        )

    @typing.override
    def post (self, url: str, # type: ignore
                    query: types.QueryParamTypes | None = None,
                    headers: types.HeaderTypes | None = None,
                    *,
                    json: object | None = None,
                    conteudo: types.RequestContent | None = None,
                    dados: types.RequestData | None = None,
                    arquivos: types.RequestFiles | None = None,
                    follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
                    timeout: types.TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT) -> ResponseHttp:
        return self.request(
            "POST", url, query, headers, 
            json=json, conteudo=conteudo, dados=dados, arquivos=arquivos,
            follow_redirects=follow_redirects, timeout=timeout
        )

    @typing.override
    def put (self, url: str, # type: ignore
                   query: types.QueryParamTypes | None = None,
                   headers: types.HeaderTypes | None = None,
                   *,
                   json: object | None = None,
                   conteudo: types.RequestContent | None = None,
                   dados: types.RequestData | None = None,
                   arquivos: types.RequestFiles | None = None,
                   follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
                   timeout: types.TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT) -> ResponseHttp:
        return self.request(
            "PUT", url, query, headers, 
            json=json, conteudo=conteudo, dados=dados, arquivos=arquivos,
            follow_redirects=follow_redirects, timeout=timeout
        )

    @typing.override
    def patch (self, url: str, # type: ignore
                     query: types.QueryParamTypes | None = None,
                     headers: types.HeaderTypes | None = None,
                     *,
                     json: object | None = None,
                     conteudo: types.RequestContent | None = None,
                     dados: types.RequestData | None = None,
                     arquivos: types.RequestFiles | None = None,
                     follow_redirects: bool | UseClientDefault = USE_CLIENT_DEFAULT,
                     timeout: types.TimeoutTypes | UseClientDefault = USE_CLIENT_DEFAULT) -> ResponseHttp:
        return self.request(
            "PATCH", url, query, headers, 
            json=json, conteudo=conteudo, dados=dados, arquivos=arquivos,
            follow_redirects=follow_redirects, timeout=timeout
        )

def request (metodo: METODOS_HTTP,
             url: str,
             query: types.QueryParamTypes | None = None,
             headers: types.HeaderTypes | None = None,
             *,
             json: object | None = None,
             conteudo: types.RequestContent | None = None,
             dados: types.RequestData | None = None,
             arquivos: types.RequestFiles | None = None,
             follow_redirects: bool = False,
             timeout: types.TimeoutTypes = 60,
             verify: str | bool = True) -> ResponseHttp:
    """Realizar um request informando o `método` desejado. Retorna um `ResponseHttp` com métodos adicionais ao `httpx.Response`
    - Realizado logs automáticos de erros de api para requests e responses com os métodos modificados
    - `metodo` Método HTTP a ser utilizado: `HEAD, OPTIONS, GET, POST, PUT, PATCH, DELETE`
    - `url` URL de destino da requisição: `request("GET", "https://httpbin.org/get")`
    - `query` Parâmetros de query adicionados à URL
        ```
        request("GET", "https://httpbin.org/get", query={ "page": 1, "limit": 10 })
        equivalente à "https://httpbin.org/get?page=1&limit=10"
        ```
    - `headers` Cabeçalhos HTTP enviados na requisição
        ```
        request(
            "GET", "https://httpbin.org/get",
            headers={ "Authorization": "Bearer TOKEN_AQUI", "X-Request-ID": "123" }
        )
        ```
    - `json` Objeto a ser serializado e enviado como JSON no corpo da requisição como `application/json`
    - `dados` Dados enviados como formulário `application/x-www-form-urlencoded`
        ```
        request(
            "POST", "https://api.exemplo.com/login",
            dados={ "username": "xpto", "password": "123" }
        )
        ```
    - `arquivos` Arquivos enviados como `multipart/form-data`
        ```
        request(
            "POST", "https://api.exemplo.com",
            arquivos = {
                "file1": open("arquivo.txt").read(),
                # (Nome arquivo, Bytes ou Stream, MIME Type)
                "file2": ("foto.jpg", open("foto.jpg").read(), "image/jpeg")
            }
        )
        ```
    - `conteudo` Conteúdo bruto (bytes ou string) enviado no corpo da requisição sem o `Header: Content-Type` definido
        ```
        request(
            "POST", "https://api.exemplo.com/xml",
            conteudo = "<user><name>Lucas</name></user>",
            headers = { "Content-Type": "application/xml" }
        )
        ```
    - `follow_redirects` Indica se a requisição deve seguir redirecionamentos automaticamente
    - `timeout` Tempo máximo de espera pela resposta (em segundos).
    - `verify` Define se o certificado SSL deve ser verificado `True/False` ou caminho para o certificado"""
    return (
        ClienteHttp(verify=verify,
                    timeout=timeout,
                    follow_redirects=follow_redirects
        )
        .request(
            metodo=metodo, url=url, query=query, headers=headers,
            json=json, conteudo=conteudo, dados=dados, arquivos=arquivos,
        )
    )

__all__ = [
    "request",
    "ClienteHttp",
]