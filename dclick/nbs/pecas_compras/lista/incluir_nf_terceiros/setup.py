# externo
import bot

@bot.util.decoradores.prefixar_erro_classe("Falha na janela de seleção para incluir nota fiscal de terceiros")
class OpcoesInclusaoNfTerceiros:
    """Representação da janela com opções para incluir nota fiscal de terceiros na aba `Lista` da janela `Compras`"""

    janela: bot.sistema.JanelaW32
    janela_compras: bot.sistema.JanelaW32

    def __init__ (self, janela_compras: bot.sistema.JanelaW32) -> None:
        self.janela_compras = janela_compras
        self.janela = janela_compras.janela_processo(
            lambda j: j.class_name == "TForm_EntradaOpcao" and j.elemento.visivel,
            aguardar = 10
        )

    @property
    def janela_entrada_nf (self) -> bot.sistema.JanelaW32:
        try: return self.janela_compras.janela_processo(
            lambda j: j.class_name == "TFormEntradaNota" and j.elemento.visivel,
            aguardar = 10
        )
        except Exception:
            raise Exception("Janela 'Entrada de Nota Fiscal' não abriu conforme esperado")

    def clicar_botao_compra (self) -> bot.sistema.JanelaW32:
        """Clicar no botão `Compra`
        - Retornado janela `Entrada de Nota Fiscal`"""
        self.janela.to_uia()\
            .elemento\
            .encontrar(lambda e: e.botao and e.texto == "Compra")\
            .clicar()
        return self.janela_entrada_nf

__all__ = [
    "OpcoesInclusaoNfTerceiros",
]