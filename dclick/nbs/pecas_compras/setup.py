# externo
import bot

IMAGEM_MODULO = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAwCAIAAAA3ogXuAAAB/ElEQVRYCc3BAY7TCBAAwe6XD/PyvsWsRcLqTglGh6usuBkrbsaKm7HiZqy4GSt+i8q/qLjAipepPKh4pBZacYEVL1MrfqH8UAJacYEVL1MrpfiVAhZacYEVL1Mr5UPxSfmhBLTiAitepn779m1m+EoBC624wIqXqRQQD5QPBQhoxQVWvEO+iyfKp0ArLrDiHSoVPynFB4VAKy6w4h0qFT8pxQeFQCsusOIdKhU/KYXyXaAVF1jxDpUC4pPyKb7TiguseIdK8R+04gIr3qHygorfZcXvUiv+NCtuxoqbseJmrLgZK27Gipux4masuBkrbsaKm7HiZqy4GStuxooHupxq+BusOOnWcNKt4X9nxUm3hr/NipNuDV/ocqgBdDnU6AI1gC6nGkAXqAF0OdRw0AVqeGbFSbeGZ7o1HHRrdGsA3RpAt0a3hoNujW4Nz3RrdGsA3RoeWHHSreGZbg0H3RrdGkC3BtCt0a3hoFujW8NBl1MNoFvDF1acdGt4plvDQbdGtwbQrQF0a3RrOOjW6NYAujUcdGs46NbwzIqTbg0n3RrdGg66Nbo1gG4NoFujW8NBt0a3BtCt4aBbo1sD6NbwwIoHupxqOOhyqAF0awDdGkC3RpdTDaBbw0GXUw2gC9TwzIo/RLeGy6z4Q3RruMyKm7HiZqy4GStu5h8cwtCwMlN0DQAAAABJRU5ErkJggg==")
"""Imagem do botão do módulo na resolução `1920x1080`"""

@bot.util.decoradores.prefixar_erro("Falha ao abrir o módulo 'Peças / Compras'")
def abrir_modulo (janela_shortcut: bot.sistema.JanelaW32,
                  imagem: bot.imagem.Imagem | None = IMAGEM_MODULO) -> None:
    """Abrir o módulo `Compras` na aba `Peças`
    - `imagem` para procurar via imagem
    - `imagem=None` é feito o click em posição esperada na aba"""
    bot.logger.informar(f"Abrindo o módulo 'Peças / Compras'")
    abas = janela_shortcut.elemento.descendentes(
        lambda elemento: elemento.class_name == "TfcShapeBtn",
        aguardar = 5
    )
    janela_shortcut.ordernar_elementos_coordenada(abas)
    assert len(abas) >= 3, "Aba 'Peças' não foi localizada"

    abas[2].clicar()
    coordenada_painel = janela_shortcut.elemento\
        .focar()\
        .encontrar(lambda e: e.visivel and e.class_name == "TfcOutlookPanel", aguardar=2)\
        .coordenada

    if imagem is None:
        posicao = coordenada_painel.transformar(0.5, 0.03)
    else:
        posicao = imagem.procurar_imagem(regiao=coordenada_painel, cinza=True, segundos=3)
        assert posicao, "Imagem do módulo não foi encontrada"

    bot.mouse.clicar_mouse(coordenada=posicao)
    # return SelecaoEmpresaFilial()

__all__ = [
    "abrir_modulo"
]