# std
import re as regex
from typing import Self
# externo
import bot
from bot.sistema.janela import ElementoW32

def clicar_botao_recalculo (janela_entrada_nf: bot.sistema.JanelaW32,
                            xy_offset: tuple[float, float] = (0.3, 0.5)) -> None:
    """Clicar na posicao do botão `Recálculo`. Botão não possui elemento
    - `xy_offset` para transformar a coordenada em relação ao elemento pai
    - Erro caso algum diálogo de erro apareça"""
    painel = janela_entrada_nf.focar().elemento[-1]
    posicao = painel.coordenada.transformar(*xy_offset)

    bot.mouse.mover(posicao)
    try: janela_entrada_nf.janela_processo(lambda j: bot.util.normalizar(j.titulo) == "recalculo",
                                           aguardar = 3)
    except Exception: raise Exception("Mouse na posição inválida para clicar no botão 'Recálculo'")
    bot.mouse.clicar()

    dialogo = janela_entrada_nf.focar().dialogo(aguardar=0.3)
    assert not dialogo, f"Diálogo inesperado ao clicar no botão 'Recálculo': {dialogo.texto}"

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
        )

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Financeiro' da janela 'Entrada de Nota Fiscal'")
class AbaFinanceiro:
    """Representação da aba `Financeiro` da janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Financeiro"
    IMAGEM_BOTAO_GERAR = bot.imagem.Imagem.from_base64("iVBORw0KGgoAAAANSUhEUgAAAEQAAAAdCAIAAACc8F3aAAABxUlEQVRYCd3BAW4cNxBFwfdPpr5ZkzcjT/YiEVhg5WQmARzDxlRF5Smi8hRReYqoPEVUniIqTxGVp4jKT5tzjtEwtfl9ovIT5pxjNF/mGHQ3v09Ubu29uVD1wZc5Bt0NzDk5upvvkvCi8gtE5dbeu+pjjFlVvKn6gDkGn7p7zsmb7uZNEpWXJCr/t6jc2ntXLegxZlVxVH3AHIOqWmvxprv5myQqv1hUbu2911pj9BiTY4yGOQZVBay1OLqbC0lU/kkSDhVIAqhAEg4VSAKoXIjKrb03UPUBjDHHaJhjUFXAWouju7mWRAWScKhAEpUjiZpE5bskahKVa1G5tfcGqhY0X+YYVBWw1uLobm4lUXlJogJJeKMmUTmS8KImUbkWlVt7b2CtNQafxuBTVa21eOlubiVReUmiAklU3iRRgSQqRxI1icq1qNzae3NUrTH4QVWttbqbW0lUjiSACiRROZKoSVQgicqRRE2ici0qt/bevFlr8VJVwFqru/k3STjUJCpHEg4VSKJyJOFFTaJyLSq39t58t9YCqopjrdXd/AGicm3OyX/Q3fwBovIUUXmKqDxFVJ4iKk8RlaeIylNE5Smi8hR/AZr8U9as1DM4AAAAAElFTkSuQmCC")
    """Imagem do botão `Gerar` na resolução `1920x1080`"""

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
        )

    @property
    def painel_condicao_pagamento (self) -> ElementoW32:
        return self.painel_aba["TGroupBox", 0]

    def condicao_pagamento_preencher_entrada (self, dias: int) -> Self:
        self.painel_condicao_pagamento["TOvcPictureField", 2]\
            .digitar(str(dias))\
            .apertar("tab")
        return self

    def condicao_pagamento_preencher_intervalo (self, dias: int) -> Self:
        self.painel_condicao_pagamento["TOvcPictureField", 3]\
            .digitar(str(dias))\
            .apertar("tab")
        return self

    def condicao_pagamento_preencher_total_parcelas (self, total: int) -> Self:
        self.painel_condicao_pagamento["TOvcPictureField", 4]\
            .digitar(str(total))\
            .apertar("tab")
        return self

    def condicao_pagamento_selecionar_tipo_pagamento (self, tipo: str) -> Self:
        valor = self.painel_condicao_pagamento["Tipo de Pagamento"]["TwwDBLookupCombo"]\
            .atalho("alt", "down")\
            .digitar(tipo, virtual=False, focar=False)\
            .sleep(0.5)\
            .apertar("tab", focar=False)\
            .to_uia().valor
        assert bot.util.normalizar(tipo) == bot.util.normalizar(valor),\
            f"Tipo de Pagamento selecionado não foi o esperado | Esperado({tipo}) | Selecionado({valor})"
        return self

    def condicao_pagamento_clicar_gerar (self) -> Self:
        """Clicar no botão `Gerar` em `Condição de Pagamento`
        - Erro caso algum diálogo apareça"""
        painel = self.painel_condicao_pagamento
        coordenada = self.IMAGEM_BOTAO_GERAR.procurar_imagem(
            regiao = painel.coordenada,
            segundos = 3
        )
        assert coordenada, "Imagem do botão 'Gerar' não foi"

        bot.mouse.mover(coordenada).clicar()
        painel.aguardar()

        assert not (dialogo := self.janela.dialogo(aguardar=1)),\
            f"Diálogo inesperado após clicar no botão 'Gerar': {dialogo.texto}"

        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'TotalNota' da janela 'Entrada de Nota Fiscal'")
class AbaTotalNota:
    """Representação da aba `TotalNota` da janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "TotalNota"

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
        )

    @property
    def painel_imposto_digitado (self) -> ElementoW32:
        return self.painel_aba["TGroupBox", 0]

    @property
    def painel_soma_imposto (self) -> ElementoW32:
        return self.painel_aba["TGroupBox", 1]

    def comparar_colunas (self) -> Self:
        """Comprar os campos do `painel_imposto_digitado` e `painel_soma_imposto`
        - Erro caso algum valor diferente do outro"""
        ordenar = self.janela.ordernar_elementos_coordenada
        elementos_ordenados = zip(
            ordenar(self.painel_imposto_digitado.to_uia().filhos(aguardar=2)),
            ordenar(self.painel_soma_imposto.to_uia().filhos(aguardar=2))
        )
        for posicao, elementos in enumerate(elementos_ordenados, start=1):
            a, b = map(lambda e: e.texto, elementos)
            assert a == b, f"Comparação de valores dos campos na posição '{posicao}' estão diferentes do esperado | '{a}' != '{b}'"
        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Locações' da janela 'Entrada de Nota Fiscal'")
