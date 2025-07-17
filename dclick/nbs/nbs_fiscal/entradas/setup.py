# externo
import bot

IMAGEM_BOTAO = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB8AAAAdCAYAAABSZrcyAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEpSURBVEhL7ZIBDoMwDAP7dJ7Gk/gBw4rcZkmaFqaNaZolK6MkvjAo27btZ1xK2SPhPOrPfBm+rmv1six/+CmncARqA4Tag/O+dpRLd+EYtJqBW2ULDOGlIFg8A9f90Gl4A+Ovuw7XOSEnPFRDGiLhOVxb54Qcd1AH2vbWkIYQ7i0ZEK4dyx0cTdJMuARraTCt1cBSeeZYTxcOLNd8MiqCo6f/7uMFBnD5yKBsAQvmfcnoP32Fe3ALQjAr+6AMTLU8v0ACb0Bb2ZuBWW2egzNMC8MRmBUzIzCrFReocGtoZoEMzN82Gzbw9veI+wtEoKhCvewBXJpeUZY7AYdx76qjPHga/g6fhusn6hvvO57XvgA/3uLQvwlH8Izjee3v+uA+6wq/yzfCt/0BB6hvC0Q58ecAAAAASUVORK5CYII=")
"""Imagem do botão `Nota Fiscal - Entradas` na resolução `1920x1080`"""

@bot.util.decoradores.prefixar_erro("Falha ao abrir o menu 'Nota Fiscal - Entradas'")
def abrir_menu_entradas (janela_sistema_fiscal: bot.sistema.JanelaW32,
                         imagem: bot.imagem.Imagem | None = IMAGEM_BOTAO) -> bot.sistema.JanelaW32:
    """Clicar no botão para abrir a `Nota Fiscal - Entradas`
    - `imagem` para procurar via imagem
    - `imagem=None` é feito o click em posição esperada
    - Retorna a janela de `Entradas`"""
    *_, painel = janela_sistema_fiscal.ordernar_elementos_coordenada(
        janela_sistema_fiscal.elemento.filhos(lambda e: e.class_name == "TPanel", aguardar=3)
    )

    if imagem is None:
        posicao_botao = painel.coordenada.transformar(0.15, 0.5)
    else:
        posicao_botao = imagem.procurar_imagem(regiao=painel.coordenada, segundos=3)
        assert posicao_botao, "Imagem do botão não foi encontrada"

    bot.mouse.clicar_mouse(coordenada=posicao_botao)
    return bot.sistema.JanelaW32(lambda j: j.titulo == "Entradas", aguardar=10)

__all__ = [
    "abrir_menu_entradas"
]