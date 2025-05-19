# std
from __future__ import annotations
import typing
# interno
import dclick
# externo
import bot

NOME_MENU = "Nota Fiscal de Item Avulso"

class Localizadores:
    # Importar
    BOTAO_IMPORTAR_NFE      = "#IMAGE1"
    BOTAO_PROCURAR_NFE      = "#IMAGE2"
    IFRAME_UPLOAD           = "#gxp0_ifrm"
    BOTAO_UPLOAD_ARQUIVOS   = "#uploadfiles"
    BOTAO_CONFIRMAR_UPLOAD  = "#TRN_ENTER"
    BOTAO_FECHAR_UPLOAD     = "#TRN_CANCEL"
    MENSAGEM_STATUS_UPLOAD  = "#TEXTBLOCKDOWNLOAD"
    MENSAGEM_ERRO           = ".ErrorViewer"

def importar_nfe (navegador: bot.navegador.Edge, *nfe: bot.estruturas.Caminho) -> None:
    """Importar todas as `nfe` em `["XML - Importação", "Nota Fiscal de Item Avulso"]`"""
    quantidade = len(nfe)
    bot.logger.informar(f"Importando '{quantidade}' NFe(s) de item avulso")
    assert quantidade >= 1, "Pelo menos 1 NFe deve ser informada"
    assert all(n.existe() for n in nfe), f"Algum caminho da NFe não foi encontrado\n\t{nfe}"

    dclick.dealernet.menus.selecionar_opcao_menu(
        navegador,
        ["XML - Importação", NOME_MENU],
        dclick.dealernet.menus.Menus.INTEGRACAO,
    )

    dclick.dealernet.menus.acessar_iframe_janela_menu(navegador, NOME_MENU)
    navegador.encontrar(Localizadores.BOTAO_IMPORTAR_NFE).clicar()
    navegador.encontrar(Localizadores.BOTAO_PROCURAR_NFE).clicar()

    with navegador.encontrar(Localizadores.IFRAME_UPLOAD).aguardar_invisibilidade() as iframe_upload:
        caminhos = "\n".join(n.string for n in nfe)
        navegador.alterar_frame(iframe_upload)\
                 .encontrar(Localizadores.BOTAO_UPLOAD_ARQUIVOS)\
                 .digitar(caminhos)

    dclick.dealernet.menus.acessar_iframe_janela_menu(navegador, NOME_MENU)
    navegador.encontrar(Localizadores.BOTAO_CONFIRMAR_UPLOAD).clicar()
    status = navegador.encontrar(Localizadores.MENSAGEM_STATUS_UPLOAD)\
                      .aguardar_visibilidade()

    try: assert f"{quantidade} de {quantidade}" in status.texto.lower()
    except Exception as e:
        erro = " | ".join(e.texto for e in navegador.procurar(Localizadores.MENSAGEM_ERRO))
        e.add_note(f"Mensagem de status do upload não está de acordo com o esperado\n\t{erro}")
        raise

    navegador.encontrar(Localizadores.BOTAO_FECHAR_UPLOAD).clicar()
    bot.logger.informar(f"NFe(s) importada(s) com sucesso")

class DadosRegistro:

    codigo: str
    cliente: str
    data_emissao: str
    nota_fiscal: str
    usuario: str
    nome_arquivo: str
    valor: str
    status: str

    def __eq__ (self, value: object) -> bool:
        return isinstance(value, type(self)) and self.codigo == value.codigo

    def __getattr__ (self, name: str) -> str:
        return ""

    def __repr__ (self) -> str:
        return f"<{type(self).__name__} {self.__dict__}>"

