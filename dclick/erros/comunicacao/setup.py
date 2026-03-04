# interno
from dclick.erros.modelo import ModeloErroComLog

CATEGORIA = "Comunicação"

LimiteEnvioEmail = ModeloErroComLog("EMAIL.END.004", CATEGORIA, "Limite de envio de e-mails atingido", "Alta", "TI", "OUT")
"""Limite de envio de e-mails atingido"""

EnvioEmailComResultados = ModeloErroComLog("EMAIL.FALHA.019", CATEGORIA, "Falha no envio de e-mail com resultados", "Alta", "Bot", "OUT")
"""Falha no envio de e-mail com resultados"""

EnderecoEmailInvalido = ModeloErroComLog("EMAIL.END.020", CATEGORIA, "Endereço de e-mail inválido", "Média", "Área de Negócio", "OUT")
"""Endereço de e-mail inválido"""

__all__ = [
    "LimiteEnvioEmail",
    "EnderecoEmailInvalido",
    "EnvioEmailComResultados",
]