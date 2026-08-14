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

DEFAULT_TIMEOUT = bot.config.nbs.obter_ou("timeout", 10)
"""TIMEOUT default utilizado nas esperas do NBS
- Default `10`
- Unidade `segundos`
- Alterado via variável .ini `[nbs] -> [timeout]`"""

def janela_shortcut (timeout: float = DEFAULT_TIMEOUT) -> JanelaW32:
    """Janela `NBS ShortCut` aberta após login"""
    return JanelaW32(
        lambda janela: janela.class_name == "TForm_Atalhos"
                       and janela.elemento.visivel,
        aguardar = timeout
    )

def janela_empresa_filial (timeout: float = DEFAULT_TIMEOUT) -> JanelaW32:
    """Janela de seleção da `Empresa/Filial` aberta antes de um módulo"""
    return bot.sistema.JanelaW32(
        lambda janela: "Empresa/Filial" in janela.titulo,
        aguardar = timeout
    )

@bot.erro.adicionar_prefixo("Falha ao abrir o NBS ou ao realizar login")
def abrir_e_login (usuario:  str | None = None,
                   senha:    str | None = None,
                   servidor: str | None = None,
                   janela_esperada: Callable[[float], JanelaW32] | None = None) -> JanelaW32:
    """Abrir o NBS e realizar o login
    - Variáveis .ini `[nbs] -> executavel, [usuario, senha, servidor]`
    - `janela_esperada: (timeout) -> JanelaW32` uma função para indicar a janela aberta do `executável`
    - Default `janela_esperada` procurado por `NBS ShortCut` ou `Empresa/Filial`"""
    secao = bot.config.nbs
    executavel = secao.executavel
    usuario    = usuario  or secao.usuario
    senha      = senha    or secao.senha
    servidor   = servidor or secao.obter_ou("servidor")

    # abrir
    dclick.logger.informar("Abrindo o NBS", usuario=usuario)
    janela_login = JanelaW32.Iniciar(executavel, aguardar=DEFAULT_TIMEOUT * 2)

    # versão nova
    try:
        input_usuario, input_senha = janela_login >> "TNBSWCustomInnerTextEdit"
        input_usuario.digitar(usuario)
        input_senha.digitar(senha)
        if servidor: (janela_login // "TNBSWCustomComboBoxInnerEdit[0]").digitar(servidor)
        confirmar = janela_login // "Entrar"
    # versão antiga
    except Exception:
        input_usuario, input_senha = janela_login >> "TOvcPictureField"
        input_usuario.input(usuario)
        input_senha.input(senha)
        if servidor: (janela_login // "TButtonedEdit[0]").input(servidor)
        confirmar = janela_login // "TfcImageBtn[0]"

    # clicar confirmar e aguardar fechar janela de login
    confirmar.sleep(0.5).clicar()
    if not bot.tempo.aguardar(lambda: janela_login.fechada, timeout=DEFAULT_TIMEOUT):
        raise TimeoutError("Janela de login não fechou conforme o esperado")

    # aguardar abrir
    def janela_ou_erro () -> JanelaW32 | str | None:
        if janela_esperada is not None:
            try: return janela_esperada(0)
            except Exception: pass
        else:
            try: return janela_shortcut(0)
            except Exception: pass
            try: return janela_empresa_filial(0)
            except Exception: pass

        if dialogo := JanelaW32(lambda j: j.dialogo()).dialogo():
            texto = dialogo.texto
            try: dialogo.confirmar()
            except Exception: pass
            return texto

    resultado = bot.tempo.esperar(janela_ou_erro, timeout=DEFAULT_TIMEOUT * 2, delay=0.25)
    match resultado.valor_ou(None):
        case JanelaW32() as janela:
            dclick.logger.debug(f"Login no NBS realizado | Aberto {janela}")
            return janela.focar()
        case str() as erro:
            encerrar_processos_nbs()
            raise AssertionError(f"Diálogo de erro encontrado após login no NBS: '{erro}'")
        case _:
            encerrar_processos_nbs()
            raise Exception("Janela do NBS não aberta após login")

def encerrar_processos_nbs (*nome_processo: str) -> None:
    """Encerrar os processos que comecem com o nome `NBS`
    - `nome_processo` para informar nomes adicionais"""
    n = bot.sistema.encerrar_processos_usuario("nbs", *nome_processo)
    dclick.logger.debug(f"Encerrado {n} processos do NBS")

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

    "janela_shortcut",
    "janela_empresa_filial",

    "abrir_e_login",
    "fechar_janelas_nbs",
    "encerrar_processos_nbs",
]