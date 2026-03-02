# interno
from dclick.erros.modelo import ModeloErroComLog

CATEGORIA = "API"

Timeout = ModeloErroComLog("API.TIMEOUT.032", CATEGORIA, "Tempo de resposta excedido na chamada", "Alta", "Sistema", "API")
"""Tempo de resposta excedido na chamada"""

Conexao = ModeloErroComLog("API.CONN.035", CATEGORIA, "Falha de conexão com endpoint da API", "Alta", "TI", "API")
"""Falha de conexão com endpoint da API"""

Autenticacao = ModeloErroComLog("API.AUTH.031", CATEGORIA, "Erro de autenticação na API", "Crítica", "TI/Sistema", "API")
"""Erro de autenticação na API"""

RespostaJson = ModeloErroComLog("API.JSON.034", CATEGORIA, "Erro ao processar JSON de resposta da API", "Alta", "Bot", "API")
"""Erro ao processar JSON de resposta da API"""

RetornoInesperado = ModeloErroComLog("API.RET.033", CATEGORIA, "Retorno inesperado da API", "Alta", "Sistema", "API")
"""Retorno inesperado da API"""

__all__ = [
    "Timeout",
    "Conexao",
    "Autenticacao",
    "RespostaJson",
    "RetornoInesperado",
]