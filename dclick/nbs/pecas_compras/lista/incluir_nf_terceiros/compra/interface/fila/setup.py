# externo
import bot
from bot.sistema.janela import ElementoW32

@bot.util.decoradores.prefixar_erro_classe("Falha na aba 'Fila' da janela 'Interface de Compra'")
class AbaFila:
    """Representação da aba `Fila` da janela `Interface de Compra`"""

    janela: bot.sistema.JanelaW32

    NOME_ABA = "Fila"
    IMAGEM_BOTAO_CARREGAR = bot.imagem.Imagem.from_base64("iVBORw0KGgoAAAANSUhEUgAAAEUAAAAYCAIAAAAj/6dXAAAB9ElEQVRYCd3B0ancBhQA0bkdTEna0lyBS1qVNB3cgECgh/1CfpKYPWcqPshUfJCp+CBT8UGm4nsqv6j4U03F99Td5WFmgIo/0lR8T91dHmZmd2em4hcqt4r/3FR8T93dmQF2F5gZbhUPasVNrfhvTcXDz58/f/z4wcPu8jszU/GgVvyvpuJB3V0YWJgZdndm+Gp3Z6biQa34hcqlAlSgUoEKULlUXFRuFaByqQAVqHiYipu6uzCwMLAzs7v8zsxUPKgV31MrtQLUClArLmqlVlzUige1Uiu+moqbugssDCzMDLs7M3y1uzNT8aBW/ELlVqkVoFaAykOlVlzUClC5VWrFV1NxU3cXBhYGdmZ2l9+ZmYoHteIrteKiVmoFqBWgVjyoFRe1UisuaqVWfDUVN3UXWJgZ/sbuzkzFg1pxUyu14qJWagWoFaBWXNRKrbiolVpxUSu14qupuKm7CzPDLuf5Po7Xeb6P43We7+N4nef7OF4z7O7MVHylcqu4qNwqtQLUiovKpeKicqsAlVulVnw1FTd1lxl2Oc/3cbzO830cr/N8H8frPN/H8Zphd4GZqfj3qRX/zFTcVGCX83wfx+s838fxOs/3cbzO830crxmeKv4dKreKf2wqHlS+V/Fnm4oPMhUfZCo+yFR8kKn4IFPxQf4CgFekqOafKngAAAAASUVORK5CYII=")
    """Imagem do botão `Carregar` na resolução `1920x1080`"""

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        bot.logger.informar(f"Abrindo a aba '{self.NOME_ABA}' na janela '{janela.titulo}'")
        self.janela = janela
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == self.NOME_ABA and e.item_aba)\
              .clicar()

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == self.NOME_ABA
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

        try: return bot.sistema.JanelaW32(
            lambda j: j.class_name == "TForm_MonitorNFeCompra",
            aguardar = 10
        )
        except Exception:
            raise Exception("Janela do 'Monitor Notas Eletrônicas' não abriu conforme esperado")

__all__ = [
    "AbaFila",
]