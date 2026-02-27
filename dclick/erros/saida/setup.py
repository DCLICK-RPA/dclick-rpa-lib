# interno
from dclick.erros.modelo import ModeloErroComLog

CATEGORIA = "Saída"

ArquivoNaoGerado = ModeloErroComLog("OUTPUT.MISS.017", CATEGORIA, "Planilha/PDF de saída não foi gerado", "Crítica", "Bot", "OUT")
"""Planilha/PDF de saída não foi gerado"""

PreenchimentoArquivo = ModeloErroComLog("OUTPUT.ERRO.018", CATEGORIA, "Erro ao preencher planilha de saída", "Média", "Bot", "OUT")
"""Erro ao preencher planilha de saída"""

__all__ = [
    "ArquivoNaoGerado",
    "PreenchimentoArquivo",
]