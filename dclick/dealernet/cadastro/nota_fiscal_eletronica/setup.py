# std
from __future__ import annotations
import typing
from datetime import date as Date
# interno
import dclick
# externo
import bot

NOME_MENU = "NFe"

class DadosRegistro:

    numero: str
    """Número nota fiscal"""
    serie: str
    ambiente: str
    tipo_emissao: str
    emissao: str
    """Data e hora da emissão"""
    natureza_operacao: str
    total: str
    """Valor total `1.234,56`"""
    destinatario: str
    vendedor: str
    status_nota_fiscal: str
    status_nfe: str
    status_servico: str

    def __eq__ (self, value: object) -> bool:
        return isinstance(value, type(self)) and self.numero == value.numero

    def __getattr__ (self, name: str) -> str:
        return ""

    def __repr__ (self) -> str:
        return f"<{type(self).__name__} {self.__dict__}>"

class TabelaRegistro:
    """Classe especializada para obter e filtrar os registros na tabela
    - Acessado iframe do menu da janela"""

    navegador: bot.navegador.Edge

    TABELA_FILTRO_REGISTROS         = "#TABLESEARCH"
    INPUT_FILTRO_NUMERO_NF          = "#vNOTAFISCALELETRONICA_NRONOTA"
    INPUT_FILTRO_PERIODO_INICIAL    = "#vNOTAFISCALELETRONICA_DATAEMISSAOINI"
    BOTAO_FILTRO_CONSULTAR          = "#IMGATUALIZAR"

    TABELA_REGISTROS                = "#GridContainerTbl"
    TABELA_REFRESH_AUTOMATICO       = "#vREFRESHAUTOMATICO"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        dclick.dealernet.menus.selecionar_opcao_menu(
            navegador,
            ["Nota Fiscal Eletronica", NOME_MENU],
            dclick.dealernet.menus.Localizadores.CADASTRO,
        )
        dclick.dealernet.menus.acessar_iframe_janela_menu(navegador, NOME_MENU)

    def desativar_refresh_automatico (self) -> typing.Self:
        """Clicar no botão para dsativar o refresh automático"""
        elemento = self.navegador.encontrar(self.TABELA_REFRESH_AUTOMATICO)
        if elemento.selecionado: elemento.clicar()
        return self

    def filtrar (
            self,
            numero_nf: str | None = None,
            periodo_inicial: Date | None = None
        ) -> typing.Self:
        """Aplicar o filtro na tabela dos registros"""
        with self.navegador.encontrar(self.TABELA_REGISTROS).aguardar_staleness():
            tabela_filtro = self.navegador.encontrar(self.TABELA_FILTRO_REGISTROS)
            itens = [(numero_nf, self.INPUT_FILTRO_NUMERO_NF),
                     (periodo_inicial.strftime("%d/%m/%Y") if periodo_inicial else None, self.INPUT_FILTRO_PERIODO_INICIAL)]

            for texto, localizador in itens:
                if texto == None: continue
                tabela_filtro.encontrar(localizador).limpar().clicar().digitar(bot.navegador.Teclas.BACKSPACE, texto)
            self.navegador.encontrar(self.BOTAO_FILTRO_CONSULTAR).clicar()

        return self

    def obter (self, filtro: typing.Callable[[DadosRegistro], bool | bot.tipagem.SupportsBool]) -> DadosRegistro:
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

class ExtrairDadosRegistro:
    """Classe para extrair dados um registro
    - `clicar_primeiro_numero_registro()` para abrir a tela da extração"""

    navegador: bot.navegador.Edge

    BOTAO_PRIMEIRO_NUMERO_REGISTRO  = "#GridContainerTbl > tbody > tr:nth-of-type(1) span[id *= 'NRONOTA' i] > a"
    TABELA_DADOS_VISAO_GERAL        = "table.DataTable .Table"
    TD_DESCRICAO                    = "td.DataDescriptionCell"
    TD_CONTEUDO                     = "td.DataContentCellView"
    BOTAO_VOLTAR                    = "table.TitleTable a"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        dclick.dealernet.menus.selecionar_opcao_menu(
            navegador,
            ["Nota Fiscal Eletronica", NOME_MENU],
            dclick.dealernet.menus.Localizadores.CADASTRO,
        )
        dclick.dealernet.menus.acessar_iframe_janela_menu(navegador, NOME_MENU)

    def clicar_primeiro_numero_registro (self) -> typing.Self:
        """Clicar no primeiro número da tabela dos registros
        - Abre a tela `Nota Fiscal Eletrônica` na aba `Visão Geral`"""
        with self.navegador.encontrar(self.BOTAO_PRIMEIRO_NUMERO_REGISTRO).aguardar_staleness() as elemento:
            elemento.clicar()
        return self

    def extrair_visao_geral (self) -> bot.estruturas.LowerDict[str]:
        """Extrair os dados da aba `Visão Geral`"""
        # mais rápido via script
        try:
            dados = self.navegador.driver.execute_script(f"""\
                let dados = {{}}
                let trs = document.querySelector("{self.TABELA_DADOS_VISAO_GERAL}")
                                .querySelectorAll("tr:has({self.TD_DESCRICAO})")
                for (let tr of trs) {{
                    descricao = tr.querySelector("{self.TD_DESCRICAO}").innerText.trim()
                    conteudo = tr.querySelector("{self.TD_CONTEUDO}").innerText.trim()
                    dados[descricao] = conteudo
                }}
                return dados
            """)
            if dados and isinstance(dados, dict):
                return bot.estruturas.LowerDict(dados)
        except Exception: pass

        # tenta via selenium caso script não resulte em sucesso
        dados = bot.estruturas.LowerDict[str]()
        tabela = self.navegador.encontrar(self.TABELA_DADOS_VISAO_GERAL)\
                               .aguardar_visibilidade()

        for tr in tabela.procurar(f"tr:has({self.TD_DESCRICAO})"):
            descricao = tr.encontrar(self.TD_DESCRICAO).texto
            conteudo = tr.encontrar(self.TD_CONTEUDO).texto
            dados[descricao] = conteudo

        assert dados, "Nenhum dado encontrado na tabela da visão geral"
        return dados

    def clicar_botao_voltar (self) -> None:
        """Clicar no botão voltar para retornar a tela das tabelas de registros"""
        with self.navegador.encontrar(self.BOTAO_VOLTAR).aguardar_staleness() as elemento:
            elemento.clicar()

__all__ = [
    "TabelaRegistro",
    "ExtrairDadosRegistro",
]