class TabelaRegistro:
    """Classe especializada para obter e filtrar os registros na tabela
    - Acessado iframe do menu da janela"""

    navegador: bot.navegador.Edge

    TABELA_REGISTROS            = "#GridintxmlContainerTbl"
    TABELA_FILTRO_REGISTROS     = "#TABLENF"
    INPUT_FILTRO_CODIGO         = "#vINTEGRACAOXMLNF_CODIGO"
    INPUT_FILTRO_USUARIO        = "#vUSUARIO_NOME"
    INPUT_FILTRO_NUMERO_NF      = "#vINTEGRACAOXMLNF_NUMERONF"
    INPUT_FILTRO_DATA_INICIAL   = "#vINTEGRACAOXMLNF_DATAEMISSAOINICIAL"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        dclick.dealernet.menus.selecionar_opcao_menu(
            navegador,
            ["XML - Importação", NOME_MENU],
            dclick.dealernet.menus.Menus.INTEGRACAO,
        )
        dclick.dealernet.menus.acessar_iframe_janela_menu(navegador, NOME_MENU)

    def filtrar (
            self,
            codigo: str | None = None,
            usuario: str | None = None,
            numero_nf: str | None = None,
        ) -> typing.Self:
        """Aplicar o filtro na tabela dos registros
        - Campo da `data_inicial` limpo"""
        itens: list[tuple[str | None, str]] = [
            (codigo,    self.INPUT_FILTRO_CODIGO),
            (usuario,   self.INPUT_FILTRO_USUARIO),
            (numero_nf, self.INPUT_FILTRO_NUMERO_NF),
            ("",        self.INPUT_FILTRO_DATA_INICIAL)
        ]

        with self.navegador.encontrar(self.TABELA_REGISTROS).aguardar_staleness() as tabela_registros:
            tabela_filtro = self.navegador.encontrar(self.TABELA_FILTRO_REGISTROS)

            for texto, localizador in itens:
                if texto == None: continue
                tabela_filtro.encontrar(localizador).limpar().digitar(texto)

            tabela_registros.hover().sleep(0.5)

        return self

    @bot.util.decoradores.retry(tentativas=2)
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

class AtualizarDadosRegistro:
    """Classe para tratar a atualização dos dados de um registro
    - `clicar_atualizar_dados(registro)` para iniciar a atualização
    - `clicar_botao_processar_atualizacao()` retorna classe para tratar o processamento dos dados do item avulso"""

    navegador: bot.navegador.Edge

    BOTAO_ATUALIZAR_DADOS_REGISTRO  = "tbody > tr:nth-child(1) > td > a:has(> img[title *= 'atualizar' i])"
    # Usado `nth-child(1)` pois é feito o filtro pelo código do registro, logo esperado apenas 1
    INPUT_SELECAO_ITEM_AVULSO       = "#vITEMAVULSO_CODIGO"
    BOTAO_ATUALIZAR_SELECAO         = "#CONFIRM"
    BOTAO_CONFIRMAR_ATUALIZACAO     = "#BTNCONFIRMAR"
    BOTAO_PROCESSAR_ATUALIZACAO     = "#BTNPROCESSAR"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        bot.logger.informar("Iniciando atualização dos dados")

    def clicar_atualizar_dados (self, registro: DadosRegistro) -> typing.Self:
        """Clicar para atualizar os dados do item avulso para o `registro`
        - Abre a tela de atualização
        - Feito o filtro do registro automaticamente"""
        TabelaRegistro(self.navegador).filtrar(registro.codigo)

        with self.navegador.encontrar(TabelaRegistro.TABELA_REGISTROS).aguardar_staleness() as tabela_registros:
            tabela_registros.encontrar(self.BOTAO_ATUALIZAR_DADOS_REGISTRO).clicar()

        return self

    def preencher_selecao_item_avulso (self, codigo: str) -> typing.Self:
        """Preencer o campo `Seleção Item Avulso` com o `código`"""
        self.navegador.encontrar(self.INPUT_SELECAO_ITEM_AVULSO)\
            .limpar()\
            .digitar(codigo, bot.navegador.Teclas.TAB)
        return self

    def clicar_botao_atualizar_selecao (self) -> typing.Self:
        """Clicar no botão `Atualizar`"""
        self.navegador.encontrar(self.BOTAO_ATUALIZAR_SELECAO).clicar()
        return self

    def clicar_botao_confirmar_atualizacao (self) -> typing.Self:
        """Clicar no botão `Confirmar`"""
        self.navegador.encontrar(self.BOTAO_CONFIRMAR_ATUALIZACAO).clicar()
        return self

    def clicar_botao_processar_atualizacao (self) -> ProcessarDadosRegistro:
        """Clicar no botão `Processar`
        - Abre a tela de processamento
        - Retorna a classe para tratamento do processamento"""
        self.navegador.encontrar(self.BOTAO_PROCESSAR_ATUALIZACAO).clicar()
        return ProcessarDadosRegistro(self.navegador)

