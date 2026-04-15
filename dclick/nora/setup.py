# std
from typing import Self
import certifi, functools
# interno
import dclick
from dclick.nora import modelos
# externo
import bot
from bot.estruturas.filas import Queue

@functools.cache
def client_singleton () -> dclick.http.ClienteHttp:
    """Criar o http `Client` configurado com o `host`, `token` e timeout
    - O Client ficará aberto após a primeira chamada na função devido ao `@cache`"""
    host, apikey = bot.configfile.obter_opcoes_obrigatorias("nora", "host", "apikey")
    return dclick.http.ClienteHttp(
        base_url = host,
        headers  = { "x-api-key": apikey },
        timeout  = 60,
        verify   = certifi.where(),
        follow_redirects = True,
    )

def executar_extracao (agente: str, mime_type: str, file_name: str, content: str) -> modelos.ResponseExecutar:
    """Executar uma extração para o `agente`
    - `mime_type` tipo do conteúdo no formato `mime`
    - `file_name` nome e extensão do arquivo
    - `content` conteúdo do arquivo como `base64`
    - Variáveis utilizadas `[nora] -> host, apikey`"""
    dclick.logger.informar(f"Executando uma extração no Nora", agente=agente, file_name=file_name)
    response = (
        client_singleton()
        .post(f"/agents/{agente}/execute",
            json = {
                "mimeType": mime_type,
                "fileName": file_name,
                "content": content
            }
        )
    )

    try: return (
        response
        .esperar_status_code(202)
        .esperar_tipo_conteudo("json")
        .unmarshal(modelos.ResponseExecutar)
    )
    except Exception:
        dclick.logger.erro(
            "Falha ao executar uma extração no Nora",
            agente = agente,
            file_name = file_name,
            response = response.text
        )
        raise

def acompanhar_extracao (tracking_code: str) -> modelos.ResponseAcompanhar:
    """Acompanhar uma extração via `tracking_code`
    - Variáveis utilizadas `[nora] -> host, apikey`"""
    dclick.logger.informar(f"Acompanhando uma extração no Nora", tracking_code=tracking_code)
    response = (
        client_singleton()
        .get(f"/extractions/track/{tracking_code}")
    )

    try: return (
        response
        .esperar_status_code(200)
        .esperar_tipo_conteudo("json")
        .unmarshal(modelos.ResponseAcompanhar)
    )
    except Exception:
        dclick.logger.erro(
            "Falha ao acompanhar uma extração no Nora",
            tracking_code = tracking_code,
            response = response.text
        )
        raise

def consultar_extracao (extraction_id: str) -> modelos.ResponseConsultar:
    """Consultar a extração `extraction_id`
    - Variáveis utilizadas `[nora] -> host, apikey`"""
    dclick.logger.informar(f"Consultando uma extração no Nora", extraction_id=extraction_id)
    response = (
        client_singleton()
        .get(f"/extractions/{extraction_id}")
    )

    try: return (
        response
        .esperar_status_code(200)
        .esperar_tipo_conteudo("json")
        .unmarshal(modelos.ResponseConsultar)
    )
    except Exception:
        dclick.logger.erro(
            "Falha ao consultar uma extração no Nora",
            extraction_id = extraction_id,
            response = response.text
        )
        raise

class PollingExtracao:
    """Classe para realizar o acompanhamento de extrações até o `status = sucesso/erro`
    - Variáveis utilizadas `[nora] -> host, apikey, [polling: 10, timeout: 300]`

    ### Utilização
    ```
    from dclick.nora import PollingExtracao

    polling = (
        # Inicializar o Polling e adicionar os `tracking_codes`
        PollingExtracao()
        .adicionar("vXRdxHZRrUKj", "wjM3N9ej0Iza", "...")
    )
    while polling.pendente():
        try: response = polling.aguardar()
        # Tempo ao aguardar a extração demorou mais tempo que o esperado
        except TimeoutError: raise
        # Erro inesperado
        except Exception: raise

        tracking_code = response.extraction.trackingCode
        if response.sucesso():
            print("Sucesso", tracking_code, response.data, response.confidence)
        elif response.erro_retry():
            print("Erro passível de retentativa", tracking_code)
        else:
            print("Erro extração", response.extraction.errorMessage)
    ```"""

    tracking_codes: Queue[str]
    """Fila de `tracking_codes`"""
    polling: int | float
    """Tempo de `polling` ao acompanhar uma extração"""
    timeout: int | float
    """Tempo de `timeout` para aguardar por uma extração"""

    def __init__ (self) -> None:
        self.tracking_codes = Queue()
        self.polling = bot.configfile.obter_opcao_ou("nora", "polling", 10.0)
        self.timeout = bot.configfile.obter_opcao_ou("nora", "timeout", 300.0)

    def adicionar (self, *tracking_code: str) -> Self:
        """Adicionar os `tracking_code` na fila"""
        for tc in tracking_code:
            self.tracking_codes.add(tc)
        return self

    def pendente (self) -> bool:
        """Checar se há algum `tracking_code` pendente na fila para ser aguardado"""
        return not self.tracking_codes.empty()

    def proximo_tracking_code (self) -> str:
        """Obter o próximo `tracking_code` que será aguardado
        - Necessário checar se há `self.pendente()` antes"""
        return self.tracking_codes.peek()

    def aguardar (self) -> modelos.ResponseAcompanhar:
        """Aguardar pela próxima extração finalizar em `sucesso` ou `error`
        - Necessário checar se há `self.pendente()` antes
        - Acompanhamentos feitos a cada `self.polling` segundos
        - `TimeoutError` caso o tempo de espera seja maior que `self.timeout`"""
        assert self.pendente(), "Não há nenhum tracking_code pendente para ser feito o Polling no NoraAI"

        tracking_code = self.tracking_codes.poll()
        timeout = (
            bot.tempo.Timeout(f"Tempo de espera pela extração do NoraAI demorou mais tempo que o esperado | tracking_code '{tracking_code}'")
            .segundos(self.timeout)
        )

        # Loop ou TimeoutError
        while timeout.pendente() or True:
            response = acompanhar_extracao(tracking_code)
            if response.pendente():
                bot.tempo.sleep(self.polling)
            else: return response

__all__ = [
    "executar_extracao",
    "acompanhar_extracao",
    "consultar_extracao",
    "PollingExtracao",
]