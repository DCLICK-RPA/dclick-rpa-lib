# externo
import bot

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
def selecionar_modulo_nbs_fiscal (janela_shortcut: bot.sistema.JanelaW32) -> SelecaoEmpresaFilial:
    """Selecionar o menu do `Nbs Fiscal`
    - Retornado `SelecaoEmpresaFilial`"""
    abas = janela_shortcut.elemento.descendentes(
        lambda elemento: elemento.class_name == "TfcShapeBtn"
    )
    *_, aba_adm = janela_shortcut.ordernar_elementos_coordenada(abas)
    aba_adm.clicar().sleep()

    posicao_nbs_fiscal = janela_shortcut.elemento\
        .encontrar(lambda e: e.class_name == "TfcOutlookPanel")\
        .coordenada\
        .transformar(0.5, 0.26)
    bot.mouse.clicar_mouse(coordenada=posicao_nbs_fiscal)

    try: return SelecaoEmpresaFilial(
        bot.sistema.JanelaW32(lambda j: "Empresa/Filial" in j.titulo, aguardar=10)
                   .focar()
    )
    except Exception:
        raise Exception("Janela de seleção 'Empresa/Filial' não abriu conforme o esperado")

__all__ = [
    "SelecaoEmpresaFilial",
    "selecionar_modulo_nbs_fiscal"
]