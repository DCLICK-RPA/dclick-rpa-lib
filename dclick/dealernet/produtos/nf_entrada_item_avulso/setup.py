# std
from __future__ import annotations
import typing, datetime
# interno
import dclick
# externo
import bot

NOME_MENU = "NF Entrada Item Avulso"

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

class ModificarDadosRegistro:
    """Classe para tratar a modificação dos dados de um registro
    - `clicar_modificar_dados(registro)` para iniciar a modificação"""

    navegador: bot.navegador.Edge

    BOTAO_MODIFICAR_DADOS_REGISTRO  = "tbody > tr:nth-child(1) > td > input[title *= 'modifica' i]"
    # Usado `nth-child(1)` pois é feito o filtro pelo código do registro, logo esperado apenas 1
    SELECAO_CONDICAO_PAGAMENTO      = "#vNOTAFISCAL_CONDICAOPAGAMENTOCOD"
    INPUT_DATA_CHEGADA              = "#vNOTAFISCAL_DATACHEGADA"
    INPUT_DATA_MOVIMENTO            = "#vNOTAFISCAL_DATAMOVIMENTO"
    BOTAO_CONFIRMAR                 = "#CONFIRMA"
    POPUP_STATUS                    = "div#DVELOP_CONFIRMPANELContainer_ConfirmPanel_c.DVelop-Simple-Dialog"
    BOTAO_OK_POPUP                  = ".Footer button"

    BOTAO_PARCELAS                  = "#PARCELA"
    BOTAO_RODAPE                    = "#RODAPE"
    BOTAO_EDITAR_PRIMEIRO_ITEM      = "table#GriditemContainerTbl > tbody > tr:nth-of-type(1) input[name *= 'vUPDATE' i]"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        dclick.dealernet.menus.acessar_iframe_janela_menu(navegador, NOME_MENU)
        bot.logger.informar("Iniciando modificação dos dados")

    def clicar_modificar_dados (self, registro: DadosRegistro) -> typing.Self:
        """Clicar para modificar os dados do item avulso para o `registro`
        - Abre a tela de modificação
        - Feito o filtro do registro automaticamente"""
        TabelaRegistro(self.navegador).filtrar(registro.codigo)

        with self.navegador.encontrar(TabelaRegistro.TABELA_REGISTROS).aguardar_staleness() as tabela_registros:
            tabela_registros.encontrar(self.BOTAO_MODIFICAR_DADOS_REGISTRO).clicar()

        return self

    def selecionar_condicao_pagamento (self, texto: str) -> typing.Self:
        """Selecionar a condição de pagamento de acordo com o `texto`"""
        self.navegador.encontrar(self.SELECAO_CONDICAO_PAGAMENTO)\
            .select\
            .select_by_visible_text(texto)
        return self

    def alterar_data_chegada (self, data: datetime.date) -> typing.Self:
        self.navegador.encontrar(self.INPUT_DATA_CHEGADA)\
            .limpar()\
            .clicar()\
            .digitar(bot.navegador.Teclas.BACKSPACE, data.strftime("%d/%m/%Y"))
        return self

    def alterar_data_movimento (self, data: datetime.date) -> typing.Self:
        self.navegador.encontrar(self.INPUT_DATA_MOVIMENTO)\
            .limpar()\
            .clicar()\
            .digitar(bot.navegador.Teclas.BACKSPACE, data.strftime("%d/%m/%Y"))
        return self

    def clicar_botao_confirmar (self) -> typing.Self:
        """Clicar no botão Confirmar"""
        self.navegador.encontrar(self.BOTAO_CONFIRMAR).clicar()
        return self

    def capturar_mensagem_popup (self) -> str:
        """Capturar a mensagem do popup que aparece após clicar no botão de Confirmar"""
        return self.navegador.encontrar(self.POPUP_STATUS)\
                             .aguardar_visibilidade()\
                             .texto

    def clicar_botao_ok_popup (self) -> None:
        """Clicar no botão OK no Popup
        - Aguardado popup ficar invisível"""
        with self.navegador.encontrar(self.POPUP_STATUS).aguardar_invisibilidade() as popup:
            popup.encontrar(self.BOTAO_OK_POPUP).clicar()

    def clicar_botao_parcelas (self) -> ModificarParcelasRegistro:
        """Clicar para modificar as parcelas
        - Abre a tela de modificação das parcelas
        - Retorna a classe para tratamento da modificação das parcelas
        - Acessado iframe das parcelas"""
        self.navegador.encontrar(self.BOTAO_PARCELAS).clicar()
        iframe = self.navegador.encontrar(ModificarParcelasRegistro.IFRAME_PARCELAS)
        return ModificarParcelasRegistro(self.navegador.alterar_frame(iframe))

    def clicar_botao_rodape (self) -> ModificarRodapeRegistro:
        """Clicar para modificar o rodapé
        - Abre a tela de modificação do rodapé
        - Retorna a classe para tratamento da modificação do rodapé"""
        with self.navegador.encontrar(self.BOTAO_RODAPE).aguardar_staleness() as botao:
            botao.clicar()
        return ModificarRodapeRegistro(self.navegador)

    def clicar_botao_editar_primeiro_item (self) -> EditarItemRegistro:
        """Clicar para editar o primeiro item
        - Abre a tela de edição do item
        - Retorna a classe para tratamento da edição do item"""
        with self.navegador.encontrar(self.BOTAO_EDITAR_PRIMEIRO_ITEM).aguardar_staleness() as botao:
            botao.clicar()
        return EditarItemRegistro(self.navegador)

