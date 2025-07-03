# std
from __future__ import annotations
import typing
# interno
import dclick
# externo
import bot

NOME_MENU = "Título a Pagar"

class DadosRegistro:

    lancamento: str
    """Identificador do registro"""
    empresa: str
    cedente: str
    nroparcela: str
    tipo_de_titulo: str
    emissao: str
    entrada: str
    vencimento: str
    pagamento: str
    valor: str
    status: str

    def __eq__ (self, value: object) -> bool:
        return isinstance(value, type(self)) and self.lancamento == value.lancamento

    def __getattr__ (self, name: str) -> str:
        return ""

    def __repr__ (self) -> str:
        return f"<{type(self).__name__} {self.__dict__}>"

class TabelaRegistro:
    """Classe especializada para obter e filtrar os registros na tabela
    - Acessado iframe do menu da janela"""

    navegador: bot.navegador.Edge

    IFRAME_FILTRO_SELECAO       = "#gxp0_ifrm"
    FILTRO_SELECAO_EMPRESAS     = "//div[@id = 'GridselecaoContainerDiv']//a[contains(., 'Empresas')]"
    FILTRO_SELECAO_MARCAR_TODOS = "#BTNMARCARTODOS"
    FILTRO_SELECAO_CONFIRMAR    = "#IMGCONFIRMAR"

    TABELA_FILTRO_REGISTROS     = "#TABLESEARCH"
    INPUT_FILTRO_NUMERO_TITULO  = "#vTITULO_NUMERO"
    BOTAO_CONSULTAR             = "#BTNCONSULTAR"

    TABELA_REGISTROS            = "#GridContainerTbl"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        dclick.dealernet.menus.selecionar_opcao_menu(
            navegador,
            ["Contas a pagar", NOME_MENU],
            dclick.dealernet.menus.Menus.FINANCEIRO,
        )
        dclick.dealernet.menus.acessar_iframe_janela_menu(navegador, NOME_MENU)

    def filtro_selecao_todas_empresas (self) -> typing.Self:
        """Tratar o `IFRAME_FILTRO_SELECAO` que aparece automaticamente quando não há nenhum filtro
        - Não tem efeito caso o iframe não esteja visível
        - Selecionado todas as empresas"""
        self.navegador.encontrar(self.TABELA_FILTRO_REGISTROS).aguardar_visibilidade()
        localizadores = (self.FILTRO_SELECAO_EMPRESAS,
                         self.FILTRO_SELECAO_MARCAR_TODOS,
                         self.FILTRO_SELECAO_CONFIRMAR)

        try:
            with self.navegador.alterar_timeout(2)\
                               .encontrar(self.IFRAME_FILTRO_SELECAO)\
                               .aguardar_invisibilidade() as iframe:
                self.navegador.alterar_frame(iframe)
                for localizador in localizadores:
                    self.navegador.encontrar(localizador).clicar().sleep(0.5)

        except bot.navegador.ElementoNaoEncontrado: pass # iframe não visível
        finally:
            self.navegador.alterar_timeout()
            dclick.dealernet.menus.acessar_iframe_janela_menu(self.navegador, NOME_MENU)
        return self

    def filtrar (
            self,
            numero_titulo: str | None = None,
        ) -> typing.Self:
        """Aplicar o filtro na tabela dos registros"""
        itens: list[tuple[str | None, str]] = [
            (numero_titulo, self.INPUT_FILTRO_NUMERO_TITULO)
        ]

        tabela_filtro = self.navegador.encontrar(self.TABELA_FILTRO_REGISTROS)\
                                      .aguardar_visibilidade()
        for texto, localizador in itens:
            if texto == None: continue
            tabela_filtro.encontrar(localizador).limpar().digitar(texto)
        tabela_filtro.encontrar(self.BOTAO_CONSULTAR).clicar()

        self.navegador.encontrar(self.TABELA_REGISTROS)\
                      .aguardar_visibilidade()
        return self

    @bot.util.decoradores.retry(tentativas=2)
    def obter (self, filtro: typing.Callable[[DadosRegistro], bot.tipagem.SupportsBool]) -> DadosRegistro:
        """Obter o primeiro registro na tabela de acordo com o `filtro`
        - Retornado classe com os dados esperados da tabela dos registros
        - `ValueError` caso não encontre"""
        tabela_registros = self.navegador.encontrar(self.TABELA_REGISTROS)\
                                         .aguardar_visibilidade()

        # buscar os nomes dos headers e seus index
        dados_header = dict[int, str]()
        headers_esperados = list(map(bot.util.normalizar, DadosRegistro.__annotations__))

        for index, th in enumerate(tabela_registros.procurar("thead th")):
            texto = bot.util.normalizar(th.texto)
            if texto not in headers_esperados: continue
            dados_header[index] = texto

        assert dados_header, "Tabela NFe de item avulso não carregou conforme esperado"

        # buscar os registros
        for tr_registro in tabela_registros.procurar("tbody tr"):
            # popular os valores do registro com os nomes dos headers
            registro = DadosRegistro()
            for index, td_registro in enumerate(tr_registro.procurar("td")):
                if index not in dados_header: continue
                setattr(registro, dados_header[index], td_registro.texto)

            try:
                if filtro(registro): return registro
            except Exception: pass

        raise ValueError("Registro de item avulso não encontrado para o filtro informado")

__all__ = [
    "TabelaRegistro",
]