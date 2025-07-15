# interno
import re as regex
from datetime import date
from typing import Self, Literal
# externo
import bot
from bot.sistema.janela import ElementoW32, ElementoUIA

@bot.util.decoradores.prefixar_erro("Falha ao abrir o menu 'Incluir Entrada'")
def abrir_menu_incluir_entrada (janela_entrada: bot.sistema.JanelaW32) -> bot.sistema.JanelaW32:
    """Clicar no botão para abrir o menu `Incluir Entrada`
    - Retornado a janela de `Entrada Diversas`"""
    painel = janela_entrada.elemento\
        .sleep()\
        .encontrar(lambda e: e.class_name == "TPageControl")\
        .encontrar(lambda e: e.class_name == "TPanel")
    posicao_botao = painel.coordenada.transformar(0.05, 0.5)
    bot.mouse.clicar_mouse(coordenada=posicao_botao)

    return bot.sistema.JanelaW32(lambda j: "Entrada Diversas" in j.titulo, aguardar=10)

@bot.util.decoradores.prefixar_erro_classe("Falha na janela 'Cálculo de tributos'")
class CalculoTributos:
    """Representação da janela `Cálculo de tributos` da aba `Capa`"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela

    @bot.util.decoradores.prefixar_erro(lambda args, _: f"Falha ao alterar o tributo '{args[0]}'")
    def alterar_tributo (self, nome_tributo: Literal["INSS", "PIS", "CSLL", "COFINS", "IRRF", "ISS Retido"],
                               selecionar: bool = True,
                               imposto: int | float | None = None) -> Self:
        """Alterar o tributo `nome_tributo`
        - `selecionar` para marcar o checkbox
        - `imposto` para alterar o valor do campo imposto
        - Confirmado diálogo de valor divergente, caso apareça"""
        elemento = self.janela.elemento.encontrar(lambda e: e.class_name == "TCheckBox"
                                                            and e.texto.upper() == nome_tributo.upper())
        if elemento.caixa_selecao.selecionado + selecionar == 1: # XOR
            elemento.clicar()

        if imposto is not None:
            assert elemento.parente, "Parente do elemento do checkbox não encontrado"
            elementos = self.janela.ordernar_elementos_coordenada(
                elemento.parente.filhos(lambda e: e.class_name == "TOvcNumericField")
            )
            assert len(elementos) == 2, f"Esperado 2 elementos de input, encontrado '{len(elementos)}'"
            elementos[-1].digitar(str(imposto).replace(".", ","))\
                         .apertar("tab")

        if dialogo := self.janela.dialogo(aguardar=0.2):
            texto = dialogo.elemento.textos().lower()
            assert "divergente" in texto, f"Esperado diálogo de confirmação 'valor divergente' | Encontrado: {texto}"
            assert dialogo.clicar("Sim"), "Falha ao fechar o diálogo de confirmação de valor divergente"

        return self

    def clicar_ok (self) -> None:
        """Clicar em OK para fechar a tela
        - Erro caso apareça diálogo com mensagem ou a janela não feche corretamente"""
        self.janela.elemento\
            .encontrar(lambda e: e.class_name == "TBitBtn" and e.texto.lower() == "ok")\
            .clicar()

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha após clicar em 'OK' na janela 'Cácula de Tributos': '{mensagem}'")

        assert bot.util.aguardar_condicao(lambda: self.janela.fechada, timeout=5),\
            "Janela 'Cácula de Tributos' não foi fechada corretamente"

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Capa' da janela 'Entrada Diversas'")
class AbaCapa:
    """Representação da aba `Capa` na janela `Entrada Diversas`"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == "Capa" and e.item_aba)\
              .clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == "Capa"
        )

    @property
    def painel_nota_fiscal (self) -> ElementoW32:
        return self.painel_aba.encontrar(
            lambda e: e.class_name == "TGroupBox"
                      and e.texto == "Nota Fiscal"
        )

    @property
    def painel_valores_nota (self) -> ElementoW32:
        return self.painel_aba\
            .encontrar(lambda e: e.class_name == "TTabSheet" and e.texto == "Valores da Nota")\
            .encontrar(lambda e: e.class_name == "TGroupBox")

    def preencher_cnpj_cpf_fornecedor (self, texto: str) -> Self:
        """Preencher o campo `CNPJ/CPF` e apertado `TAB` para confirmar
        - Erro caso apareça diálogo com mensagem"""
        self.painel_aba\
            .encontrar(lambda e: e.texto == "Fornecedor")\
            .encontrar(lambda e: e.class_name == "TCPF_CGC")\
            .apertar("backspace")\
            .digitar(texto)\
            .apertar("enter")

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao preencher o cnpj/cpf '{texto}': '{mensagem}'")

        return self

    def preencher_numero_nota_fiscal (self, numero: str) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_nota_fiscal.filhos()
        )
        assert len(elementos) >= 1, "Elemento não foi encontrado"

        elementos[1]\
            .digitar(numero)\
            .apertar("tab")
        return self

    def preencher_serie_nota_fiscal (self, serie: str) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_nota_fiscal.filhos()
        )
        assert len(elementos) >= 2, "Elemento não foi encontrado"

        elementos[2]\
            .digitar(serie)\
            .apertar("tab")
        return self

    def preencher_emissao_nota_fiscal (self, data: date) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_nota_fiscal.filhos()
        )
        assert len(elementos) >= 3, "Elemento não foi encontrado"

        elementos[3]\
            .digitar(data.strftime(r"%d%m%Y"))\
            .apertar("tab")
        return self

    def preencher_entrada_nota_fiscal (self, data: date) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_nota_fiscal.filhos()
        )
        assert len(elementos) >= 4, "Elemento não foi encontrado"

        elementos[4]\
            .digitar(data.strftime(r"%d%m%Y"))\
            .apertar("tab")
        return self

    def alterar_estado_nota_no_livro_fiscal (self, selecionar=False) -> Self:
        caixa = self.painel_aba\
            .encontrar(lambda e: e.class_name == "TCheckBox" and "livro fiscal" in e.texto.lower())\
            .caixa_selecao

        # XOR, apenas 1 True
        if caixa.selecionado + selecionar == 1: 
            caixa.alternar()

        return self

    def preencher_base_iss_valores_nota (self, base_iss: int | float) -> Self:
        painel = self.painel_valores_nota.focar()
        elementos = self.janela.ordernar_elementos_coordenada(
            painel.filhos(lambda e: e.class_name == "TOvcDbPictureField")
        )
        assert len(elementos) >= 7, "Elemento não foi encontrado"

        elementos[7]\
            .apertar("backspace")\
            .digitar(str(base_iss).replace(".", ","))\
            .apertar("tab")
        return self

    def preencher_aliquota_iss_valores_nota (self, aliquota_iss: int | float) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_valores_nota.filhos(lambda e: e.class_name == "TOvcDbPictureField")
        )
        assert len(elementos) >= 8, "Elemento não foi encontrado"

        elementos[8]\
            .apertar("backspace")\
            .digitar(str(aliquota_iss).replace(".", ","))\
            .apertar("tab")
        return self

    def obter_valor_iss_valores_nota (self) -> float:
        """Obtero valor atual do `Valor ISS`"""
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_valores_nota.filhos(lambda e: e.class_name == "TOvcDbPictureField")
        )
        assert len(elementos) >= 9, "Elemento não foi encontrado"

        valor = elementos[9].to_uia().texto
        return float(valor.replace(",", "."))

    def preencher_valor_iss_valores_nota (self, valor_iss: int | float) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_valores_nota.filhos(lambda e: e.class_name == "TOvcDbPictureField")
        )
        assert len(elementos) >= 9, "Elemento não foi encontrado"

        elementos[9]\
            .apertar("backspace")\
            .digitar(str(valor_iss).replace(".", ","))\
            .apertar("tab")
        return self

    def preencher_codigo_servico_prefeitura_valores_nota (self, codigo: str) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_valores_nota.filhos(lambda e: e.class_name == "TOvcDbPictureField")
        )
        assert len(elementos) >= 11, "Elemento não foi encontrado"

        elementos[11].apertar("backspace").digitar(codigo).apertar("tab")
        return self

    def preencher_total_nota_valores_nota (self, total: int | float) -> Self:
        """Preencher o campo `Total Nota` e apertado `TAB` para confirmar
        - Erro caso apareça diálogo com mensagem"""
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_valores_nota.filhos(lambda e: e.class_name == "TOvcDbPictureField")
        )
        assert len(elementos) >= 12, "Elemento não foi encontrado"

        elementos[12].apertar("backspace")\
                     .digitar(str(total).replace(".", ","))\
                     .apertar("enter")

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao preencher o total nota '{total}': '{mensagem}'")

        return self

    def alterar_estado_fisco_municipal_valores_nota (self, selecionar=True) -> Self:
        caixa = self.painel_valores_nota\
            .encontrar(lambda e: e.class_name == "TDBCheckBox" and e.texto == "Fisco Municipal")\
            .caixa_selecao

        # XOR, apenas 1 True
        if caixa.selecionado + selecionar == 1: 
            caixa.alternar()

        return self

    def preencher_observacao_operacao (self, texto: str) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(self.painel_aba.filhos())
        assert elementos, "Elemento não foi encontrado"
        elementos[-1].encontrar(lambda e: e.class_name == "TOvcDbPictureField")\
                     .digitar(texto)\
                     .apertar("tab")
        return self

    @bot.util.decoradores.prefixar_erro("Falha ao abrir a janela de 'Calculo de Tributos'")
    def abrir_janela_calculo_tributos (self) -> CalculoTributos:
        """Clicar para abrir a janela 'Calculo de Tributos'
        - Retornado classe para tratar janela
        - Fechar a janela após realizar alterações"""
        posicao = self.painel_valores_nota\
            .coordenada\
            .transformar(0.3, 0.06)
        bot.mouse.clicar_mouse(coordenada=posicao)

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(mensagem)

        return CalculoTributos(
            self.janela.janela_processo(lambda j: j.class_name == "TfrmCalculoTributos", aguardar=5)
                       .focar()
        )

    def preencher_cod_retencao_valores_nota (self, codigo: str) -> Self:
        painel = self.painel_valores_nota.focar()
        assert painel.parente

        elementos = self.janela.ordernar_elementos_coordenada(
            painel.parente.filhos(lambda e: e.class_name == "TOvcDbPictureField")
        )
        assert len(elementos) >= 1, "Elemento não foi encontrado"

        elementos[0]\
            .apertar("backspace")\
            .digitar(codigo)\
            .apertar("tab")
        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Contabilização' da janela 'Entrada Diversas'")
