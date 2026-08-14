# std
from typing import Self
# interno
import dclick
from dclick.nbs import DEFAULT_TIMEOUT
# externo
import bot
from bot.estruturas import String
from bot.sistema.janela import ElementoW32
from bot.imagem import Imagem, capturar_tela

def clicar_botao_recalculo (janela_entrada_nf: bot.sistema.JanelaW32,
                            xy_offset: tuple[float, float] = (0.3, 0.5)) -> None:
    """Clicar na posicao do botão `Recálculo`. Botão não possui elemento
    - `xy_offset` para transformar a coordenada em relação ao elemento pai
    - Erro caso algum diálogo de erro apareça"""
    painel = janela_entrada_nf.focar().elemento[-1]
    posicao = painel.coordenada.transformar(*xy_offset)

    bot.mouse.mover(posicao)
    try: janela_entrada_nf.janelas_processo(lambda j: String(j.titulo).normalizar() == "recalculo",
                                           aguardar = DEFAULT_TIMEOUT)
    except Exception: raise Exception("Mouse na posição inválida para clicar no botão 'Recálculo'")
    bot.mouse.clicar()

    dialogo = janela_entrada_nf.focar().dialogo(aguardar=0.3)
    assert not dialogo, f"Diálogo inesperado ao clicar no botão 'Recálculo': {dialogo.texto}"

@bot.erro.adicionar_prefixo_classe("Falha na aba 'CapaNotaFiscal' da janela 'Entrada de Nota Fiscal'")
class AbaCapaNotaFiscal:
    """Representação da aba `CapaNotaFiscal` da janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "CapaNotaFiscal"

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        dclick.logger.debug(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia().elemento.encontrar(
            lambda e: e.texto == self.NOME_ABA
                      and e.tipo.item_aba,
            aguardar = DEFAULT_TIMEOUT
        ).clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA,
            aguardar = DEFAULT_TIMEOUT
        )

@bot.erro.adicionar_prefixo_classe("Falha na aba 'Financeiro' da janela 'Entrada de Nota Fiscal'")
class AbaFinanceiro:
    """Representação da aba `Financeiro` da janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Financeiro"
    IMAGEM_BOTAO_GERAR = Imagem.FromBase64("iVBORw0KGgoAAAANSUhEUgAAAEQAAAAdCAIAAACc8F3aAAABxUlEQVRYCd3BAW4cNxBFwfdPpr5ZkzcjT/YiEVhg5WQmARzDxlRF5Smi8hRReYqoPEVUniIqTxGVp4jKT5tzjtEwtfl9ovIT5pxjNF/mGHQ3v09Ubu29uVD1wZc5Bt0NzDk5upvvkvCi8gtE5dbeu+pjjFlVvKn6gDkGn7p7zsmb7uZNEpWXJCr/t6jc2ntXLegxZlVxVH3AHIOqWmvxprv5myQqv1hUbu2911pj9BiTY4yGOQZVBay1OLqbC0lU/kkSDhVIAqhAEg4VSAKoXIjKrb03UPUBjDHHaJhjUFXAWouju7mWRAWScKhAEpUjiZpE5bskahKVa1G5tfcGqhY0X+YYVBWw1uLobm4lUXlJogJJeKMmUTmS8KImUbkWlVt7b2CtNQafxuBTVa21eOlubiVReUmiAklU3iRRgSQqRxI1icq1qNzae3NUrTH4QVWttbqbW0lUjiSACiRROZKoSVQgicqRRE2ici0qt/bevFlr8VJVwFqru/k3STjUJCpHEg4VSKJyJOFFTaJyLSq39t58t9YCqopjrdXd/AGicm3OyX/Q3fwBovIUUXmKqDxFVJ4iKk8RlaeIylNE5Smi8hR/AZr8U9as1DM4AAAAAElFTkSuQmCC")
    """Imagem do botão `Gerar` na resolução `1920x1080`"""

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        dclick.logger.debug(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia().elemento.encontrar(
            lambda e: e.texto == self.NOME_ABA
                      and e.tipo.item_aba,
            aguardar = DEFAULT_TIMEOUT
        ).clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA,
            aguardar = DEFAULT_TIMEOUT
        )

    @property
    def painel_condicao_pagamento (self) -> ElementoW32:
        return self.painel_aba / "TGroupBox[0]"

    def condicao_pagamento_preencher_entrada (self, dias: int) -> Self:
        (self.painel_condicao_pagamento / "TOvcPictureField[2]")\
            .digitar(str(dias))\
            .teclar("tab")
        return self

    def condicao_pagamento_preencher_intervalo (self, dias: int) -> Self:
        (self.painel_condicao_pagamento / "TOvcPictureField[3]")\
            .digitar(str(dias))\
            .teclar("tab")
        return self

    def condicao_pagamento_preencher_total_parcelas (self, total: int) -> Self:
        (self.painel_condicao_pagamento / "TOvcPictureField[4]")\
            .digitar(str(total))\
            .teclar("tab")
        return self

    def condicao_pagamento_selecionar_tipo_pagamento (self, tipo: str) -> Self:
        valor = (self.painel_condicao_pagamento / "Tipo de Pagamento" / "TwwDBLookupCombo[0]")\
            .atalho("alt", "down")\
            .digitar(tipo, focar=False)\
            .sleep(0.5)\
            .teclar("tab")\
            .to_uia().valor
        assert String(tipo).normalizar() == String(valor).normalizar(),\
            f"Tipo de Pagamento selecionado não foi o esperado | Esperado({tipo}) | Selecionado({valor})"
        return self

    def condicao_pagamento_clicar_gerar (self) -> Self:
        """Clicar no botão `Gerar` em `Condição de Pagamento`
        - Erro caso algum diálogo apareça"""
        painel = self.painel_condicao_pagamento
        coordenada = self.IMAGEM_BOTAO_GERAR.procurar_imagem(
            regiao = painel.coordenada,
            segundos = DEFAULT_TIMEOUT
        )
        assert coordenada, "Imagem do botão 'Gerar' não foi"

        bot.mouse.mover(coordenada).clicar()
        painel.aguardar()

        assert not (dialogo := self.janela.dialogo(aguardar=1)),\
            f"Diálogo inesperado após clicar no botão 'Gerar': {dialogo.texto}"

        return self

