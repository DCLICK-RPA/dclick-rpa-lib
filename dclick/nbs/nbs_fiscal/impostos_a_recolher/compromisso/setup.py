# std
from typing import Self
# externo
import bot
from bot.sistema.janela import ElementoW32

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Documento' da janela 'Compromisso'")
class AbaDocumento:
    """Representação da aba `Documento` na janela `Compromisso`"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == "Documento" and e.item_aba)\
              .clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == "Documento"
        )

    @property
    def painel_inferior_aba (self) -> ElementoW32:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_aba.filhos(lambda e: e.class_name == "TPanel")
        )
        assert len(elementos) >= 2, "Painel com elementos não encontrado"
        return elementos[1]

    def preencher_fornecedor (self, texto: str) -> Self:
        """Preencher o campo `Fornecedor` e apertado `TAB` para confirmar
        - Erro caso apareça diálogo com mensagem"""
        self.painel_inferior_aba\
            .encontrar(lambda e: e.class_name == "TCPF_CGC")\
            .apertar("backspace")\
            .digitar(texto)\
            .apertar("tab")

        if dialogo := self.janela.dialogo(aguardar=1):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao preencher o campo fornecedor com '{texto}': '{mensagem}'")

        return self

    def selecionar_natureza (self, descricao: str) -> Self:
        elemento, *_ = self.janela.ordernar_elementos_coordenada(
            self.painel_inferior_aba
                .to_uia()
                .filhos(lambda e: e.class_name == "TwwDBLookupCombo")
        ) or [None]
        assert elemento, "Elemento 'Natureza' não foi encontrado"

        elemento.encontrar(lambda e: e.class_name == "TBtnWinControl")\
                .clicar()
        elemento.digitar(descricao, virtual=False)\
                .apertar("enter")\
                .sleep(0.5)

        valor = elemento.valor
        assert valor.upper() == descricao.upper(), f"Falha ao preencher o campo naturaza | Esperado '{descricao}' | Encontrado '{valor}'"
        return self

    def selecionar_doc_tipo (self, texto: str) -> Self:
        """Selecionar o campo `Doc./Tipo`
        - Não possível confirmar se o `texto` foi selecionado corretamente"""
        elemento, *_ = self.janela.ordernar_elementos_coordenada(
            self.painel_inferior_aba
                .to_uia()
                .filhos(lambda e: e.class_name == "TDBLookupComboBox")
        ) or [None]
        assert elemento, "Elemento ComboBox 'Doc./Tipo' não foi encontrado"

        elemento.digitar(texto, virtual=False)
        return self

@bot.util.decoradores.prefixar_erro_classe("Falha na confirmação da janela 'Compromisso'")
class Confirmar:
    """Representação do processo de Confirmação na janela `Compromisso`"""

    full_hd: bool
    janela: bot.sistema.JanelaW32

    IMAGEM_CANCELAR = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEQAAAAXCAYAAACyCenrAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGmSURBVFhH7ZQ9ksIwDIV9J2Yyw10oUuQg6ag4BS1dzkCdkhNwgK1TeC1HCpYsO94MFGRdfAPRj+X3Ysc8fyZbeVENEVRDBJsMscbY3gG/Wv6bUQ0hwbkcodV8M5EhTHDfp3NKfg/kDQlEbzPjYfvGuNaZ002r+QDjxR6ai71ruRWyVyYUL5+1Ps5sxuH8wOfBnszR9qOs+wDvNgSITCFKr4myqfs4OPD/+bicHNMOr562c8aJOOUobjp7pfit09fB2ck5jZvjT2+wliNpCOCqtxsCGw0FhTCz4OTgprxo2mAQF6fLi4S12TqTvbZ4LSmenaOf1qwhkRnvMgTwm8I3R5tjAuDKafGA8HQg/oqG9atzOH+/MkCJKZmhsxDl7bOeQkM006m+aA6n7KOqsWqK9lHF51CI3/SKIeLK+B6og/olPs9jV6ZoDicyRDXDiY9iGJf9nNkEdpxlHD+iTIivCQ3BHPUsb93hhdJaKH5Zp2QOhxniOpOic7k9kTdECGb5HZoBpA1JCPY1OzUDiL4hIHbPgteIDPnvVEME1RBBNURQDWFM9hfM9zt0FZHS5AAAAABJRU5ErkJggg==")
    """Imagem do botão `Cancelar` na resolução `1920x1080`"""

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        resolucao_atual, _ = bot.sistema.informacoes_resolucao()
        self.full_hd = resolucao_atual == (1920, 1080)

    def clicar_ok (self) -> Self:
        """Clicar no botão `OK`"""
        self.janela.elemento\
            .encontrar(lambda e: e.texto.upper() == "OK" and e.class_name == "TBitBtn")\
            .clicar()
        return self

    def confirmar_dialogo_ficha_controle (self) -> Self:
        """Clicar em `Sim` no diálogo `Ficha de Controle`"""
        dialogo = self.janela.dialogo(aguardar=5)
        if not dialogo: return self

        texto = dialogo.elemento.textos().lower()
        assert "ficha de controle" in texto,\
            f"Texto do diálogo não está de acordo com o esperado: '{texto}'"

        assert dialogo.clicar("Sim"), "Diálogo 'Ficha de Controle' não fechou conforme esperado"
        return self

    def fechar_janela_ficha_controle_via_imagem (self) -> None:
        """Fechar a janela `Ficha de Controle de Pagamento`"""
        assert self.full_hd, "Esperado resolução '1920x1080' para encontrar a imagem do botão 'Cancelar'"

        titulo = 'Ficha de Controle de Pagamento'
        try: janela = self.janela.janela_processo(lambda j: j.titulo == titulo, aguardar=5).focar()
        except Exception:
            raise Exception(f"Janela '{titulo}' não foi encontrada")

        coordenada = self.IMAGEM_CANCELAR.procurar_imagem(
            regiao = janela.elemento.coordenada,
            segundos = 5
        )
        assert coordenada, f"Coordenada do botão 'Cancelar' não encontrado na janela '{titulo}'"

        bot.mouse.clicar_mouse(coordenada=coordenada)
        assert bot.util.aguardar_condicao(lambda: janela.fechada, timeout=5),\
            f"Janela '{titulo}' não foi fechada corretamente"

__all__ = [
    "Confirmar",
    "AbaDocumento"
]
