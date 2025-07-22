# std
from typing import Self
# externo
import bot
from bot.util import normalizar

IMAGEM_MODULO = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADoAAAAvCAYAAACyoNkAAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGVSURBVGhD7ZhtroQgDEVdOktzZ765ozdem6JoLM5DTkKE8lFOSubHDNNL6KKt0UWjSCktvZVhSN8WSbgoxTxBMEviG3uVsNNVbBzHpbelliQIyaBVhCRaMjI1JcHtWexTpShIaU5XWxKEZKLYt5IfYVYWPCEJbs9GIYDnqpKoKARzkqx4BLefjMvywny+YH226zzBeK7+fxL9iODSWlmvipBSQezLVfoObj8Zl7WiCuVqCZKQDLg4K2ahKL41BElYJj5hS60KWsIyek/4CUESmplPmP0nCc/+1FO1hN/gFyTBb9yiAl20Nbpoa3TR1uiirdFFW+PdovhL0qIxb76E+a/ObWP8LnJnZUXtBh1fvdjVfWfI5eii+gW2r03xYqQk7u1nrCRu15DLosrReoKYNsL+UQzYMcmtJ4c/Rt4B9rC9OSU3V3q2BXPaGPM4FAV6EPDmFTsmpXEdn92TXb98N3iHaMyb1y+wa4AXA3v77Z6zcVIkCjSGvjbFi5GSuLefsb045+wa4oq2SBdtjS7aGi8RnaY/CSKCTRQAu6YAAAAASUVORK5CYII=")
"""Imagem do módulo `Nbs Fiscal` na resolução `1920x1080`"""

class SelecaoEmpresaFilial:
    """Classe para tratar a seleção da empresa e filial do menu `Nbs Fiscal`
    - TODO Não encontrado forma de se realizar o input do texto para o elemento da Empresa e confirmar em seguida"""

    janela: bot.sistema.JanelaW32
    empresa: str
    filial: str

    def __init__ (self) -> None:
        bot.logger.informar(f"Selecionando a empresa/filial")
        self.empresa = self.filial = ""
        try: self.janela = bot.sistema.JanelaW32(lambda j: "Empresa/Filial" in j.titulo, aguardar=10).focar()
        except Exception: raise Exception("Janela de seleção 'Empresa/Filial' não encontrada")

    def selecionar_empresa (self, empresa: str) -> Self:
        """Selecionar a `empresa`
        - Não possível confirmar se foi selecionado corretamente"""
        self.empresa = empresa
        self.janela.elemento\
            .encontrar(lambda e: e.texto == "Empresa")\
            .encontrar(lambda e: e.class_name == "TDBLookupComboBox")\
            .digitar(empresa, virtual=False)
        return self

    def selecionar_filial (self, filial: str) -> Self:
        self.filial = filial
        elemento = self.janela.to_uia().elemento\
            .encontrar(lambda e: e.texto == "Filial")\
            .encontrar(lambda e: e.class_name == "TwwDBLookupCombo")\
            .clicar()\
            .digitar(filial, virtual=False)\
            .apertar("enter")

        valor = elemento.valor
        assert normalizar(valor) == normalizar(filial),\
            f"Falha ao preencher a filial | Esperado '{filial}' | Encontrado '{valor}'"
        return self

    @bot.util.decoradores.prefixar_erro("Erro ao confirmar a seleção da Empresa/Filial")
    def confirmar (self) -> bot.sistema.JanelaW32:
        """Clicar no botão de confirmar
        - Fechado janela informativa que pode aparecer
        - Utilizar `self.checar_selecao` para checar sucesso após
        - Retornado janela `Sistema Fiscal`"""
        self.janela.elemento\
            .encontrar(lambda e: "confirma" in e.texto.lower())\
            .clicar()

        # Janela informativa fechada caso aparecer
        try: self.janela.janela_processo(lambda j: j.class_name == "TFrmListaNfeRen", aguardar=2)\
                        .sleep()\
                        .fechar()
        except Exception: pass

        try: return bot.sistema.JanelaW32(lambda j: j.titulo == "Sistema Fiscal", aguardar=5)
        except Exception:
            raise Exception("Janela 'Sistema Fiscal' não foi encontrada")

    def checar_selecao (self) -> None:
        """Checar se a selação da Empresa/Filial aconteceu com sucesso"""
        empresa, filial = self.obter_empresa_filial_selecionada()
        assert normalizar(self.empresa) in normalizar(empresa),\
            f"Falha ao selecionar a empresa '{self.empresa}' | Encontrado '{empresa}'"
        assert normalizar(self.filial) in normalizar(filial),\
            f"Falha ao selecionar a filial '{self.filial}' | Encontrado '{filial}'"

    @bot.util.decoradores.prefixar_erro("Falha ao obter a empresa/filial selecionada na janela 'Sistema Fiscal'")
    def obter_empresa_filial_selecionada (self) -> tuple[str, str]:
        """Obter a `(empresa, filial)` selecionada na janela `Sistema Fiscal`"""
        barra_status = bot.sistema.JanelaW32(lambda j: j.titulo == "Sistema Fiscal", aguardar=3)\
                                  .to_uia()\
                                  .elemento\
                                  .encontrar(lambda e: e.class_name == "TStatusBar", aguardar=3)
        empresa, filial = (
            barra_status.encontrar(lambda e: e.texto.lower().startswith(texto), aguardar=3)
                        .texto
                        .split(":")[-1]
                        .strip()
            for texto in ("emp.:", "fil.:")
        )
        return (empresa, filial)

@bot.util.decoradores.prefixar_erro("Falha ao selecionar o módulo 'ADM / NBS Fiscal'")
def abrir_modulo_nbs_fiscal (janela_shortcut: bot.sistema.JanelaW32,
                             imagem: bot.imagem.Imagem | None = IMAGEM_MODULO) -> SelecaoEmpresaFilial:
    """Abrir o módulo `Nbs Fiscal`
    - `imagem` para procurar via imagem
    - `imagem=None` é feito o click em posição esperada na aba `ADM`
    - Retornado `SelecaoEmpresaFilial`"""
    bot.logger.informar(f"Abrindo o módulo 'NBS Fiscal'")
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
    return SelecaoEmpresaFilial()

def fechar_janela_nbs_fiscal (titulo: str = "Sistema Fiscal") -> None:
    """Fechar a janela nbs fiscal `titulo`
    - Usado o `destruir` na janela para encerrar todas as janelas dependentes
    - Ignorado caso não encontre
    - `AssertionError` caso falhe ao encerrar"""
    try:
        janela = bot.sistema.JanelaW32(lambda j: j.titulo == titulo, aguardar=1)
        assert janela.destruir(5), f"Falha ao encerrar a janela nbs fiscal '{titulo}'"
        janela.sleep()
    except AssertionError: raise
    except Exception: return

__all__ = [
    "SelecaoEmpresaFilial",
    "abrir_modulo_nbs_fiscal",
    "fechar_janela_nbs_fiscal",
]