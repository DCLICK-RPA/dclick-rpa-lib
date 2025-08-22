# interno
from .fila import AbaFila
# externo
import bot

def abrir_interface (janela: bot.sistema.JanelaW32) -> AbaFila:
    """Abrir a opção `Interface` na janela `Entrada de Nota Fiscal`
    - Retornado classe de tratamento da janela aberta"""
    janela.to_uia()\
        .elemento\
        .encontrar(lambda e: e.botao and e.texto == "Interface")\
        .clicar()

    try: j = janela.janela_processo(
        lambda j: j.class_name == "TForm_InterfaceCompra" and j.elemento.visivel,
        aguardar = 10
    ).focar()
    except Exception:
        raise Exception("Janela 'Entrada de Nota Fiscal' não abriu conforme esperado")

    return AbaFila(j)

__all__ = [
    "abrir_interface",
]