class ProcessarDadosRegistro:
    """Classe para tratar o processamento dos dados de um registro
    - `AtualizarDadosItemAvulso` para iniciar o processamento"""

    navegador: bot.navegador.Edge

    # Tipo Documento
    BOTAO_TIPO_DOCUMENTO                = "#TIPODOC"
    IFRAME_SELECAO_TIPO_DOCUMENTO       = Localizadores.IFRAME_UPLOAD
    BOTAO_CONFIRMAR_TIPO_DOCUMENTO      = "#CONFIRMAR"
    # Natureza Operação
    BOTAO_NATUREZA_OPERACAO             = "#NATOPE"
    IFRAME_SELECAO_NATUREZA_OPERACAO    = IFRAME_SELECAO_TIPO_DOCUMENTO
    BOTAO_CONFIRMAR_NATUREZA_OPERACAO   = BOTAO_CONFIRMAR_TIPO_DOCUMENTO
    # Conta Gerencial
    BOTAO_CONTA_GERENCIAL               = "#IMGPROMPTCG"
    IFRAME_SELECAO_CONTA_GERENCIAL      = IFRAME_SELECAO_TIPO_DOCUMENTO
    BOTAO_FILTRO_TIPO_TODOS             = "input[type='radio']:last-of-type"
    INPUT_IDENTIFICADOR_CONTA_GERENCIAL = "#vCONTAGERENCIAL_IDENTIFICADOR"
    TABELA_SELECAO_CONTA_GERENCIAL      = "#GridContainerTbl"
    # Departamento
    SELECAO_DEPARTAMENTO                = "#vNOTAFISCAL_DEPARTAMENTOCOD"
    # Condição Pagamento
    SELECAO_CONDICAO_PAGAMENTO          = "#vNOTAFISCAL_CONDICAOPAGAMENTOCOD"
    # Agente Cobrado
    SELECAO_AGENTE_COBRADOR             = "#vAGENTECOBRADOR_CODIGO"

    BOTAO_PROCESSAR                     = "#IMGPROCESSAR"
    MENSAGEM_SUCESSO_E_ERRO             = ".ErrorViewer"
    BOTAO_FECHAR                        = "#TRN_CANCEL"

    def __init__ (self, navegador: bot.navegador.Edge) -> None:
        self.navegador = navegador
        bot.logger.informar("Iniciando processamento dos dados")

    def selecionar_natureza_operacao (self, texto: str) -> typing.Self:
        """Selecionar a natureza da operação com o `texto`"""
        self.navegador.encontrar(self.BOTAO_NATUREZA_OPERACAO).clicar()

        with self.navegador.encontrar(self.IFRAME_SELECAO_NATUREZA_OPERACAO)\
                           .aguardar_invisibilidade() as iframe:
            self.navegador.alterar_frame(iframe)\
                          .encontrar("select")\
                          .select\
                          .select_by_visible_text(texto)
            self.navegador.encontrar(self.BOTAO_CONFIRMAR_NATUREZA_OPERACAO)\
                          .clicar()

        dclick.dealernet.menus.acessar_iframe_janela_menu(self.navegador, NOME_MENU)
        return self

    def selecionar_tipo_documento (self, texto: str) -> typing.Self:
        """Selecionar o tipo de documento com o `texto`"""
        self.navegador.encontrar(self.BOTAO_TIPO_DOCUMENTO).clicar()

        with self.navegador.encontrar(self.IFRAME_SELECAO_TIPO_DOCUMENTO)\
                           .aguardar_invisibilidade() as iframe:
            self.navegador.alterar_frame(iframe)\
                          .encontrar("select")\
                          .select\
                          .select_by_visible_text(texto)
            self.navegador.encontrar(self.BOTAO_CONFIRMAR_TIPO_DOCUMENTO)\
                          .clicar()

        dclick.dealernet.menus.acessar_iframe_janela_menu(self.navegador, NOME_MENU)
        return self

    def selecionar_conta_gerencial (self, identificador: str) -> typing.Self:
        """Selecionar a conta gerencial de acordo com o `identificador`"""
        self.navegador.encontrar(self.BOTAO_CONTA_GERENCIAL).clicar()

        iframe = self.navegador.encontrar(self.IFRAME_SELECAO_CONTA_GERENCIAL)
        self.navegador.alterar_frame(iframe)
        tabela = self.navegador.encontrar(self.TABELA_SELECAO_CONTA_GERENCIAL)

        with tabela.aguardar_staleness():
            self.navegador.encontrar(self.BOTAO_FILTRO_TIPO_TODOS)\
                          .clicar()
            self.navegador.encontrar(self.INPUT_IDENTIFICADOR_CONTA_GERENCIAL)\
                          .limpar()\
                          .digitar(identificador)

        with iframe.aguardar_invisibilidade():
            localizador_botao = f"""./tbody/tr[contains(., "{identificador}")]//input"""
            tabela.encontrar(localizador_botao).clicar()

        dclick.dealernet.menus.acessar_iframe_janela_menu(self.navegador, NOME_MENU)
        return self

    def selecionar_departamento (self, texto: str) -> typing.Self:
        """Selecionar o departamento de acordo com o `texto`"""
        self.navegador.encontrar(self.SELECAO_DEPARTAMENTO)\
            .select\
            .select_by_visible_text(texto)
        return self

    def selecionar_condicao_pagamento (self, texto: str) -> typing.Self:
        """Selecionar a condição de pagamento de acordo com o `texto`"""
        self.navegador.encontrar(self.SELECAO_CONDICAO_PAGAMENTO)\
            .select\
            .select_by_visible_text(texto)
        return self

    def selecionar_agente_cobrador (self, texto: str) -> typing.Self:
        """Selecionar o agente cobrador de acordo com o `texto`"""
        self.navegador.encontrar(self.SELECAO_AGENTE_COBRADOR)\
            .select\
            .select_by_visible_text(texto)
        return self

    def capturar_mensagens (self) -> str:
        """Capturar as mensagens de sucesso e erro"""
        return "; ".join(
            elemento.texto
            for elemento in self.navegador.procurar(self.MENSAGEM_SUCESSO_E_ERRO)
            if elemento.visivel
        )

    def clicar_botao_processar (self) -> str:
        """Clicar no botão Processar e retornar o resultado do `self.capturar_mensagens()`"""
        mensagem = self.capturar_mensagens()
        self.navegador.encontrar(self.BOTAO_PROCESSAR).clicar()
        bot.util.aguardar_condicao(
            lambda: mensagem != self.capturar_mensagens(),
            timeout = 15,
            delay = 0.5
        )
        return self.capturar_mensagens()

    def clicar_botao_fechar (self) -> typing.Self:
        """Clicar no botão Fechar"""
        with self.navegador.encontrar(self.BOTAO_FECHAR).aguardar_staleness() as botao:
            botao.clicar()
        return self

__all__ = [
    "importar_nfe",
    "TabelaRegistro",
    "AtualizarDadosRegistro",
]