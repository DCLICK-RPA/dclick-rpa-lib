# interno
from dclick.erros.modelo import ModeloErroComLog

CATEGORIA = "Entrada"

PlanilhaNaoLocalizada = ModeloErroComLog("INPUT.MISS.001", CATEGORIA, "Planilha de entrada não localizada", "Alta", "Área de Negócio", "IN")
"""Planilha de entrada não localizada"""

PlanilhaVazia = ModeloErroComLog("INPUT.MISS.002", CATEGORIA, "Planilha de entrada está vazia", "Alta", "Área de Negócio", "IN")
"""Planilha de entrada está vazia"""

PlanilhaForaDoPadrao = ModeloErroComLog("INPUT.MISS.003", CATEGORIA, "Planilha fora do padrão", "Alta", "Área de Negócio", "IN")
"""Planilha fora do padrão"""

DadosInvalidosObrigatorios = ModeloErroComLog("INPUT.VAL.005", CATEGORIA, "Dados inválidos no campo obrigatório", "Alta", "Área de Negócio", "IN")
"""Dados inválidos no campo obrigatório"""

DadosDuplicados = ModeloErroComLog("INPUT.VAL.006", CATEGORIA, "Dados em duplicidade", "Média", "Área de Negócio", "IN")
"""Dados em duplicidade"""

DadosFormatacaoIncorreta = ModeloErroComLog("INPUT.VAL.007", CATEGORIA, "Dados com formatação incorreta", "Média", "Área de Negócio", "IN")
"""Dados com formatação incorreta"""

__all__ = [
    "PlanilhaVazia",
	"DadosDuplicados",
    "PlanilhaForaDoPadrao",
    "PlanilhaNaoLocalizada",
	"DadosFormatacaoIncorreta",
    "DadosInvalidosObrigatorios",
]