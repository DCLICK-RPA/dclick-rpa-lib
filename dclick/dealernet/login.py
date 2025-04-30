# externo
import bot

class Localizadores:
    USUARIO     = "input#vUSUARIO_IDENTIFICADORALTERNATIVO"
    SENHA       = "input#vUSUARIOSENHA_SENHA"
    CONFIRMAR   = "input#IMAGE3"

def login (navegador: bot.navegador.Edge) -> None:
    """Realizar o login no dealernet
    - Recebe uma nova instância do `navegador` e realiza o login na aba aberta
    - Variáveis `[dealernet.login] -> url, usuario, senha`"""
    url, usuario, senha = bot.configfile.obter_opcoes_obrigatorias("dealernet.login", "url", "usuario", "senha")
    bot.logger.informar(f"Realizando login no Dealernet '{url}'")

    navegador.pesquisar(url)
    titulo = navegador.titulo

    navegador.encontrar(Localizadores.USUARIO).limpar().digitar(usuario)
    navegador.encontrar(Localizadores.SENHA).limpar().digitar(senha)
    navegador.encontrar(Localizadores.CONFIRMAR).clicar()

    # aguardar carregar
    assert bot.util.aguardar_condicao(
        lambda: navegador.titulo != titulo, 
        timeout = 15
    ), "Falha ao realizar login, o título da página não foi alterado após o tempo configurado"

    bot.logger.informar(f"Login realizado com sucesso e página carregada '{navegador.titulo}'")

__all__ = [
    "login"
]