# interno
from dclick.erros.modelo import ModeloErroComLog

CATEGORIA = "Arquivo"

FalhaPDF = ModeloErroComLog("ARQUIVO.PDF.014", CATEGORIA, "Falha ao gerar/baixar PDF", "Alta", "Sistema", "OUT")
"""Falha ao gerar/baixar PDF"""

NomeInvalidoOuDuplicado = ModeloErroComLog("ARQUIVO.NOME.015", CATEGORIA, "Nome de arquivo inválido ou duplicado", "Média", "Bot", "OUT")
"""Nome de arquivo inválido ou duplicado"""

SalvarArquivo = ModeloErroComLog("ARQUIVO.FALHA.016", CATEGORIA, "Falha ao salvar arquivo", "Alta", "Bot", "OUT")
"""Falha ao salvar arquivo"""

__all__ = [
    "FalhaPDF",
    "SalvarArquivo",
    "NomeInvalidoOuDuplicado",
]