class AbaContabilizacao:
    """Representação da aba `Contabilização` na janela `Entrada Diversas`"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == "Contabilização" and e.item_aba)\
              .clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == "Contabilização"
        )

    @property
    def painel_contabilizacao_padrao (self) -> ElementoW32:
        return self.painel_aba.encontrar(
            lambda e: e.class_name == "TGroupBox"
                      and e.texto == "Contabilização Padrão"
        )

    def preencher_codigo_contabilizacao_padrao (self, codigo: str) -> Self:
        self.painel_contabilizacao_padrao\
            .encontrar(lambda e: e.class_name == "TOvcNumericField")\
            .digitar(codigo)\
            .apertar("tab")
        return self

    def confirmar_contabilizacao_padrao (self) -> Self:
        """Clicar no botao de raio para confirmar a `Contabilização Padrão`
        - Erro caso apareça diálogo com mensagem"""
        posicao_botao = self.painel_contabilizacao_padrao\
                            .coordenada\
                            .transformar(0.96, 0.65)
        bot.mouse.clicar_mouse(coordenada=posicao_botao)

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao confirmar a contabilização padrão: '{mensagem}'")

        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Faturamento' da janela 'Entrada Diversas'")
class AbaFaturamento:
    """Representação da aba `Faturamento` na janela `Entrada Diversas`"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == "Faturamento" and e.item_aba)\
              .clicar()

    @property
    def painel_aba (self) -> ElementoUIA:
        return self.janela.to_uia().elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == "Faturamento"
        )

    @property
    def painel_condicao_pagamento (self) -> ElementoUIA:
        return self.janela.to_uia().elemento.encontrar(
            lambda e: e.class_name == "TGroupBox"
                      and e.texto == "Condição de Pagamento"
        )

    @property
    def painel_alteracao_parcelas (self) -> ElementoUIA:
        return self.janela.to_uia().elemento.encontrar(
            lambda e: e.class_name == "TGroupBox"
                      and e.texto == "Alteração das Parcelas"
        )

    def selecionar_tipo_pagamento (self, descricao: str) -> Self:
        elemento = self.painel_aba\
            .encontrar(lambda e: e.texto == "Tipo de Pagamento")\
            .encontrar(lambda e: e.class_name == "TwwDBLookupCombo")\
            .clicar()\
            .digitar(descricao, virtual=False)\
            .apertar("enter")\
            .sleep(0.5)

        valor = elemento.valor
        assert valor.upper() == descricao.upper(), f"Falha ao preencher o tipo de pagamento | Esperado '{descricao}' | Encontrado '{valor}'"
        return self

    def selecionar_natureza_despesa (self, descricao: str) -> Self:
        elemento = self.painel_aba\
            .encontrar(lambda e: e.texto == "Natureza Despesa")\
            .encontrar(lambda e: e.class_name == "TwwDBLookupCombo")\
            .clicar()\
            .digitar(descricao, virtual=False)\
            .apertar("enter")\
            .sleep(0.5)

        valor = elemento.valor
        assert valor.upper() == descricao.upper(), f"Falha ao preencher a naturaza da despesa | Esperado '{descricao}' | Encontrado '{valor}'"
        return self

    def preencher_total_parcelas_condicao_pagamento (self, parcelas: str) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_condicao_pagamento.filhos(lambda e: e.class_name == "TOvcNumericField")
        )
        assert len(elementos) >= 3, "Elemento não foi encontrado"
        elementos[2].digitar(parcelas).apertar("tab")
        return self

    def clicar_gerar_condicao_pagamento (self) -> Self:
        """Clicar no botao `Gerar` para confirmar a `Condição de Pagamento`
        - Erro caso apareça diálogo com mensagem"""
        posicao_botao = self.painel_condicao_pagamento\
                            .coordenada\
                            .transformar(0.8, 0.4)
        bot.mouse.clicar_mouse(coordenada=posicao_botao)

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao confirmar a condição de pagamento: '{mensagem}'")

        return self

    def preencher_vencimento_alteracao_parcelas (self, vencimento: date) -> Self:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_alteracao_parcelas.filhos(lambda e: e.class_name == "TOvcDbPictureField")
        )
        assert len(elementos) >= 1, "Elemento não foi encontrado"
        elementos[1].apertar("backspace")\
                    .digitar(vencimento.strftime(r"%d%m%Y"))\
                    .apertar("tab")
        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Retenções PJ' da janela 'Entrada Diversas'")
