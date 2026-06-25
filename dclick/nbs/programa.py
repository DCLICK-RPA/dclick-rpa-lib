# std
from typing import Callable
# interno
import dclick
# externo
import bot
from bot.sistema import JanelaW32
# externo opcional
try: from bot import imagem
except ImportError: raise ImportError(
    "Dependência opcional 'dclick[nbs]' necessária. "
    "Instale como 'dclick[nbs]' para utilizar o módulo 'dclick.nbs'"
)

DEFAULT_TIMEOUT = bot.configfile.obter_opcao_ou("nbs", "timeout", 10)
"""TIMEOUT default utilizado nas esperas do NBS
- Default `10`
- Unidade `segundos`
- Alterado via variável .ini `[nbs] -> [timeout]`"""

janela_shortcut = lambda: JanelaW32(
    lambda janela: janela.class_name == "TForm_Atalhos"
                   and janela.elemento.visivel,
    aguardar = DEFAULT_TIMEOUT
)
"""Janela `NBS ShortCut` aberta após login"""

@bot.erro.adicionar_prefixo("Falha ao abrir o NBS ou ao realizar login")
def abrir_e_login (usuario: str | None = None, senha: str | None = None) -> JanelaW32:
    """Abrir o NBS e realizar o login
    - Variáveis .ini `[nbs] -> executavel, [usuario, senha]`
    - Retorna a janela `NBS ShortCut`"""
    executavel, *_ = bot.configfile.obter_opcoes_obrigatorias("nbs", "executavel")
    usuario = usuario or bot.configfile.obter_opcoes_obrigatorias("nbs", "usuario")[0]
    senha = senha or bot.configfile.obter_opcoes_obrigatorias("nbs", "senha")[0]

    dclick.logger.informar("Abrindo o NBS", usuario=usuario)
    janela_login = JanelaW32.iniciar(executavel, aguardar=DEFAULT_TIMEOUT * 2)

    filhos = janela_login.ordernar_elementos_coordenada(janela_login.elemento.filhos(aguardar=5))
    input_usuario, input_senha = (filho for filho in filhos if filho.class_name == "TOvcPictureField")
    *_, input_confirmar = (filho for filho in filhos if filho.class_name == "TfcImageBtn")
    input_usuario.digitar(usuario)
    input_senha.digitar(senha)
    input_confirmar.sleep(0.5).clicar()

    assert bot.tempo.aguardar(
        lambda: janela_login.fechada,
        timeout = DEFAULT_TIMEOUT
    ), "Janela de login não fechou corretamente"

    try:
        janela = janela_shortcut().focar()
        dclick.logger.debug(f"Login realizado | Aberto {janela}")
        return janela
    except Exception: pass

    try:
        dialogo = JanelaW32(lambda j: j.dialogo()).dialogo()
        assert dialogo
        raise AssertionError(f"Diálogo de erro encontrado após login: '{dialogo.texto}'")
    except AssertionError: raise
    except Exception: raise Exception("Janela Shortcut não aberta após login")

def fechar_janelas_nbs (filtro: Callable[[JanelaW32], bot.tipagem.SupportsBool] | None = None) -> None:
    """Fechar as janelas do NBS de acordo com o `filtro`
    - Default: Começar com `NBS` no titulo"""
    filtro = filtro or (lambda j: j.titulo.lower().startswith("nbs"))
    try:
        while janela := JanelaW32(filtro, aguardar=0.5):
            dclick.logger.debug(f"Fechando a {janela!r}")
            janela.encerrar(1)
    except Exception: pass

__all__ = [
    "DEFAULT_TIMEOUT",

    "abrir_e_login",
    "janela_shortcut",
    "fechar_janelas_nbs",
]