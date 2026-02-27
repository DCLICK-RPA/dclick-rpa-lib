# interno
from dclick.erros.modelo import ModeloErroComLog

CATEGORIA = "Execução"

ExcecaoNaoTratada = ModeloErroComLog("BOT.ERRO.022", CATEGORIA, "Exceção não tratada", "Crítica", "Bot", "Fluxo Principal")
"""Exceção não tratada"""

LoopInfinito = ModeloErroComLog("BOT.LOOP.023", CATEGORIA, "Loop infinito detectado", "Crítica", "Bot", "Fluxo Principal")
"""Loop infinito detectado"""

TempoDeExecucaoAcimaDoEsperado = ModeloErroComLog("BOT.TEMP.024", CATEGORIA, "Tempo de execução acima do esperado", "Média", "Bot", "Fluxo Principal")
"""Tempo de execução acima do esperado"""

ValorNuloOuInexistente = ModeloErroComLog("BOT.ABS.025", CATEGORIA, "Tentativa de acessar valor nulo/inexistente", "Alta", "Bot", "Fluxo Principal")
"""Tentativa de acessar valor nulo/inexistente"""

__all__ = [
    "LoopInfinito",
    "ExcecaoNaoTratada",
    "ValorNuloOuInexistente",
    "TempoDeExecucaoAcimaDoEsperado",
]