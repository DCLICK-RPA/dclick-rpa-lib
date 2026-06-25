# interno
import dclick
# externo
import bot
# externo opcional
try: from bot.navegador import Navegador
except ImportError: raise ImportError(
    "Dependência opcional 'dclick[dealernet]' necessária. "
    "Instale como 'dclick[dealernet]' para utilizar o módulo 'dclick.dealernet'"
)

class Localizadores:
    USUARIO     = "input#vUSUARIO_IDENTIFICADORALTERNATIVO"
    SENHA       = "input#vUSUARIOSENHA_SENHA"
    CONFIRMAR   = "input#IMAGE3"

def login (navegador: Navegador) -> None:
    """Realizar o login no dealernet
    - Recebe uma nova instância do `navegador` e realiza o login na aba aberta
    - Variáveis `[dealernet.login] -> url, usuario, senha`"""
    url, usuario, senha = bot.configfile.obter_opcoes_obrigatorias("dealernet.login", "url", "usuario", "senha")
    dclick.logger.informar(f"Realizando login no Dealernet '{url}'")

    navegador.pesquisar(url)
    titulo = navegador.titulo

    navegador.encontrar(Localizadores.USUARIO).limpar().digitar(usuario)
    navegador.encontrar(Localizadores.SENHA).limpar().digitar(senha)
    navegador.encontrar(Localizadores.CONFIRMAR).clicar()

    # aguardar carregar
    assert bot.tempo.aguardar(
        lambda: navegador.titulo != titulo, 
        timeout = 15
    ), "Falha ao realizar login, o título da página não foi alterado após o tempo configurado"

    dclick.logger.debug(f"Login realizado com sucesso e página carregada '{navegador.titulo}'")

__all__ = [
    "login"
]