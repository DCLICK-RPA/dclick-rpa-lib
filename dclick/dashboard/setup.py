# std
from datetime import datetime as Datetime
# externo
import bot

def gravar_transacao (
        chave: str,
        identificador: str,
        mensagem: str = "",
        data_hora: Datetime | None = None) -> None:
    """Gravar transação na dashboard com os dados para a automação `codigo_automacao`
    - `data_hora=None` para usar o default `Datetime.today()`
    - Variáveis utilizadas `[dashboard] -> "codigo_automacao", "host"`"""
    chave, identificador, mensagem = map(str, (chave, identificador, mensagem))
    bot.logger.informar(f"Gravando uma transação no dashboard chave({chave}) identificador({identificador})")

    codigo_automacao, host = bot.configfile.obter_opcoes_obrigatorias("dashboard", "codigo_automacao", "host")
    response = bot.http.request(
        method  = "POST",
        url     = f"{host}/admin/api/Dashboard/GravarTransacao",
        timeout = 30,
        json    = {
            "CodigoAutomacao": codigo_automacao,
            "Chave": chave, 
            "Identificador": identificador,
            "DataHora": (data_hora or Datetime.today()).strftime("%Y-%m-%dT%H:%M:%S"),
            "Mensagem": mensagem if len(mensagem) <= 200 else mensagem[:200],
        },
    )

    assert response.is_success, f"O status code '{response.status_code}' foi diferente do esperado"

__all__ = [
    "gravar_transacao"
]