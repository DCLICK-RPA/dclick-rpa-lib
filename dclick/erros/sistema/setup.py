# interno
from dclick.erros.modelo import ModeloErroComLog

CATEGORIA = "Sistema"

FalhaLogin = ModeloErroComLog("SISTEMA.AUTH.008", CATEGORIA, "Falha de login no sistema", "Crítica", "TI/Área de Negócio", "Fluxo Principal")
"""Falha de login no sistema"""

TimeoutResposta = ModeloErroComLog("SISTEMA.TIMEOUT.009", CATEGORIA, "Timeout na resposta do sistema", "Crítica", "Sistema", "Fluxo Principal")
"""Timeout na resposta do sistema"""

ForaDoAr = ModeloErroComLog("SISTEMA.BLOQ.010", CATEGORIA, "Sistema fora do ar", "Crítica", "Sistema", "Fluxo Principal")
"""Sistema fora do ar"""

ElementoOuImagemNaoEncontrado = ModeloErroComLog("SISTEMA.UI.011", CATEGORIA, "Elemento/imagem esperado não encontrado na tela", "Alta", "Bot", "Fluxo Principal")
"""Elemento/imagem esperado não encontrado na tela"""

MudancaLayout = ModeloErroComLog("SISTEMA.UI.012", CATEGORIA, "Mudança de layout/interface", "Alta", "Sistema", "Fluxo Principal")
"""Mudança de layout/interface"""

PermissaoModuloOuFuncao = ModeloErroComLog("SISTEMA.PERM.013", CATEGORIA, "Usuário sem permissão para acessar módulo/função", "Alta", "Área de Negócio", "Fluxo Principal")
"""Usuário sem permissão para acessar módulo/função"""

__all__ = [
    "ForaDoAr",
    "FalhaLogin",
	"MudancaLayout",
    "TimeoutResposta",
	"PermissaoModuloOuFuncao",
    "ElementoOuImagemNaoEncontrado",
]