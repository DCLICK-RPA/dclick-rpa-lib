# externo
import bot

@bot.util.decoradores.prefixar_erro("Falha ao abrir o menu 'Nota Fiscal de Entradas'")
def abrir_menu_nf_entradas (janela_sistema_fiscal: bot.sistema.JanelaW32) -> bot.sistema.JanelaW32:
    """Abrir o menu `Nota Fiscal de Entradas`
    - Retorna a janela de `Entradas`"""
    bot.logger.informar(f"Abrindo o menu 'Nota Fiscal de Entradas'")
    janela_sistema_fiscal.to_uia().menu("Notas Fiscais", "Nota Fiscal de Entradas")
    return bot.sistema.JanelaW32(lambda j: j.titulo == "Entradas", aguardar=10)

__all__ = [
    "abrir_menu_nf_entradas"
]