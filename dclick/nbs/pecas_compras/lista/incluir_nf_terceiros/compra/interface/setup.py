# std
from typing import Self
# externo
import bot
from bot.sistema.janela import ElementoW32

def abrir_interface (janela: bot.sistema.JanelaW32) -> bot.sistema.JanelaW32:
    """Abrir a opção `Interface` na janela `Entrada de Nota Fiscal`
    - Retornado janela `Interface de Compra`"""
    bot.logger.informar(f"Abrindo a opção 'Interface' na {janela!r}")

    janela.to_uia()\
        .elemento\
        .encontrar(lambda e: e.botao and e.texto == "Interface" and e.visivel)\
        .clicar()

    try: return janela.janela_processo(lambda j: j.class_name == "TForm_InterfaceCompra" and j.visivel,
                                       aguardar = 10)\
                      .focar()
    except Exception:
        raise Exception("Janela 'Interface de Compra' não abriu conforme esperado")

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Fila' da janela 'Interface de Compra'")
class AbaFila:
    """Representação da aba `Fila` da janela `Interface de Compra`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Fila"
    IMAGEM_BOTAO_CARREGAR = bot.imagem.Imagem.from_base64("iVBORw0KGgoAAAANSUhEUgAAAEUAAAAYCAIAAAAj/6dXAAAB9ElEQVRYCd3B0ancBhQA0bkdTEna0lyBS1qVNB3cgECgh/1CfpKYPWcqPshUfJCp+CBT8UGm4nsqv6j4U03F99Td5WFmgIo/0lR8T91dHmZmd2em4hcqt4r/3FR8T93dmQF2F5gZbhUPasVNrfhvTcXDz58/f/z4wcPu8jszU/GgVvyvpuJB3V0YWJgZdndm+Gp3Z6biQa34hcqlAlSgUoEKULlUXFRuFaByqQAVqHiYipu6uzCwMLAzs7v8zsxUPKgV31MrtQLUClArLmqlVlzUige1Uiu+moqbugssDCzMDLs7M3y1uzNT8aBW/ELlVqkVoFaAykOlVlzUClC5VWrFV1NxU3cXBhYGdmZ2l9+ZmYoHteIrteKiVmoFqBWgVjyoFRe1UisuaqVWfDUVN3UXWJgZ/sbuzkzFg1pxUyu14qJWagWoFaBWXNRKrbiolVpxUSu14qupuKm7CzPDLuf5Po7Xeb6P43We7+N4nef7OF4z7O7MVHylcqu4qNwqtQLUiovKpeKicqsAlVulVnw1FTd1lxl2Oc/3cbzO830cr/N8H8frPN/H8Zphd4GZqfj3qRX/zFTcVGCX83wfx+s838fxOs/3cbzO830crxmeKv4dKreKf2wqHlS+V/Fnm4oPMhUfZCo+yFR8kKn4IFPxQf4CgFekqOafKngAAAAASUVORK5CYII=")
    """Imagem do botão `Carregar` na resolução `1920x1080`"""

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
              .clicar()

        if dialogo := self.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao abrir a aba: '{dialogo.texto}'")

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA
                      and e.visivel
        )

    def abrir_monitor_notas_eletronicas (self) -> bot.sistema.JanelaW32:
        """Clicar no botão `Carregar` e selecionar as opções `NF-e / Monitor`
        - Retornado janela `Monitor Notas Eletrônicas`"""
        regiao = self.painel_aba.coordenada
        coordenada = self.IMAGEM_BOTAO_CARREGAR.procurar_imagem(regiao=regiao, cinza=True, segundos=5)
        assert coordenada, "Imagem do botão 'Carregar' não foi encontrado"

        class_name_dialogo = "TMessageForm"
        bot.mouse.mover(coordenada).clicar()
        for texto in ("NF-e", "Monitor"):
            dialogo = self.janela.dialogo(class_name_dialogo, aguardar=5)
            assert dialogo, f"Diálogo contendo botão '{texto}' não foi encontrado"
            assert dialogo.clicar(texto), f"Diálogo de confirmação não fechou conforme esperado"

        try: return bot.sistema.JanelaW32(lambda j: j.class_name == "TForm_MonitorNFeCompra" and j.visivel,
                                          aguardar = 10)\
                               .focar()
        except Exception:
            raise Exception("Janela 'Monitor Notas Eletrônicas' não abriu conforme esperado")

@bot.util.decoradores.prefixar_erro_classe("Falha na janela 'Interface de Compra CFOP'")
class InterfaceCompraCFOP:

    janela: bot.sistema.JanelaUIA

    def __init__ (self) -> None:
        self.janela = bot.sistema.JanelaUIA(
            lambda j: j.class_name == "TForm_InterfaceCFOP" and j.visivel,
            aguardar = 5
        )
        bot.mouse.mover(self.janela.coordenada.topo())

    @property
    def campo_tributados_ativo (self) -> bool:
        """Checar se o campo `Tributados` está ativo para ser modificado"""
        return self.janela.elemento["TwwDBLookupCombo", 0].ativo

    def campo_tributados_selecionar_primeiro (self) -> Self:
        """Selecionar a primeira opção no campo `Tributados`"""
        elemento = self.janela.elemento["TwwDBLookupCombo", 0]\
            .atalho("alt", "down")\
            .apertar("up", "tab", focar=False)
        assert elemento.valor, "Nenhuma opção selecionada no campo 'Tributados'"
        return self

    @property
    def campo_fonte_ativo (self) -> bool:
        """Checar se o campo `Fonte` está ativo para ser modificado"""
        return self.janela.elemento["TwwDBLookupCombo", 2].ativo

    def campo_fonte_selecionar_primeiro (self) -> Self:
        """Selecionar a primeira opção no campo `Fonte`"""
        elemento = self.janela.elemento["TwwDBLookupCombo", 2]\
            .atalho("alt", "down")\
            .apertar("up", "tab", focar=False)
        assert elemento.valor, "Nenhuma opção selecionada no campo 'Fonte'"
        return self

    @property
    def campo_combustivel_ativo (self) -> bool:
        """Checar se o campo `Combustível` está ativo para ser modificado"""
        return self.janela.elemento["TwwDBLookupCombo", 3].ativo

    def clicar_ok (self) -> None:
        """Clicar no botão `OK`
        - Erro caso algum diálogo apareça"""
        self.janela.elemento["OK"].clicar()
        if dialogo := self.janela.dialogo(aguardar=0.3):
            raise Exception(f"Diálogo encontrado ao clicar em OK: '{dialogo.texto}'")
        assert self.janela.fechar(), "Janela não fechada conforme esperado"

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Definir Tributação/CFOP' da janela 'Interface de Compra'")
class AbaTributacaoCFOP:
    """Representação da aba `Definir Tributação/CFOP` da janela `Interface de Compra`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Definir Tributação/CFOP"

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela.focar()
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
              .clicar()

        if dialogo := self.janela.dialogo(aguardar=0.5):
            raise Exception(f"Diálogo encontrado ao abrir a aba: '{dialogo.texto}'")

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA
                      and e.visivel
        )

    @property
    def grid (self) -> ElementoW32:
        return self.janela.elemento[0].encontrar(lambda e: e.class_name == "TwwDBGrid"
                                                           and e.visivel)

    def abrir_definir_cfop (self, xy_offset_grid: tuple[float, float] = (0.1, 0.09)) -> InterfaceCompraCFOP:
        """Abrir a opção `Definir CFOP` de um registro no grid
        - `xy_offset_grid` para mover o mouse para o registro correto. Default primeiro"""
        posicao = self.grid.coordenada.transformar(*xy_offset_grid)
        bot.mouse.mover(posicao).clicar(botao="right")

        assert (popup := self.janela.popup(aguardar=3)), "Popup para definir o CFOP não foi encontrado"
        popup.menu("Definir CFOP")

        return InterfaceCompraCFOP()

