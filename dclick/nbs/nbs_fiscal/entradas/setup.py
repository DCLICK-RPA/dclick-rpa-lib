# externo
import bot

@bot.util.decoradores.adicionar_prefixo_erro("Falha ao abrir o menu 'Nota Fiscal - Entradas'")
def abrir_menu_entradas (janela_sistema_fiscal: bot.sistema.JanelaW32) -> bot.sistema.JanelaW32:
    """Clicar no botão para abrir a `Nota Fiscal - Entradas`
    - Retorna a janela de `Entradas`"""
    *_, painel = janela_sistema_fiscal.ordernar_elementos_coordenada(
        janela_sistema_fiscal.elemento.descendentes(lambda e: e.class_name == "TPanel")
    )
    posicao_botao = painel.coordenada.transformar(0.15, 0.5)
    bot.mouse.clicar_mouse(coordenada=posicao_botao)

    return bot.sistema.JanelaW32(lambda j: j.titulo == "Entradas", aguardar=10)

__all__ = [
    "abrir_menu_entradas"
]