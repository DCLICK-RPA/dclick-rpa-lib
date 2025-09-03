# externo
import bot

@bot.util.decoradores.prefixar_erro_classe("Falha na janela de seleção para incluir nota fiscal de terceiros")
class OpcoesInclusaoNfTerceiros:
    """Representação da janela com opções para incluir nota fiscal de terceiros na aba `Lista` da janela `Compras`"""

    janela: bot.sistema.JanelaW32
    janela_compras: bot.sistema.JanelaW32

    CLASSNAME_JANELA_ENTRADA_FRETE = "TForm_EntradaFrete"

    def __init__ (self, janela_compras: bot.sistema.JanelaW32) -> None:
        self.janela_compras = janela_compras.focar()
        self.janela = janela_compras.janela_processo(
            lambda j: j.class_name == "TForm_EntradaOpcao" and j.visivel,
            aguardar = 10
        ).focar()

    @property
    def janela_entrada_nf (self) -> bot.sistema.JanelaW32:
        try: return self.janela_compras.janela_processo(lambda j: j.class_name == "TFormEntradaNota" and j.visivel,
                                                        aguardar = 10)\
                                       .focar()
        except Exception:
            raise Exception("Janela 'Entrada de Nota Fiscal' não abriu conforme esperado")

    def clicar_botao_compra (self) -> bot.sistema.JanelaW32:
        """Clicar no botão `Compra`
        - Caso a janela `Conhecimento de Transporte` apareça, será cliado em `Entrada Sem Frete`
        - Retornado janela `Entrada de Nota Fiscal`"""
        with bot.sistema.JanelaW32.aguardar_nova_janela() as janela:
            self.janela.to_uia().elemento\
                .encontrar(lambda e: e.botao and e.texto == "Compra")\
                .clicar()

        if janela.class_name == self.CLASSNAME_JANELA_ENTRADA_FRETE:
            janela.elemento.encontrar(lambda e: e.texto == "Entrada Sem Frete" and e.visivel).clicar()
            janela.elemento.encontrar(lambda e: e.texto == "OK").clicar()

        return self.janela_entrada_nf

__all__ = [
    "OpcoesInclusaoNfTerceiros",
]