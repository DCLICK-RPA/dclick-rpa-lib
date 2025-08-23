# externo
import bot
from bot.sistema.janela import ElementoW32

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'CapaNotaFiscal' da janela 'Entrada de Nota Fiscal'")
class AbaCapaNotaFiscal:
    """Representação da aba `CapaNotaFiscal` da janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "CapaNotaFiscal"

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
              .clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA
                      and e.visivel
        )

__all__ = [
    "AbaCapaNotaFiscal",
]