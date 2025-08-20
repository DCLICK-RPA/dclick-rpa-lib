# std
from typing import Callable
# externo
import bot
from bot.sistema import JanelaW32

janela_shortcut = lambda: JanelaW32(
    lambda janela: janela.class_name == "TForm_Atalhos"
                   and janela.elemento.visivel,
    aguardar = 10
)
"""Janela `NBS ShortCut` aberta após login"""

@bot.util.decoradores.prefixar_erro("Falha ao abrir o NBS ou ao realizar login")
def abrir_e_login () -> JanelaW32:
    """Abrir o NBS e realizar o login
    - Variáveis .ini `[nbs] -> usuario, senha, executavel`
    - Retorna a janela `NBS ShortCut`"""
    usuario, senha, executavel = bot.configfile.obter_opcoes_obrigatorias("nbs", "usuario", "senha", "executavel")
    janela_login = JanelaW32.iniciar(executavel)
    bot.logger.informar("Aberto o NBS")

    filhos = janela_login.ordernar_elementos_coordenada(janela_login.elemento.filhos(aguardar=5))
    input_usuario, input_senha = (filho for filho in filhos if filho.class_name == "TOvcPictureField")
    *_, input_confirmar = (filho for filho in filhos if filho.class_name == "TfcImageBtn")

    input_usuario.digitar(usuario)
    input_senha.digitar(senha)
    input_confirmar.sleep(0.5).clicar()

    assert bot.util.aguardar_condicao(
        lambda: janela_login.fechada,
        timeout = 10
    ), "Janela de login não fechou corretamente"

    try:
        janela = janela_shortcut().focar()
        bot.logger.informar(f"Login realizado | Aberto {janela}")
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
            bot.logger.informar(f"Fechando a {janela!r}")
            janela.encerrar(1)
    except Exception: pass

__all__ = [
    "abrir_e_login",
    "janela_shortcut",
    "fechar_janelas_nbs",
]