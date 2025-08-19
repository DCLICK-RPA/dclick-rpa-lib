# std
from typing import Self
# externo
import bot
from bot.sistema.janela import ElementoW32

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Pesquisar' da janela 'Monitor Notas Eletrônicas'")
class AbaPesquisar:
    """Representação da aba `Pesquisar` na janela `Monitor Notas Eletrônicas`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Pesquisar"

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
              .clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA
        )

    def alternar_inicio_emissao (self) -> Self:
        """Alternar o estado do checkbox `Emissao` de início"""
        elemento, *_ = self.janela.ordernar_elementos_coordenada(
            self.painel_aba.descendentes(lambda e: e.class_name == "TDateTimePicker", aguardar=5)
        ) or [None]
        assert elemento, "Elemento 'Data Emissão Início' não foi encontrado"

        elemento.apertar("space")
        return self

    def preencher_numero_nfe (self, texto: str) -> Self:
        elemento, *_ = self.janela.ordernar_elementos_coordenada(
            self.painel_aba.descendentes(lambda e: e.class_name == "TOvcPictureField", aguardar=5)
        ) or [None]
        assert elemento, "Elemento 'Número NFe' não foi encontrado"

        elemento.digitar(texto).apertar("tab")
        return self

    def selecionar_fornecedor (self, fornecedor: str) -> Self:
        """Selecionar o `fornecedor` na parte inferior da aba
        - Feito validação se foi selecionado com sucesso"""
        elemento = self.painel_aba[-1].to_uia()\
            .encontrar(lambda e: e.class_name == "TwwDBLookupCombo", aguardar=5)\
            .atalho("alt", "down")\
            .digitar(fornecedor, virtual=False, focar=False)\
            .sleep(0.5)\
            .apertar("tab", focar=False)

        valor = elemento.valor
        assert bot.util.normalizar(fornecedor) in bot.util.normalizar(valor),\
            f"Falha ao selecionar o fornecedor '{fornecedor}' | Encontrado '{valor}'"

        return self

    def atalho_botao_pesquisar (self) -> Self:
        """Realizar o atalho `F1` para o botão `Pesquisar`"""
        painel = self.painel_aba
        painel[0].atalho("f1")
        painel.encontrar(lambda e: e.class_name == "TwwDBGrid")\
              .aguardar()
        return self

__all__ = [
    "AbaPesquisar",
]