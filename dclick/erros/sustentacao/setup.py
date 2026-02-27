# interno
from dclick.erros.modelo import ModeloErroComLog

CATEGORIA = "Sustentação"

ExcecaoNaoMapeada = ModeloErroComLog("EXC.NAO.MAP.026", CATEGORIA, "Exceção não mapeada na tratativa", "Alta", "Bot", "Fluxo Principal")
"""Exceção não mapeada na tratativa"""

FalhaTratativaErro = ModeloErroComLog("EXC.TRAT.027", CATEGORIA, "Tratativa de erro falhou", "Crítica", "Bot", "Fluxo Principal")
"""Tratativa de erro falhou"""

__all__ = [
    "ExcecaoNaoMapeada",
    "FalhaTratativaErro",
]