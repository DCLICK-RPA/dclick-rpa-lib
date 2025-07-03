# std
import typing
# interno
import dclick
# externo
import bot

NOME_MENU = "NF Entrada Produto"

class DadosRegistro:

    codigo: str
    numero: str
    """Número Nota Fiscal"""
    serie: str
    grupo_movimento: str
    nro_os: str
    emissao: str
    """Data e hora da emissão da nota fiscal"""
    movimento: str
    """Data de movimento"""
    pessoa: str
    valor_total: str
    status: str

    def __eq__ (self, value: object) -> bool:
        return isinstance(value, DadosRegistro) and self.codigo == value.codigo

    def __getattr__ (self, name: str) -> str:
        return ""

    def __repr__ (self) -> str:
        return f"<Registro {self.__dict__}>"

class TabelaRegistro:
    """Classe especializada para obter e filtrar os registros na tabela
    - Acessado iframe do menu da janela"""

    navegador: bot.navegador.Edge

    TABELA_FILTRO_REGISTROS = "#TABLESEARCH"
    INPUT_FILTRO_CODIGO     = "#vNOTAFISCAL_CODIGO"
    INPUT_FILTRO_NUMERO_NF  = "#vNOTAFISCAL_NUMERO"
    BOTAO_FILTRO_CONSULTAR  = "#IMGREFRESH"
    TABELA_REGISTROS        = "#GridContainerTbl"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        dclick.dealernet.menus.selecionar_opcao_menu(
            navegador,
            ["Nota Fiscal", NOME_MENU],
            dclick.dealernet.menus.Menus.PRODUTOS,
        )
        dclick.dealernet.menus.acessar_iframe_janela_menu(navegador, NOME_MENU)

    def filtrar (
            self,
            codigo: str | None = None,
            numero_nf: str | None = None,
        ) -> typing.Self:
        """Aplicar o filtro na tabela dos registros"""
        with self.navegador.encontrar(self.TABELA_REGISTROS).aguardar_staleness():
            tabela_filtro = self.navegador.encontrar(self.TABELA_FILTRO_REGISTROS)

            for texto, localizador in [(codigo, self.INPUT_FILTRO_CODIGO),
                                       (numero_nf, self.INPUT_FILTRO_NUMERO_NF)]:
                if texto == None: continue
                tabela_filtro.encontrar(localizador).limpar().digitar(texto)

            self.navegador.encontrar(self.BOTAO_FILTRO_CONSULTAR).clicar()

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