@bot.util.decoradores.prefixar_erro_classe("Falha na confirmação da janela 'Interface de Compra'")
class Confirmar:
    """Representação do processo de Confirmação na janela `Interface de Compra`"""

    janela: bot.sistema.JanelaW32

    IMAGEM_BOTAO_ACEITAR = bot.imagem.Imagem.from_base64("iVBORw0KGgoAAAANSUhEUgAAAGkAAAAeCAIAAACgx6cUAAABrElEQVRoBe3B0WkkWRAAwSwP0n8r04M69sFA6+5n1cwITnTEVDxumYrHLVPxuGUqHrdMxeOWqXjcMhWPW6bik1Sg4teZio9Rd4GdmYrfZSo+Rt1dmBkqfpep+Bh1F9iZqfhdpuJj1N2FmaHiL6gV36FW/Lip+CR1d2Fm+JeK/1Arvk+t+EFT8W4qF7vAwszALjMcFV+plVrxTWrFD5qKd1N3FwYWBhYGdmbYZYaj4iu1UiteVI6KQ+WoALVSgQpQOSpABSreaireTeXYBRYGFmYGdpnhqLhQKw61AtSKQ63UikOt1Eqt+Eqt1Ip3m4p3U3cXBhYGFgZ2ZthlhqPiQq041ApQKy5ULiq1UisOlZdKrXi3qfgAFdgFFgYWZgZ2meGouFC5qAC14kKtuFArtQLUikOt1Ip3m4oPUHeBhYGFmeGPXWY4Kl7Uigu1UisOtVIrDrVSK7UC1IpDrdSKd5uKz1C5qFSOXWaoeFErLtQKUDkqDpWjAtQKUCtA5aVSK95tKn6WylHxfzYVj1um4nHLVDxumYrHLVPxuGUqHrdMxeOWqXjcMhWPW/4BBHZtjv1KCgIAAAAASUVORK5CYII=")
    """Imagem do botão `Aceitar` na resolução `1920x1080`"""

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Confirmando na janela '{janela.titulo}'")
        self.janela = janela

    @property
    def painel_botao_confirmar (self) -> ElementoW32:
        return self.janela.elemento[-1]

    def clicar_aceitar_via_imagem (self) -> Self:
        """Clicar no botão `Aceitar` procurando pela Imagem"""
        coordenada = self.IMAGEM_BOTAO_ACEITAR.procurar_imagem(
            regiao = self.painel_botao_confirmar.coordenada,
            segundos = 5
        )
        assert coordenada, "Imagem do botão 'Aceitar' não foi encontrada"
        bot.mouse.mover(coordenada).clicar()
        return self

    def condicao_sucesso (self) -> None:
        """Condição esperada para o sucesso após clicar no botão `Aceitar`
        - Nenhum diálogo do windows aberto
        - Confirmado janela `TMessageForm` caso apareça
        - `AssertionError` erro caso a janela não feche"""
        self.janela.aguardar()
        if dialogo := self.janela.dialogo(aguardar=0.2):
            raise Exception(f"Diálogo após clicar em `Aceitar` não esperado: {dialogo.texto}")

        try: self.janela.janela_processo(lambda j: j.class_name == "TMessageForm",
                                         aguardar = 0.2)\
                        .elemento\
                        .encontrar(lambda e: e.texto.lower() == "sim")\
                        .clicar()
        except Exception: pass

        assert self.janela.fechar(), "Janela não fechou após confirmação"

__all__ = [
    "abrir_interface",
    "AbaFila",
    "AbaTributacaoCFOP",
    "Confirmar",
]