class ModificarParcelasRegistro:
    """Classe para tratar a modificação das parcelas dentro do registro
    - Esperado estar na tela de modificação das parcelas
    - Obtido a partir do `ModificarDadosRegistro().clicar_botao_parcelas()` para iniciar a modificação"""

    navegador: bot.navegador.Edge

    IFRAME_PARCELAS         = "#gxp0_ifrm"
    BOTAO_INSERIR_PARCELA   = "#INSERT"
    TABELA_PARCELAS         = "#GridparcelaContainerTbl"
    INPUT_DATA_VENCIMENTO   = "input[id *= 'DATAVENCIMENTO' i]"
    INPUT_VALOR             = "input[id *= 'VALOR' i]"
    SELECAO_TIPO_TITULO     = "select[id *= 'TIPOTITULO' i]"
    BOTAO_CONFIRMAR         = "#BTNCONFIRMAR"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        bot.logger.informar("Iniciando modificação das parcelas")

    def clicar_botao_inserir_parcela (self) -> typing.Self:
        """Clicar no botão para inserir uma nova parcela"""
        self.navegador.encontrar(self.BOTAO_INSERIR_PARCELA).clicar()
        return self

    def alterar_ultima_parcela (
            self,
            data_vencimento: datetime.date | None = None,
            valor: str | None = None,
            tipo_titulo: str | None = None,
        ) -> typing.Self:
        """Alterar o último registro da tabela com os dados `data_vencimento, valor e tipo_titulo`
        - `valor` no formato `12345,67`
        - Usar com o `clicar_botao_inserir_parcela()`"""
        ultimo_registro = self.navegador.encontrar(self.TABELA_PARCELAS).encontrar("tbody > tr:last-of-type")

        for texto, localizador in [(data_vencimento.strftime("%d/%m/%Y") if data_vencimento else None, self.INPUT_DATA_VENCIMENTO),
                                   (valor, self.INPUT_VALOR)]:
            if texto == None: continue
            ultimo_registro.encontrar(localizador)\
                           .limpar()\
                           .clicar()\
                           .digitar(bot.navegador.Teclas.BACKSPACE, texto)

        if tipo_titulo: ultimo_registro.encontrar(self.SELECAO_TIPO_TITULO)\
                                       .select\
                                       .select_by_visible_text(tipo_titulo)
        
        return self

    def clicar_botao_confirmar (self) -> None:
        """Clicar no botão para confirmar
        - Esperado o botão ficar invisível
        - Retornado ao iframe do menu"""
        with self.navegador.encontrar(self.BOTAO_CONFIRMAR).aguardar_invisibilidade() as botao:
            botao.clicar()
        dclick.dealernet.menus.acessar_iframe_janela_menu(self.navegador, NOME_MENU)

