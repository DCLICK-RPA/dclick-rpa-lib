# std
from typing import Callable
# externo
import bot

janela_shortcut = lambda: bot.sistema.JanelaW32(
    lambda janela: janela.titulo.lower().startswith("nbs shortcut"),
    aguardar = 10
)
"""Janela `NBS ShortCut` aberta após login"""

@bot.util.decoradores.prefixar_erro("Falha ao abrir o NBS ou ao realizar login")
def abrir_e_login () -> bot.sistema.JanelaW32:
    """Abrir o NBS e realizar o login
    - Variáveis .ini `[nbs] -> usuario, senha, executavel`
    - Retorna a janela `NBS ShortCut`"""
    usuario, senha, executavel = bot.configfile.obter_opcoes_obrigatorias("nbs", "usuario", "senha", "executavel")
    bot.sistema.abrir_programa(executavel, shell=True)

    try: janela_login = bot.sistema.JanelaW32(lambda janela: janela.class_name == "TForm_SenhaLogin", aguardar=10)
    except Exception:
        raise Exception("Janela de login não foi encontrada após abrir o programa")

    bot.logger.informar("Aberto o NBS")
    filhos = janela_login.ordernar_elementos_coordenada(janela_login.elemento.filhos())
    input_usuario, input_senha = (filho for filho in filhos if filho.class_name == "TOvcPictureField")
    *_, input_confirmar = (filho for filho in filhos if filho.class_name == "TfcImageBtn")

    input_usuario.digitar(usuario)
    input_senha.digitar(senha)
    input_confirmar.clicar()

    assert bot.util.aguardar_condicao(
        lambda: janela_login.fechada,
        timeout = 10
    ), "Janela de login não fechou corretamente"
    bot.logger.informar("Login realizado")

    return janela_shortcut().focar()

def fechar_janelas_nbs (filtro: Callable[[bot.sistema.JanelaW32], bot.tipagem.SupportsBool] | None = None) -> None:
    """Fechar as janelas do NBS de acordo com o `filtro`
    - Default: Possui `NBS` no titulo"""
    filtro = filtro or (lambda j: "NBS" in j.titulo)
    try:
        janela = bot.sistema.JanelaW32(filtro)
        bot.logger.informar(f"Fechando a {janela!r}")
        janela.encerrar(1)
    except Exception: pass

__all__ = [
    "abrir_e_login",
    "janela_shortcut",
    "fechar_janelas_nbs",
]