# std
from typing import Self
# externo
import bot
from bot.sistema.janela import ElementoW32

@bot.util.decoradores.prefixar_erro_classe("Falha nas abas 'Situações Especiais / Suframa' da janela 'Interface de Compra'")
class AbaSituacoesEspeciaisSuframa:
    """Representação das abas `Situações Especiais / Suframa` da janela `Interface de Compra`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "SUFRAMA"

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Abrindo a aba 'Situações Especiais / {self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
              .clicar()

        if dialogo := self.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao abrir a aba: '{dialogo.texto}'")

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(lambda e: e.class_name == "TTabSheet"
                                                        and e.texto == "Situações Especiais"
                                                        and e.visivel)\
                                   .encontrar(lambda e: e.class_name == "TTabSheet"
                                                        and e.texto == self.NOME_ABA)

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
        return AbaSituacoesEspeciaisSuframa(self.janela)

    def clicar_botao_alterar_situacoes_especiais (self) -> Self:
        """Clicar no botão `Alterar Situações Especiais`
        - Erro caso apareça diálogo"""
        self.painel_aba.encontrar(lambda e: e.texto == "Alterar Situações Especiais")\
                       .clicar()
        if dialogo := self.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao clicar no botão 'Alterar Situações Especiais': '{dialogo.texto}'")
        return self

__all__ = ["AbaSituacoesEspeciais"]