class AbaRetencoesPJ:
    """Representação da aba `Retenções PJ` na janela `Entrada Diversas`"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        try: janela.to_uia()\
                   .elemento\
                   .encontrar(lambda e: e.texto == "Retenções PJ" and e.item_aba)\
                   .clicar()
        except Exception:
            raise Exception("Falha ao abrir a aba 'Retenções PJ'")

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == "Retenções PJ"
        )

    @property
    def janela_retencoes_pj (self) -> bot.sistema.JanelaUIA:
        """Janela `Retenções PJ` aberta após utilizar o `clicar_incluir()`"""
        return self.janela.janela_processo(lambda j: j.titulo == "Retenções PJ", aguardar=5)\
            .focar()\
            .to_uia()

    @bot.util.decoradores.prefixar_erro("Falha ao abrir a janela interna 'Retenções PJ'")
    def clicar_incluir (self) -> Self:
        """Clicar no botão verde `+` para incluir
        - Necessário para abrir a `janela_retencoes_pj`
        - TODO Posição alterada do botão após o primeiro click"""
        posicao = self.painel_aba\
            .encontrar(lambda e: e.texto == "pnlBtnAcoesPJGeral")\
            .coordenada\
            .transformar(yOffset=0.09)
        bot.mouse.clicar_mouse(coordenada=posicao)

        self.janela_retencoes_pj
        return self

    def alterar_codigo_natureza (self, codigo: str) -> Self:
        elemento = self.janela_retencoes_pj\
            .elemento\
            .encontrar(lambda e: e.class_name == "TwwDBLookupCombo")\
            .clicar()\
            .digitar(codigo, virtual=False)\
            .sleep(2)\
            .apertar("tab")\
            .sleep(0.5)

        valor = elemento.valor
        assert codigo.lower() in valor.lower(),\
            f"Falha ao preencher o código da natureza | Esperado '{codigo}' | Encontrado '{valor}'"
        return self

    def clicar_gravar (self) -> Self:
        """Clicar no botão `Gravar`
        - Erro caso apareça diálogo com mensagem"""
        self.janela_retencoes_pj\
            .elemento\
            .encontrar(lambda e: e.texto.lower() == "gravar" and e.class_name == "TNBSWButton")\
            .clicar()

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao clicar para gravar na aba 'Retenções PJ': '{mensagem}'")

        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na confirmação da janela 'Entrada Diversas'")
class Confirmar:
    """Representação do processo de Confirmação na janela 'Entrada Diversas'"""

    full_hd: bool
    janela: bot.sistema.JanelaW32

    IMAGEM_CONFIRMAR = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEsAAAAdCAYAAADimZEAAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGmSURBVGhD7ZaBlYMgDEDZiW1Yho7CAg7BKE7CEQQMGNR4tvfORt9vAWOMX6RV0zQF4RjY1DzPQdhHZDEQWQxEFgORxeBWWSru1PhTuE0WiFKvBer4E7hFFhal1IuMeQK/ltWIEllj+KJ8sBriFoyjYs6y5jLWBq1t8GTcfVyWFcu8JEpbn/suGKWD9X3cSfxnBGEuyeKLihA3572L5LbVdcZVoXCOMVHqMq6My+eC6DymTHAld/qO8WnGlfHSh7yuzsZyDXzdmr/Pk665IyuGNX08zhYFOINutgOKq0WhGbcZXwtv5Jd2ikezFff7dpVbHiDK3+fJkLKqkLiT41xRwJ6s7pgzeT1rbgZe404EJavGD2KodplZvcySJ0PLwkKysNTC4xxRwKCAxF/JguuOZjTOk6FlRRGNmF4UwJVFLvC5D8UdFv0mWeUhJXEXZAEbYRi2qMIiqCyoq7h2oa1/KZqi3/EaonryD8l2Rq8MZQGksMui/j+7soBG2BeLAg5lAUnYl4sCTskSFkQWA5HFQGQxEFkMRBaDKgsawjFJVvqU7cQWwg8Fw9KgLVft2wAAAABJRU5ErkJggg==")
    """Imagem do botão `Confirmar` na resolução `1920x1080`"""
    IMAGEM_CANCELAR = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEQAAAAXCAYAAACyCenrAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGmSURBVFhH7ZQ9ksIwDIV9J2Yyw10oUuQg6ag4BS1dzkCdkhNwgK1TeC1HCpYsO94MFGRdfAPRj+X3Ysc8fyZbeVENEVRDBJsMscbY3gG/Wv6bUQ0hwbkcodV8M5EhTHDfp3NKfg/kDQlEbzPjYfvGuNaZ002r+QDjxR6ai71ruRWyVyYUL5+1Ps5sxuH8wOfBnszR9qOs+wDvNgSITCFKr4myqfs4OPD/+bicHNMOr562c8aJOOUobjp7pfit09fB2ck5jZvjT2+wliNpCOCqtxsCGw0FhTCz4OTgprxo2mAQF6fLi4S12TqTvbZ4LSmenaOf1qwhkRnvMgTwm8I3R5tjAuDKafGA8HQg/oqG9atzOH+/MkCJKZmhsxDl7bOeQkM006m+aA6n7KOqsWqK9lHF51CI3/SKIeLK+B6og/olPs9jV6ZoDicyRDXDiY9iGJf9nNkEdpxlHD+iTIivCQ3BHPUsb93hhdJaKH5Zp2QOhxniOpOic7k9kTdECGb5HZoBpA1JCPY1OzUDiL4hIHbPgteIDPnvVEME1RBBNURQDWFM9hfM9zt0FZHS5AAAAABJRU5ErkJggg==")
    """Imagem do botão `Cancelar` na resolução `1920x1080`"""

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        resolucao_atual, _ = bot.sistema.informacoes_resolucao()
        self.full_hd = resolucao_atual == (1920, 1080)

    @property
    def painel_botao_confirmar (self) -> ElementoW32:
        e = self.janela.elemento.encontrar(lambda e: e.texto.lower() == "dados")
        painel = e.filhos(lambda e: e.class_name == "TPanel")
        assert painel, "Painel com o botão 'Confirmar' não foi encontrado"
        return painel[0]

    def clicar_confirmar_via_imagem (self) -> Self:
        """Clicar no botão `Confirmar` procurando pela Imagem
        - Esperado resolução `1920x1080`"""
        assert self.full_hd, "Esperado resolução '1920x1080' para encontrar a imagem do botão 'Confirmar'"

        coordenada = self.IMAGEM_CONFIRMAR.procurar_imagem(
            regiao = self.painel_botao_confirmar.coordenada,
            segundos = 5
        )
        assert coordenada, "Imagem do botão 'Confirmar' não foi encontrada"
        bot.mouse.clicar_mouse(coordenada=coordenada)

        return self

    def confirmar_dialogo_data_barreira (self) -> Self:
        """Checar pelo diálogo `Data de Barreira` e clicar em `Sim` caso apareça"""
        dialogo = self.janela.dialogo(aguardar=5)
        if not dialogo: return self

        texto = dialogo.elemento.textos().lower()
        if "data de barreira" not in texto: return self

        assert dialogo.clicar("Sim"), "Diálogo 'Data de Barreira' não fechou conforme esperado"
        return self

    def dialogo_aviso_nfe (self) -> str:
        """Diálogo `Aviso NF-e`, retornado o número de controle e clicado em `OK`"""
        dialogo = self.janela.dialogo(aguardar=5)
        assert dialogo, "Diálogo 'Aviso NF-e' não encontrado"

        texto = dialogo.elemento.textos().lower()
        assert "controle" in texto, "Mensagem do diálogo 'Aviso NF-e' não está de acordo com o esperado"

        match = regex.search(r"\d+", texto)
        assert match, "Mensagem do diálogo 'Aviso NF-e' não está de acordo com o esperado"

        assert dialogo.clicar("OK"), "Diálogo 'Aviso NF-e' não fechou conforme esperado"
        return match.group()

    def fechar_janela_ficha_controle_pagamento_via_imagem (self) -> None:
        """Fechar a janela 'Ficha de Controle de Pagamento'"""
        assert self.full_hd, "Esperado resolução '1920x1080' para encontrar a imagem do botão 'Cancelar'"

        titulo = 'Ficha de Controle de Pagamento'
        try: janela = self.janela.janela_processo(lambda j: j.titulo == titulo).focar()
        except Exception:
            raise Exception(f"Janela '{titulo}' não foi encontrada")

        coordenada = self.IMAGEM_CANCELAR.procurar_imagem(
            regiao = janela.elemento.coordenada,
            segundos = 5
        )
        assert coordenada, f"Coordenada do botão 'Cancelar' não encontrado na janela '{titulo}'"

        bot.mouse.clicar_mouse(coordenada=coordenada)
        assert bot.util.aguardar_condicao(lambda: janela.fechada, timeout=5),\
            f"Janela '{titulo}' não foi fechada corretamente"

__all__ = [
    "AbaCapa",
    "Confirmar",
    "AbaFaturamento",
    "AbaRetencoesPJ",
    "AbaContabilizacao",
    "abrir_menu_incluir_entrada"
]