class AbaLocacoes:
    """Representação da aba `Locações` da janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Locações"

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
        )

    @property
    def painel_itens_lancados (self) -> ElementoW32:
        return self.painel_aba.encontrar(
            lambda e: "Itens Lançados" in e.texto and e.visivel,
            aguardar = 5
        )

    @property
    def painel_inputs (self) -> ElementoW32:
        return self.painel_aba["TPanel"]

    @property
    def painel_novas_locacoes (self) -> ElementoW32:
        return self.painel_aba["Novas Locações"]

    def selecionar_local (self, local: str) -> Self:
        valor = self.painel_inputs["TwwDBLookupCombo"]\
            .atalho("alt", "down")\
            .digitar(local, virtual=False, focar=False)\
            .sleep(0.5)\
            .apertar("tab", focar=False)\
            .to_uia().valor
        assert bot.util.normalizar(local) == bot.util.normalizar(valor),\
            f"Local selecionado não foi o esperado | Esperado({local}) | Selecionado({valor})"
        return self

    def preencher_locacao (self, texto: str) -> Self:
        self.painel_inputs["TEdit"].digitar(texto).apertar("tab")
        return self

    def preencher_locacao_padrao (self, texto: str) -> Self:
        painel = self.painel_inputs
        elemento = painel.encontrar(
            lambda e: e.class_name == "TOvcPictureField" and e.profundidade - 2 == painel.profundidade,
            aguardar = 5
        )
        elemento.digitar(texto).apertar("tab")
        return self

    def clicar_botao_sugestao (self, xy_offset: tuple[float, float] = (0.58, 0.5)) -> Self:
        """Clicar na posicao do botão `Sugestão`. Botão não possui elemento
        - `xy_offset` para transformar a coordenada em relação ao elemento pai
        - Erro caso algum diálogo de erro apareça"""
        self.janela.focar()

        posicao = self.painel_inputs.coordenada.transformar(*xy_offset)
        bot.mouse.mover(posicao)
        assert "locacoes atuais" in self.janela.tooltips().lower(), "Mouse na posição inválida para clicar no botão 'Sugestão'"
        bot.mouse.clicar()

        dialogo = self.janela.focar().dialogo(aguardar=0.3)
        assert not dialogo, f"Diálogo inesperado ao clicar no botão 'Sugestão': {dialogo.texto}"

        return self

    def itens_lancados_nao_encontrar_cor_vermelha (self) -> Self:
        """Procurar no painel `Itens Lançados` se cor vermelha não existe
        - `AssertionError` caso seja encontrado"""
        cor = (255, 0, 0)
        posicao = self.painel_itens_lancados.imagem.encontrar_cor(cor)
        assert posicao is None, "Cor vermelha detectada no painel 'Itens Lançados'"
        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na confirmação da janela 'Entrada de Nota Fiscal'")
class Confirmar:
    """Representação do processo de Confirmação na janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Confirmando na janela '{janela.titulo}'")
        self.janela = janela

    @property
    def painel_botao_confirmar (self) -> ElementoW32:
        return self.janela.elemento[-1]

    def clicar_botao_aceitar (self) -> Self:
        """Clicar no botão `Aceitar`"""
        self.painel_botao_confirmar["Confirmar"].clicar()
        return self

    def condicao_sucesso (self) -> str:
        """Condição esperada para o sucesso após clicar no botão `Aceitar`
        - Confirmar diálogos, exceto o `imprimir`
        - Confirmar diálogo `Número de Controle` e retornar o valor
        - Esperado que a janela feche"""
        self.janela.aguardar()
        texto_dialogo = ""

        for _ in range(5):
            dialogo = self.janela.dialogo(aguardar=1)
            if not dialogo: break
            texto_dialogo = dialogo.texto
            if "imprimir" in texto_dialogo: dialogo.negar()
            else: dialogo.confirmar()

        match = regex.search(r"\d+", texto_dialogo)
        assert "sucesso" in texto_dialogo.lower() and match, f"Diálogo inesperado: '{texto_dialogo}'"
        assert bot.util.aguardar_condicao(lambda: self.janela.fechada, timeout=10),\
            f"Janela '{self.janela.titulo}' não fechou conforme esperado"

        return match.group()

__all__ = [
    "clicar_botao_recalculo",
    "AbaCapaNotaFiscal",
    "AbaFinanceiro",
    "AbaTotalNota",
    "AbaLocacoes",
    "Confirmar",
]