@bot.erro.adicionar_prefixo_classe("Falha na aba 'TotalNota' da janela 'Entrada de Nota Fiscal'")
class AbaTotalNota:
    """Representação da aba `TotalNota` da janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "TotalNota"

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        dclick.logger.debug(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia().elemento.encontrar(
            lambda e: e.texto == self.NOME_ABA
                      and e.tipo.item_aba,
            aguardar = DEFAULT_TIMEOUT
        ).clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA,
            aguardar = DEFAULT_TIMEOUT
        )

    @property
    def painel_imposto_digitado (self) -> ElementoW32:
        return self.painel_aba / "TGroupBox[0]"

    @property
    def painel_soma_imposto (self) -> ElementoW32:
        return self.painel_aba / "TGroupBox[1]"

    def comparar_colunas (self) -> Self:
        """Comprar os campos do `painel_imposto_digitado` e `painel_soma_imposto`
        - Erro caso algum valor diferente do outro"""
        ordenar = self.janela.aguardar().ordernar_elementos_coordenada
        elementos_ordenados = zip(
            ordenar(self.painel_imposto_digitado.to_uia().filhos(aguardar=2)),
            ordenar(self.painel_soma_imposto.to_uia().filhos(aguardar=2))
        )
        for posicao, elementos in enumerate(elementos_ordenados, start=1):
            a, b = map(lambda e: e.texto, elementos)
            assert a == b, f"Comparação de valores dos campos na posição '{posicao}' estão diferentes do esperado | '{a}' != '{b}'"
        return self

@bot.erro.adicionar_prefixo_classe("Falha na aba 'Locações' da janela 'Entrada de Nota Fiscal'")
class AbaLocacoes:
    """Representação da aba `Locações` da janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Locações"

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        dclick.logger.debug(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia().elemento.encontrar(
            lambda e: e.texto == self.NOME_ABA
                      and e.tipo.item_aba,
            aguardar = DEFAULT_TIMEOUT
        ).clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA,
            aguardar = DEFAULT_TIMEOUT
        )

    @property
    def painel_itens_lancados (self) -> ElementoW32:
        return self.painel_aba.encontrar(
            lambda e: "Itens Lançados" in e.texto and e.visivel,
            aguardar = DEFAULT_TIMEOUT / 2
        )

    @property
    def painel_inputs (self) -> ElementoW32:
        return self.painel_aba / "TPanel[0]"

    @property
    def painel_novas_locacoes (self) -> ElementoW32:
        return self.painel_aba / "Novas Locações"

    def selecionar_local (self, local: str) -> Self:
        valor = (self.painel_inputs / "TwwDBLookupCombo[0]")\
            .atalho("alt", "down")\
            .digitar(local, focar=False)\
            .sleep(0.5)\
            .teclar("tab", focar=False)\
            .to_uia().valor
        assert String(local).normalizar() == String(valor).normalizar(),\
            f"Local selecionado não foi o esperado | Esperado({local}) | Selecionado({valor})"
        return self

    def preencher_locacao (self, texto: str) -> Self:
        (self.painel_inputs / "TEdit[0]").digitar(texto).teclar("tab")
        return self

    def preencher_locacao_padrao (self, texto: str) -> Self:
        painel = self.painel_inputs
        elemento = painel.encontrar(
            lambda e: e.class_name == "TOvcPictureField" and e.profundidade - 2 == painel.profundidade,
            aguardar = DEFAULT_TIMEOUT / 2
        )
        elemento.digitar(texto).teclar("tab")
        return self

    def clicar_botao_sugestao (self, xy_offset: tuple[float, float] = (0.58, 0.5)) -> Self:
        """Clicar na posicao do botão `Sugestão`. Botão não possui elemento
        - `xy_offset` para transformar a coordenada em relação ao elemento pai
        - Erro caso algum diálogo de erro apareça"""
        self.janela.focar()

        posicao = self.painel_inputs.coordenada.transformar(*xy_offset)
        bot.mouse.mover(posicao)
        assert "locacoes atuais" in (self.janela.tooltips() or "").lower(), "Mouse na posição inválida para clicar no botão 'Sugestão'"
        bot.mouse.clicar()

        dialogo = self.janela.focar().dialogo(aguardar=0.3)
        assert not dialogo, f"Diálogo inesperado ao clicar no botão 'Sugestão': {dialogo.texto}"

        return self

    def itens_lancados_nao_encontrar_cor_vermelha (self) -> Self:
        """Procurar no painel `Itens Lançados` se cor vermelha não existe
        - `AssertionError` caso seja encontrado"""
        RGB_VERMELHO = (255, 0, 0)
        coordenada = self.painel_itens_lancados.coordenada
        posicao = capturar_tela(coordenada).encontrar_cor(RGB_VERMELHO)
        assert posicao is None, "Cor vermelha não detectada no painel 'Itens Lançados'"
        return self