class ModificarRodapeRegistro:
    """Classe para tratar a modificação do rodapé dentro do registro
    - Esperado estar na tela de modificação do rodapé
    - Obtido a partir do `ModificarDadosRegistro().clicar_botao_rodape()` para iniciar a modificação"""

    navegador: bot.navegador.Edge

    SELECAO_TIPO_FRETE  = "select#vNOTAFISCAL_TIPOFRETE"
    BOTAO_CONFIRMAR     = "#BTNCONFIRMA"
    BOTAO_FECHAR        = "#TRN_CANCEL"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        bot.logger.informar("Iniciando modificação do rodapé")

    def selecionar_tipo_frete (self, texto: str) -> typing.Self:
        """Selecionar o tipo de frete de acordo com o `texto`"""
        self.navegador.encontrar(self.SELECAO_TIPO_FRETE)\
            .select\
            .select_by_visible_text(texto)
        return self

    def clicar_confirmar_e_fechar (self) -> None:
        """Clicar no botão para confirmar e fechar
        - Pode ser que apenas o confirmar não feche a tela do rodapé e seja necessário clicar no fechar após
        - Retornado para a tela anterior
        - Esperado o botão ficar invisível"""
        with self.navegador.encontrar(self.BOTAO_CONFIRMAR).aguardar_invisibilidade() as botao:
            botao.clicar().sleep(1)

        try:
            # checar se continou na tela do rodapé
            self.navegador.alterar_timeout(2).encontrar(self.SELECAO_TIPO_FRETE)
            # fechar tela rodapé
            with self.navegador.encontrar(self.BOTAO_FECHAR).aguardar_invisibilidade() as botao:
                botao.clicar()
        # tela rodapé fechada
        except bot.navegador.ElementoNaoEncontrado: return
        finally: self.navegador.alterar_timeout()

class EditarItemRegistro:
    """Classe para tratar a edição de um item dentro do registro
    - Esperado estar na tela de edição do item
    - Obtido a partir do `ModificarDadosRegistro().clicar_botao_editar_primeiro_item()` para iniciar a edição"""

    navegador: bot.navegador.Edge

    SELECAO_PROCEDENCIA = "select#vNOTAFISCALITEM_PROCEDENCIACOD"
    INPUT_DESCRICAO     = "textarea#vNOTAFISCALITEM_OBSERVACAO"
    BOTAO_CONFIRMAR     = "#CONFIRMAR"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        bot.logger.informar("Iniciando edição do item")

    def alterar_descricao (self, texto: str) -> typing.Self:
        """Alterar a descrição de acordo com o `texto`"""
        self.navegador.encontrar(self.INPUT_DESCRICAO)\
            .limpar()\
            .digitar(texto)
        return self

    def selecionar_procedencia (self, texto: str) -> typing.Self:
        """Selecionar a procedência de acordo com o `texto`"""
        self.navegador.encontrar(self.SELECAO_PROCEDENCIA)\
            .select\
            .select_by_visible_text(texto)
        return self

    def clicar_botao_confirmar (self) -> None:
        """Clicar no botão para confirmar e retornar a tela anterior
        - Esperado o botão ficar invisível"""
        with self.navegador.encontrar(self.BOTAO_CONFIRMAR).aguardar_invisibilidade() as botao:
            botao.clicar()

__all__ = [
    "TabelaRegistro",
    "ModificarDadosRegistro",
]