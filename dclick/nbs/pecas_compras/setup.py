# std
import re as regex
from typing import Self
# externo
import bot

janela_compras = lambda: bot.sistema.JanelaW32(
    lambda j: j.class_name == "TForm_Principal" and j.visivel,
    aguardar = 10
)

CLASS_NAME_JANELA_INFORMATIVA = "TFrmListaNfeRen"
IMAGEM_MODULO = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADEAAAAwCAIAAAA3ogXuAAAB/ElEQVRYCc3BAY7TCBAAwe6XD/PyvsWsRcLqTglGh6usuBkrbsaKm7HiZqy4GSt+i8q/qLjAipepPKh4pBZacYEVL1MrfqH8UAJacYEVL1MrpfiVAhZacYEVL1Mr5UPxSfmhBLTiAitepn779m1m+EoBC624wIqXqRQQD5QPBQhoxQVWvEO+iyfKp0ArLrDiHSoVPynFB4VAKy6w4h0qFT8pxQeFQCsusOIdKhU/KYXyXaAVF1jxDpUC4pPyKb7TiguseIdK8R+04gIr3qHygorfZcXvUiv+NCtuxoqbseJmrLgZK27Gipux4masuBkrbsaKm7HiZqy4GStuxooHupxq+BusOOnWcNKt4X9nxUm3hr/NipNuDV/ocqgBdDnU6AI1gC6nGkAXqAF0OdRw0AVqeGbFSbeGZ7o1HHRrdGsA3RpAt0a3hoNujW4Nz3RrdGsA3RoeWHHSreGZbg0H3RrdGkC3BtCt0a3hoFujW8NBl1MNoFvDF1acdGt4plvDQbdGtwbQrQF0a3RrOOjW6NYAujUcdGs46NbwzIqTbg0n3RrdGg66Nbo1gG4NoFujW8NBt0a3BtCt4aBbo1sD6NbwwIoHupxqOOhyqAF0awDdGkC3RpdTDaBbw0GXUw2gC9TwzIo/RLeGy6z4Q3RruMyKm7HiZqy4GStu5h8cwtCwMlN0DQAAAABJRU5ErkJggg==")
"""Imagem do botão do módulo na resolução `1920x1080`"""

@bot.util.decoradores.prefixar_erro("Falha ao abrir o módulo 'Peças / Compras'")
@bot.util.decoradores.retry()
def abrir_modulo (
        janela_shortcut: bot.sistema.JanelaW32,
        imagem: bot.imagem.Imagem | None = IMAGEM_MODULO
    ) -> bot.sistema.JanelaW32:
    """Abrir o módulo `Compras` na aba `Peças`
    - `imagem` para procurar via imagem
    - `imagem=None` é feito o click em posição esperada na aba
    - Fechado possível janela informativa
    - Retornado a janela `Compras`"""
    bot.logger.informar(f"Abrindo o módulo 'Peças / Compras'")
    abas = janela_shortcut.focar().elemento.descendentes(
        lambda elemento: elemento.class_name == "TfcShapeBtn"
                         and elemento.visivel,
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
        bot.mouse.mover((0, 0)) # Remover mouse da janela antes de procurar
        posicao = imagem.procurar_imagem(regiao=coordenada_painel, cinza=True, segundos=3)
        assert posicao, "Imagem do módulo não foi encontrada"
    bot.mouse.mover(posicao).clicar()

    janela = bot.sistema.JanelaW32.aguardar_nova_janela()
    if janela.class_name == CLASS_NAME_JANELA_INFORMATIVA:
        assert janela.fechar(), "Falha ao fechar janela informativa"

    try: return janela_compras().focar()
    except Exception: raise Exception("Janela 'Compras' não abriu conforme esperado")

def fechar_janela_modulo (titulo: str = "Compras") -> None:
    """Fechar a janela do módulo
    - Usado o `destruir` na janela para encerrar todas as janelas dependentes
    - Ignorado caso não encontre
    - `AssertionError` caso falhe ao encerrar"""
    try:
        janela = bot.sistema.JanelaW32(lambda j: titulo in j.titulo, aguardar=1)
        assert janela.destruir(5), f"Falha ao encerrar a janela do módulo '{titulo}'"
        janela.sleep()
    except AssertionError: raise
    except Exception: return

@bot.util.decoradores.prefixar_erro_classe("Falha ao selecionar a empresa/filial do módulo")
class SelecaoEmpresaFilial:
    """Classe para tratar a seleção da empresa e filial do módulo
    - Necessário checar se a empresa já está selecionada pois a selecionada não aparece na seleção

    ## Exemplo
    ```
    nome_empresa = "Artvel Mogi Mirim"
    selecao = pecas_compras.SelecaoEmpresaFilial(nome_empresa)
    if not selecao.checar_empresa_selecionada():
        selecao.abrir_janela_via_atalho()\\
            .preencher_nome_empresa()\\
            .clicar_bota_ok()
        assert selecao.checar_empresa_selecionada(), f"Falha ao selecionar a empresa '{nome_empresa}'"
    ```
    """

    janela: bot.sistema.JanelaW32
    janela_compras: bot.sistema.JanelaW32
    nome_empresa: str

    def __init__ (self, nome_empresa: str) -> None:
        bot.logger.informar("Selecionando a empresa/filial")
        self.nome_empresa = nome_empresa
        self.janela_compras = janela_compras().focar()

    def abrir_janela_via_atalho (self) -> Self:
        """Abrir a janela de seleção via atalho"""
        try:
            self.janela_compras.focar().elemento.atalho("ctrl", "l")
            self.janela = bot.sistema.JanelaW32(lambda j: j.class_name == "TFrmSelEmpresa")
            return self
        except Exception as erro: raise Exception(f"Janela da seleção não abriu conforme esperado; {erro}")

    def preencher_nome_empresa (self) -> Self:
        """Preencher o campo nome empresa"""
        *_, elemento = self.janela.ordernar_elementos_coordenada(
            self.janela.elemento.descendentes(lambda e: e.class_name == "TwwIncrementalSearch")
        )
        elemento.digitar(self.nome_empresa, virtual=False)\
                .apertar("tab")
        return self

    def clicar_bota_ok (self) -> Self:
        """Clicar no botão `OK` para alterar a empresa/filial"""
        self.janela.to_uia()\
            .elemento\
            .encontrar(lambda e: e.botao and e.texto == "OK")\
            .clicar()
        return self

    def checar_empresa_selecionada (self) -> bool:
        """Checar se a empresa selecionado possui `self.nome_empresa`"""
        empresa = self.obter_empresa_selecionada()
        return bot.util.normalizar(self.nome_empresa) in bot.util.normalizar(empresa)

    def obter_empresa_selecionada (self) -> str:
        """Obter a `empresa` selecionada na janela"""
        return self.janela_compras.aguardar().to_uia()\
            .elemento\
            .encontrar(lambda e: e.class_name == "TStatusBar", aguardar=3)\
            .encontrar(lambda e: regex.search(r"empresa\s*:", e.texto.lower()), aguardar=3)\
            .texto\
            .split(":")[1].strip()

__all__ = [
    "abrir_modulo",
    "fechar_janela_modulo",
    "SelecaoEmpresaFilial",
]