@bot.erro.adicionar_prefixo_classe("Falha na confirmação da janela 'Entrada de Nota Fiscal'")
class Confirmar:
    """Representação do processo de Confirmação na janela `Entrada de Nota Fiscal`"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        dclick.logger.debug(f"Confirmando na janela '{janela.titulo}'")
        self.janela = janela

    @property
    def painel_botao_confirmar (self) -> ElementoW32:
        return self.janela.elemento[-1]

    def clicar_botao_aceitar (self) -> Self:
        """Clicar no botão `Aceitar`"""
        (self.painel_botao_confirmar  / "Confirmar").clicar()
        return self

    def condicao_sucesso (self) -> str:
        """Condição esperada para o sucesso após clicar no botão `Aceitar`
        - Confirmar diálogos, exceto o `imprimir`
        - Confirmar diálogo `Número de Controle` e retornar o valor
        - Esperado que a janela feche"""
        texto_dialogo = ""
        self.janela.aguardar()

        for _ in range(5):
            dialogo = self.janela.dialogo(aguardar=1)
            if not dialogo: break
            texto_dialogo = dialogo.texto
            if "imprimir" in texto_dialogo: dialogo.negar()
            else: dialogo.confirmar()

        match = String(texto_dialogo).re_search(r"\d+")
        assert "sucesso" in texto_dialogo.lower() and match, f"Diálogo inesperado: '{texto_dialogo}'"
        assert bot.tempo.aguardar(lambda: self.janela.fechada, timeout=DEFAULT_TIMEOUT),\
            f"Janela '{self.janela.titulo}' não fechou conforme esperado"

        return str(match)

__all__ = [
    "clicar_botao_recalculo",
    "AbaCapaNotaFiscal",
    "AbaFinanceiro",
    "AbaTotalNota",
    "AbaLocacoes",
    "Confirmar",
]