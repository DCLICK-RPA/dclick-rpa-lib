# interno
from .incluir_nf_terceiros import OpcoesInclusaoNfTerceiros
# externo
import bot
from bot.sistema.janela import ElementoW32

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Lista' da janela 'Compras'")
class AbaLista:
    """Representação da aba `Lista` na janela `Compras`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Lista"
    IMAGEM_INCLUIR_NF_TERCEIROS = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAcCAIAAABUG4BXAAABMklEQVRYCdXBQXIaUQBEsX73P7RC/dVgHGI2To0UdhNhNxF2E2E3EXYTYTcR9qFqB/aLwt6qsatqB/aLwt6qPbD/Luyi9gZb7YG9qLCfqbAXFfadsIvaG2y1B/aiwn6mwj4R9lbtgf1Thf1MhX0i7K0a+6Lahl1U2Fah2oYd1Q5sq1BhR4UK1TbsIuxz1TbsosK2ahu2Vaiwo0KFCjsqVKiwZ2Gvag/sExW2VdhRocIuKlTYUaFChT0Le1V7YH9RbcMuKmyrsKNChV1UqLCjQoUKexZ2VfuCvai2YRcVtlXYUaHCjgoVKmyrtqFChT0Lu6p9wX6mwrYKOypsq3ZgW4Vt1TZUqFBhz8Je1R7Yd6od2C8Ke1V7YN+pdmC/KOwmwm4i7CbCbiLsJsJuIuwmwm7iD3atRNj/aR7WAAAAAElFTkSuQmCC")
    """Imagem do botão `Incluir` na resolução `1920x1080`"""

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

    def clicar_botao_incluir_nf_terceiros_via_imagem (self) -> OpcoesInclusaoNfTerceiros:
        """Clicar no botão `Incluir` para incluir nota fiscal emitida por terceiro
        - Retornado clase para tratar a sub-janela aberta"""
        regiao = self.painel_aba.coordenada
        coordenada = self.IMAGEM_INCLUIR_NF_TERCEIROS.procurar_imagem(regiao=regiao, cinza=True, segundos=3)
        assert coordenada, "Imagem do botão 'Incluir' não foi encontrado"
        bot.mouse.mover(coordenada).clicar()
        return OpcoesInclusaoNfTerceiros(self.janela)

__all__ = [
    "AbaLista",
]