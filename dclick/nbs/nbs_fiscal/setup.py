# externo
import bot

IMAGEM_MODULO = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADoAAAAvCAYAAACyoNkAAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGVSURBVGhD7ZhtroQgDEVdOktzZ765ozdem6JoLM5DTkKE8lFOSubHDNNL6KKt0UWjSCktvZVhSN8WSbgoxTxBMEviG3uVsNNVbBzHpbelliQIyaBVhCRaMjI1JcHtWexTpShIaU5XWxKEZKLYt5IfYVYWPCEJbs9GIYDnqpKoKARzkqx4BLefjMvywny+YH226zzBeK7+fxL9iODSWlmvipBSQezLVfoObj8Zl7WiCuVqCZKQDLg4K2ahKL41BElYJj5hS60KWsIyek/4CUESmplPmP0nCc/+1FO1hN/gFyTBb9yiAl20Nbpoa3TR1uiirdFFW+PdovhL0qIxb76E+a/ObWP8LnJnZUXtBh1fvdjVfWfI5eii+gW2r03xYqQk7u1nrCRu15DLosrReoKYNsL+UQzYMcmtJ4c/Rt4B9rC9OSU3V3q2BXPaGPM4FAV6EPDmFTsmpXEdn92TXb98N3iHaMyb1y+wa4AXA3v77Z6zcVIkCjSGvjbFi5GSuLefsb045+wa4oq2SBdtjS7aGi8RnaY/CSKCTRQAu6YAAAAASUVORK5CYII=")
"""Imagem do módulo `Nbs Fiscal` na resolução `1920x1080`"""

class SelecaoEmpresaFilial:
    """Classe para tratar a seleção da empresa e filial do menu `Nbs Fiscal`
    - TODO implementar escolhas de Empresa e Filial"""

    janela: bot.sistema.JanelaW32

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela

    @bot.util.decoradores.prefixar_erro("Erro ao confirmar a seleção da Empresa/Filial")
    def confirmar (self) -> bot.sistema.JanelaW32:
        """Clicar no botão de confirmar
        - Fechado janela informativa que pode aparecer
        - Retornado janela `Sistema Fiscal`"""
        self.janela.elemento\
            .encontrar(lambda e: "confirma" in e.texto.lower())\
            .clicar()

        # Janela informativa fechada caso aparecer
        try: self.janela.janela_processo(lambda j: j.class_name == "TFrmListaNfeRen", aguardar=2)\
                        .sleep()\
                        .fechar()
        except Exception: pass

        try: return self.janela.janela_processo(lambda j: j.titulo == "Sistema Fiscal", aguardar=2)
        except Exception:
            raise Exception("Janela 'Sistema Fiscal' não foi encontrada")

@bot.util.decoradores.prefixar_erro("Falha ao selecionar o módulo 'ADM / NBS Fiscal'")
def selecionar_modulo_nbs_fiscal (janela_shortcut: bot.sistema.JanelaW32,
                                  imagem: bot.imagem.Imagem | None = IMAGEM_MODULO) -> SelecaoEmpresaFilial:
    """Selecionar o menu do `Nbs Fiscal`
    - `imagem` para procurar via imagem
    - `imagem=None` é feito o click em posição esperada na aba `ADM`
    - Retornado `SelecaoEmpresaFilial`"""
    abas = janela_shortcut.elemento.descendentes(
        lambda elemento: elemento.class_name == "TfcShapeBtn",
        aguardar = 5
    )
    *_, aba_adm = janela_shortcut.ordernar_elementos_coordenada(abas)
    aba_adm.clicar()

    coordenada_painel = janela_shortcut.elemento\
        .focar()\
        .encontrar(lambda e: e.visivel and e.class_name == "TfcOutlookPanel", aguardar=2)\
        .coordenada

    if imagem is None:
        posicao_nbs_fiscal = coordenada_painel.transformar(0.5, 0.26)
    else:
        posicao_nbs_fiscal = imagem.procurar_imagem(regiao=coordenada_painel, cinza=True, segundos=3)
        assert posicao_nbs_fiscal, "Imagem do módulo não foi encontrada"

    bot.mouse.clicar_mouse(coordenada=posicao_nbs_fiscal)
    try: return SelecaoEmpresaFilial(
        bot.sistema.JanelaW32(lambda j: "Empresa/Filial" in j.titulo, aguardar=10)
                   .focar()
    )
    except Exception:
        raise Exception("Janela de seleção 'Empresa/Filial' não abriu conforme o esperado")

def fechar_janela_nbs_fiscal (titulo: str = "Sistema Fiscal") -> None:
    """Fechar a janela nbs fiscal `titulo`
    - Usado o `destruir` na janela para encerrar todas as janelas dependentes
    - Ignorado caso não encontre
    - `AssertionError` caso falhe ao encerrar"""
    try: assert bot.sistema.JanelaW32(lambda j: j.titulo == titulo, aguardar=1)\
                           .destruir(5),\
            f"Falha ao encerrar a janela nbs fiscal '{titulo}'"
    except AssertionError: raise
    except Exception: return

__all__ = [
    "SelecaoEmpresaFilial",
    "fechar_janela_nbs_fiscal",
    "selecionar_modulo_nbs_fiscal"
]