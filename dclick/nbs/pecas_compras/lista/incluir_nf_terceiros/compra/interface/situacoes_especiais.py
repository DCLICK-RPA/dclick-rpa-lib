"""Módulo para a aba `Situações Especiais`"""

# std
from __future__ import annotations
from typing import Self, Literal
# externo
import bot
from bot.sistema.janela import ElementoW32

@bot.util.decoradores.prefixar_erro_classe("Falha nas abas 'Situações Especiais / Suframa' da janela 'Interface de Compra'")
class AbaSituacoesEspeciaisSuframa:
    """Representação das abas `Situações Especiais / Suframa` da janela `Interface de Compra`"""

    aba: AbaSituacoesEspeciais

    NOME_ABA = "SUFRAMA"

    def __init__ (self, aba: AbaSituacoesEspeciais) -> None:
        bot.logger.informar(f"Abrindo a aba 'Situações Especiais / {self.NOME_ABA}' na janela '{aba.janela.titulo}'")
        self.aba = aba
        self.aba.janela.to_uia()\
                       .elemento\
                       .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
                       .clicar()

        if dialogo := self.aba.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao abrir a aba: '{dialogo.texto}'")

    @property
    def painel_aba (self) -> ElementoW32:
        return self.aba.painel_aba\
            .encontrar(lambda e: e.class_name == "TTabSheet"
                                 and e.texto == self.NOME_ABA)

@bot.util.decoradores.prefixar_erro_classe("Falha nas abas 'Situações Especiais / ICMS' da janela 'Interface de Compra'")
class AbaSituacoesEspeciaisICMS:
    """Representação das abas `Situações Especiais / ICMS` da janela `Interface de Compra`"""

    aba: AbaSituacoesEspeciais

    NOME_ABA = "ICMS"

    def __init__ (self, aba: AbaSituacoesEspeciais) -> None:
        bot.logger.informar(f"Abrindo a aba 'Situações Especiais / {self.NOME_ABA}' na janela '{aba.janela.titulo}'")
        self.aba = aba
        self.aba.janela.to_uia()\
                       .elemento\
                       .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
                       .clicar()

        if dialogo := self.aba.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao abrir a aba: '{dialogo.texto}'")

    @property
    def painel_aba (self) -> ElementoW32:
        return self.aba.painel_aba\
            .encontrar(lambda e: e.class_name == "TTabSheet"
                                 and e.texto == self.NOME_ABA)

    def selecionar_base_icms (self, texto: str | Literal["Considerar desconto sobre item",
                                                         "Não considerar desconto"]) -> Self:
        """Selecionar o `texto` no grupo de opções `Para a Base do ICMS`"""
        self.painel_aba.aguardar()\
            ["Para a Base do ICMS"]\
            [texto]\
            .clicar()
        return self

    def selecionar_modalidade_bc_icms (self, texto: str | Literal["Preço tabelado ou Máximo sugerido",
                                                                  "Valor da Operação"]) -> Self:
        """Selecionar o `texto` no grupo de opções `Modalidade de determinação da BC ICMS`"""
        self.painel_aba.aguardar()\
            ["Modalidade de determinação da BC ICMS"]\
            [texto]\
            .clicar()
        return self

@bot.util.decoradores.prefixar_erro_classe("Falha nas abas 'Situações Especiais / ICMS-ST' da janela 'Interface de Compra'")
class AbaSituacoesEspeciaisIcmsSt:
    """Representação das abas `Situações Especiais / ICMS-ST` da janela `Interface de Compra`"""

    aba: AbaSituacoesEspeciais

    NOME_ABA = "ICMS-ST"

    def __init__ (self, aba: AbaSituacoesEspeciais) -> None:
        bot.logger.informar(f"Abrindo a aba 'Situações Especiais / {self.NOME_ABA}' na janela '{aba.janela.titulo}'")
        self.aba = aba
        self.aba.janela.to_uia()\
                       .elemento\
                       .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
                       .clicar()

        if dialogo := self.aba.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao abrir a aba: '{dialogo.texto}'")

    @property
    def painel_aba (self) -> ElementoW32:
        return self.aba.painel_aba\
            .encontrar(lambda e: e.class_name == "TTabSheet"
                                 and e.texto == self.NOME_ABA)

    def selecionar_base_icms_st (self, texto: str | Literal["Considerar desconto item + Desconto Suframa",
                                                            "Não considerar desconto",
                                                            "Considerar desconto sobre item"]) -> Self:
        """Selecionar o `texto` no grupo de opções `Para a Base do ICMS - ST`"""
        self.painel_aba.aguardar()\
            ["Para a Base do ICMS - ST"]\
            [texto]\
            .clicar()
        return self

    def selecionar_modalidade_bc_icms_st (self, texto: str | Literal["Preço tabelado ou Máximo sugerido",
                                                                     "Margem de valor agregado (MVA)"]) -> Self:
        """Selecionar o `texto` no grupo de opções `Modalidade de determinação da BC ICMS-ST`"""
        self.painel_aba.aguardar()\
            ["Modalidade de determinação da BC ICMS-ST"]\
            [texto]\
            .clicar()
        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Situações Especiais' da janela 'Interface de Compra'")
class AbaSituacoesEspeciais:
    """Representação da aba `Situações Especiais` da janela `Interface de Compra`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Situações Especiais"

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
              .clicar()

        if dialogo := self.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao abrir a aba: '{dialogo.texto}'")

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA
                      and e.visivel
        )

    @property
    def aba_suframa (self) -> AbaSituacoesEspeciaisSuframa:
        """Abrir a aba `SUFRAMA`"""
        return AbaSituacoesEspeciaisSuframa(self)

    @property
    def aba_icms (self) -> AbaSituacoesEspeciaisICMS:
        """Abrir a aba `ICMS`"""
        return AbaSituacoesEspeciaisICMS(self)

    @property
    def aba_icms_st (self) -> AbaSituacoesEspeciaisIcmsSt:
        """Abrir a aba `ICMS-ST`"""
        return AbaSituacoesEspeciaisIcmsSt(self)

    def clicar_botao_alterar_situacoes_especiais (self) -> Self:
        """Clicar no botão `Alterar Situações Especiais`
        - Erro caso apareça diálogo"""
        self.painel_aba.to_uia()\
            .encontrar(lambda e: e.botao and e.visivel and e.texto == "Alterar Situações Especiais")\
            .clicar()
        if dialogo := self.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao clicar no botão 'Alterar Situações Especiais': '{dialogo.texto}'")
        return self

    def clicar_botao_ok (self) -> Self:
        """Clicar no botão `OK`
        - Erro caso apareça diálogo"""
        self.painel_aba.to_uia()\
            .encontrar(lambda e: e.botao and e.visivel and e.texto == "OK")\
            .clicar()
        if dialogo := self.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao clicar no botão 'OK': '{dialogo.texto}'")
        return self

__all__ = ["AbaSituacoesEspeciais"]