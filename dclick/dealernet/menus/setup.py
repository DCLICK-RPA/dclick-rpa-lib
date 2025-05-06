# std
from enum import Enum
from typing import Iterable
from functools import cache
# externo
import bot

class Localizadores (Enum):
    """Classe com os Localizadores dos menus suportados"""

    EMPRESA    = """(//tr[contains(@class, "x-toolbar-right")])[2]/td/table//button"""
    PRODUTOS   = """//button[contains(text(), "Produtos")]"""
    CADASTRO   = """//button[contains(text(), "Cadastro")]"""
    INTEGRACAO = """//button[contains(text(), "Integração")]"""
    FINANCEIRO = """//button[contains(text(), "Financeiro")]"""

    JANELA_MENU = """html > body > div > div[id *= "W5Window"].W5Window"""
    FECHAR_JANELA_MENU = ".x-window-header .x-tool-close"
    TEXTO_JANELA_MENU = "span.x-window-header-text"

@cache
def de_para_opcoes () -> bot.estruturas.LowerDict[list[str]]:
    secao = "dealernet.menu.opcoes_empresa"
    return bot.estruturas.LowerDict({
        opcao: [
            item.strip()
            for item in bot.configfile.obter_opcao_ou(secao, opcao).split(",")
            if item.strip()
        ]
        for opcao in bot.configfile.opcoes_secao(secao)
    })

def opcoes_empresa (chave: str) -> list[str] | None:
    """Obter as opções de navegação da empresa de acordo com a `chave` fornecida
    - `None` caso não encontre
    - Variáveis `[dealernet.menu.opcoes_empresa]` com opções dinâmicas:
        - `chave = opcao1, opcao2, ...`"""
    return de_para_opcoes().get(chave)

def fechar_janelas_menu_abertas (navegador: bot.navegador.Edge) -> None:
    """Fechar todas as janelas de menu que estão abertas
    - Ao selecionar uma opção menu que não seja empresa, será aberto uma janela manu"""
    janelas = navegador.alterar_frame().procurar(Localizadores.JANELA_MENU)
    for janela in reversed(janelas):
        try:
            navegador.driver.execute_script("arguments[0].style.zIndex = 9999;", janela.elemento)
            janela.encontrar(Localizadores.FECHAR_JANELA_MENU).clicar()
        except Exception: pass

def acessar_iframe_janela_menu (navegador: bot.navegador.Edge, nome_menu: str) -> None:
    """Acessar o iframe do menu aberto com o `nome_menu`
    - `nome_menu` observado ser a última parte das opções em `selecionar_opcao_menu()`
    - Menu é trago para frente dos demais menus"""
    janela_encontrada = None
    nome_menu = bot.util.normalizar(nome_menu)

    for janela in navegador.alterar_frame().procurar(Localizadores.JANELA_MENU):
        texto = janela.encontrar(Localizadores.TEXTO_JANELA_MENU).texto
        if bot.util.normalizar(texto) == nome_menu: janela_encontrada = janela
        else: navegador.driver.execute_script("arguments[0].style.zIndex = 9900;", janela.elemento)

    if not janela_encontrada:
        raise Exception(f"Nenhum menu encontrado com nome '{nome_menu}'")

    navegador.driver.execute_script("arguments[0].style.zIndex = 9999;", janela_encontrada.elemento)
    navegador.alterar_frame(janela_encontrada.encontrar("iframe"))

def selecionar_opcao_menu (
        navegador: bot.navegador.Edge,
        opcoes: Iterable[str],
        menu: Localizadores = Localizadores.EMPRESA,
    ) -> None:
    """Clicar no localizador do `menu` e navegar pelas `opcoes` clicando em cada opção do menu de acordo com o texto
    - Checado se o `menu` já se encontra selecionado
    - Exemplo: `selecionar_opcao_menu(navegador, ["Nota Fiscal", "NF Entrada Item Avulso"], Localizadores.PRODUTOS)`"""
    opcoes = [bot.util.normalizar(opcao) for opcao in opcoes]
    assert opcoes, "Nenhuma opção informada"
    bot.logger.informar(f"Selecionando as opções [{" -> ".join(opcoes)}] no menu '{menu.name.capitalize()}' do Dealernet")

    elemento_menu = navegador.alterar_frame().encontrar(menu)

    # checar se já se encontra selecionado
    if menu is Localizadores.EMPRESA and opcoes[-1] == bot.util.normalizar(elemento_menu.texto):
        return bot.logger.informar("Opção da Empresa já se encontrava selecionada")
    if bot.estruturas.Resultado(acessar_iframe_janela_menu, navegador, opcoes[-1]):
        navegador.alterar_frame()
        return bot.logger.informar("Opção do Menu já se encontrava selecionada")

    # abrir menu
    elemento_menu.clicar()

    # navegar nas opções
    id_ul_selecionados: list[str] = []
    for opcao in opcoes:
        # encontrar `/html/body/div/ul` que está visivel e ainda não foi selecionado
        ul, *_ = [
            e for e in navegador.procurar("html > body> div[style *= 'visible' i] > ul")
            if e.atributos.get("id", "") not in id_ul_selecionados
        ] or [None]
        assert ul, f"Nenhum novo elemento <ul> ficou visível | Opção: '{opcao}'"

        id_ul = ul.atributos.get("id", "")
        id_ul_selecionados.append(id_ul)

        # encontrar `/ul/a` onde o texto seja igual a `opção` desejada
        opcao_ul, *_ = [
            e for e in ul.procurar("li > a")
            if opcao == bot.util.normalizar(e.texto)
        ] or [None]
        assert opcao_ul, f"Nenhuma das opções do <ul> possui o texto da opção '{opcao}'"

        # realizar ação na opção
        # hover se tiver mais elementos para serem carregados, click quando chegar no último
        if "x-menu-item-arrow" in opcao_ul.atributos.get("class", ""):
            opcao_ul.hover().sleep(0.5)
        else:
            with opcao_ul.aguardar_invisibilidade(): opcao_ul.clicar()

    bot.logger.informar("Opções selecionadas com sucesso")

__all__ = [
    "Localizadores",
    "opcoes_empresa",
    "selecionar_opcao_menu",
    "acessar_iframe_janela_menu",
    "fechar_janelas_menu_abertas",
]