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
    IMAGEM_COLUNA_EMISSAO = bot.imagem.Imagem.from_base64("iVBORw0KGgoAAAANSUhEUgAAADAAAAATCAIAAABZWBlIAAACWElEQVRIDc3BIZLdOBQF0Pv2Igf8ygqsFcghRk3FLCiTYR82C7GgzEQbmcRagbyC1AeRNtEruOOuzDToTFWGTI3PEZK4EiGJKxGSuBIhiSsRkvjvZCfD96Um2K+fSjT4PSGJU3YyrPhLv9TiFf5ZC9oiFa/we9npH38k2G7+vDMa/AtCEqfsZBsZDf5vQhKn7GQbGQ3etaDt4zPW9UC/7E8vw3ygX2r58k1bpPLlm+7mA6d+qcUroAXdzQdO/VKLVwBa0N184DTtjAZAC7qbDwD9UotX+IWQxCk7GVb81C+1eNWC7l6eavEIunt5qsUjaIuUYC3S/dFtI6MBspNtZDTZyTYyGiA72UZG04K2SMUrZCfbyGha0N3jzmiQnTzfavEKHwhJnLKTbWQ0eNeCtkjFqxa0RSpetaAtUoK1SAm2mw8A085ocGpBd/MBYNoZDX5qQXfzgVO/1OKrk21kNACyk21kNPhASOKUnWwjo8G7FrRFKl61oC1S8aoFbZESrEUqXgFoQXfzAUw7o8GbFnQ3H8C0M8LJgJ3RIDt5vtXiq5NtZDQAspNtZDT4QEjilJ1sI6PBuxa0RSpetaAtUvGqBW2REqzF/elleNwZDYDs5PlWE2z3uDMaANnJ862WT19lGxkNspPh+1KLR9Dd485okJ0832rxCh8ISZyyk2HF36adsQvaIhWvWtAWqXjVgrZICdYiFV+dDCve9EstXgHZybDiTb/U4hWyk2EFME3TumJnNGhBd/MBYNoZDX4lJHElQhJXIiRxJUISVyIkcSVC8vX1FZfxJ0EIY73AjKTzAAAAAElFTkSuQmCC")
    """Imagem da coluna `Emissão` na resolução `1920x1080`"""

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

    @property
    def grid (self) -> ElementoW32:
        return self.painel_aba.encontrar(lambda e: e.class_name == "TwwDBGrid" and e.visivel)

    def alternar_inicio_emissao (self) -> Self:
        """Alternar o estado do checkbox `Emissao` de início"""
        self.painel_aba\
            [0]["TDateTimePicker"]\
            .apertar("space")
        return self

    def preencher_numero_nfe (self, texto: str) -> Self:
        self.painel_aba\
            [0]["TOvcPictureField"]\
            .digitar(texto)\
            .apertar("tab")
        return self

    def selecionar_fornecedor (self, fornecedor: str) -> Self:
        """Selecionar o `fornecedor` na parte inferior da aba
        - Feito validação se foi selecionado com sucesso"""
        elemento = self.painel_aba[-1].to_uia()\
            .encontrar(lambda e: e.class_name == "TwwDBLookupCombo" and e.visivel, aguardar=5)\
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
        self.painel_aba[0].atalho("f1")
        self.grid.aguardar()
        return self

    def ordenar_grid_emissao_via_imagem (self) -> Self:
        """Clicar na coluna `Emissão` para ordenar"""
        grid = self.grid
        coordenada = self.IMAGEM_COLUNA_EMISSAO.procurar_imagem(
            regiao = grid.coordenada,
            segundos = 3,
            cinza = True,
        )
        assert coordenada, "Coordenada da coluna 'Emissão' no grid não foi encontrado"

        bot.mouse.mover(coordenada).clicar()
        grid.aguardar()
        return self

    def selecionar_ultimo_registro (self) -> Self:
        """Selecionar o último registro através de atalhos
        - Erro caso não tenha nenhum registro (Feito via imagem)"""
        grid = self.grid
        imagem_antes_selecionar = bot.imagem.capturar_tela(grid.coordenada)
        grid.apertar("end", "space").aguardar()

        nao_encontrado = imagem_antes_selecionar.procurar_imagem(confianca=1.0, regiao=grid.coordenada) is None
        assert nao_encontrado, "Nenhum registro encontrado para ser selecionado"

        return self

    def salvar (self) -> None:
        """Clicar no botão `Salvar` e confirmar diálogo de confirmação
        - Confirmado diálogo sobre o `SEFAZ` caso apareça
        - Erro caso diálogo seja diferente do esperado
        - Janela `Monitor Notas Eletrônicas` fechada"""
        self.painel_aba[-1]\
            .to_uia()\
            .encontrar(lambda e: e.botao and e.texto == "Salvar" and e.visivel)\
            .clicar()

        dialogo = self.janela.dialogo(aguardar=3)
        assert dialogo, "Diálogo de confirmação, após clicar em 'Salvar', não encontrado"

        if "sefaz" in dialogo.texto.lower():
            dialogo.confirmar()
            dialogo = self.janela.dialogo(aguardar=3)
            assert dialogo, "Diálogo de confirmação, após clicar em 'Salvar', não encontrado"

        texto = dialogo.texto
        if "salvar" not in texto.lower():
            dialogo.negar()
            raise AssertionError(f"Texto do diálogo de confirmação, após clicar em 'Salvar', não está de acordo com o esperado | {texto}")

        dialogo.confirmar()
        dialogo = self.janela.dialogo(aguardar=0.5)
        assert not dialogo, f"Diálogo inesperado encontrado após salvar: {texto}"

        assert self.janela.fechar(), "Esperado janela fechar após salvar"

__all__ = [
    "AbaPesquisar",
]