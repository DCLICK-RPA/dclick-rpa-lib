# std
from datetime import date
from typing import Self
# externo
import bot
from bot.sistema.janela import ElementoW32

@bot.util.decoradores.adicionar_prefixo_erro("Falha ao abrir o menu 'Impostos a Recolher'")
def abrir_menu_impostos_a_recolher (janela_sistema_fiscal: bot.sistema.JanelaW32) -> bot.sistema.JanelaW32:
    """Clicar no botão para abrir `Impostos a Recolher`
    - Retorna a janela `Impostos a Recolher`"""
    janela_sistema_fiscal\
        .to_uia()\
        .menu("Outros", "Impostos a Recolher")

    return janela_sistema_fiscal\
        .janela_processo(lambda j: j.titulo == "Impostos a Recolher", aguardar=10)

class AbaLista:
    """Representação da aba `Lista` na janela `Impostos a Recolher`"""

    full_hd: bool
    janela: bot.sistema.JanelaW32

    IMAGEM_OCULOS = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAUCAYAAACTQC2+AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACJSURBVEhL7ZILCoAwDEN7/1PtZtWAK8W1NkwZIj4ofkjzBiq6iHeJRERba8fTHKUIEn9liA52ue3LWVF2sHR7CBIin6FEUWklGoor0RMScCmqCiPYg9kb/CUI+Dm/yzIMJrIi3O/TSz1MJsNSWOgFNoGoymRY6puiJd8IYMlPBJOJ4JM3+UWTqG75oDTOWTdCaAAAAABJRU5ErkJggg==")
    """Imagem do botão `Procurar`, ícone de um Óculos, na resolução `1920x1080`"""
    IMAGEM_SETA_ENVIAR_SELECIONADOS_COMPROMISSO = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAWCAYAAADafVyIAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAABiSURBVEhL7Y0xDsAwCAP5/6cpquQMcZDjoVM5yQyB+CI/ZgSSHwki4o2LJahhi2wBciuiC3w8pQZl7Rpo0xWpdCJ6weEpNShr19BvNnaBKga24LYYWAKnGPg/TEYgGYEg8wEHi4vXA0x4ogAAAABJRU5ErkJggg==")
    """Imagem do botão `Enviar apenas selecionados para compromisso`, ícone de uma seta vermelha, na resolução `1920x1080`"""
    IMAGEM_SETA_ENVIAR_TODOS_COMPROMISSO = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAXCAYAAADk3wSdAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACESURBVEhL7dDtCoQwDETRvHl982qwgzSd9MPoD8ELA7tue2CV/EIfReX4povWEIAjeBe9i9MrDNbN5h5lKDbKPcIwO6/OTy3izVY/YjdWVro+kUS2qaWUyo0zF2WX7SyGKKqHGYJ5GKIog3QjDDVoBEMVav/2KoYqNIoh+k6j/ejT5bwD5EybQbbvwc0AAAAASUVORK5CYII=")
    """Imagem do botão `Enviar todos para compromisso`, ícone de uma seta azul, na resolução `1920x1080`"""

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == "Lista" and e.item_aba)\
              .clicar()
        resolucao_atual, _ = bot.sistema.informacoes_resolucao()
        self.full_hd = resolucao_atual == (1920, 1080)

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == "Lista"
        )

    @property
    def painel_superior_aba (self) -> ElementoW32:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_aba.filhos(lambda e: e.class_name == "TPanel")
        )
        assert elementos, "Painel com elementos não encontrado"
        return elementos[0]

    @property
    def painel_grid (self) -> ElementoW32:
        return self.painel_aba.encontrar(
            lambda e: e.class_name == "TwwDBGrid"
        )

    def preencher_fornecedor (self, texto: str) -> Self:
        """Preencher o campo `Fornecedor` e apertado `TAB` para confirmar
        - Erro caso apareça diálogo com mensagem"""
        self.painel_superior_aba\
            .encontrar(lambda e: e.class_name == "TCPF_CGC")\
            .apertar("backspace")\
            .digitar(texto)\
            .apertar("tab")

        if dialogo := self.janela.dialogo(aguardar=1):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao preencher o campo fornecedor com '{texto}': '{mensagem}'")

        return self

    def preencher_data_inicio (self, data: date) -> Self:
        """Preencher o campo data início"""
        elemento, *_ = self.janela.ordernar_elementos_coordenada(
            self.painel_superior_aba
                .filhos(lambda e: e.class_name == "TDateTimePicker")
        ) or [None]
        assert elemento, "Elemento 'Data Início' não encontrado"

        data_formatada = data.strftime(r"%d/%m/%Y")
        dia, mes, ano = data_formatada.split("/")

        posicao_dia = elemento.coordenada.transformar(0.25)
        bot.mouse.clicar_mouse(coordenada=posicao_dia)
        elemento.digitar(dia, virtual=False, focar=False)\
            .apertar("right").digitar(mes, virtual=False, focar=False)\
            .apertar("right").digitar(ano, virtual=False, focar=False)

        texto = elemento.to_uia().texto
        assert data_formatada == texto, f"Falha ao preencher a elemento 'Data Início' | Esperado '{data_formatada}' | Encontrado '{texto}'"
        return self

    def preencher_data_fim (self, data: date) -> Self:
        """Preencher o campo data fim"""
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_superior_aba
                .filhos(lambda e: e.class_name == "TDateTimePicker")
        )
        assert len(elementos) >= 2, "Elemento 'Data Fim' não encontrado"
        elemento = elementos[1]

        data_formatada = data.strftime(r"%d/%m/%Y")
        dia, mes, ano = data_formatada.split("/")

        posicao_dia = elemento.coordenada.transformar(0.25)
        bot.mouse.clicar_mouse(coordenada=posicao_dia)
        elemento.digitar(dia, virtual=False, focar=False)\
            .apertar("right").digitar(mes, virtual=False, focar=False)\
            .apertar("right").digitar(ano, virtual=False, focar=False)

        texto = elemento.to_uia().texto
        assert data_formatada == texto, f"Falha ao preencher a elemento 'Data Fim' | Esperado '{data_formatada}' | Encontrado '{texto}'"
        return self

    def clicar_oculos_via_imagem (self) -> Self:
        """Clicar no ícone do óculos, para realizar a busca
        - Erro caso apareça diálogo com mensagem"""
        assert self.full_hd, "Esperado resolução '1920x1080' para encontrar a imagem do botão"

        coordenada = self.IMAGEM_OCULOS.procurar_imagem(
            regiao = self.painel_superior_aba.coordenada,
            segundos = 5
        )
        assert coordenada, f"Coordenada do botão não encontrado na janela '{self.janela.titulo}'"

        bot.mouse.clicar_mouse(coordenada=coordenada)
        self.painel_grid.sleep(2).aguardar()

        if dialogo := self.janela.dialogo():
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao clicar na imagem do óculos para procurar: '{mensagem}'")

        return self

    def obter_linhas_registro_grid_via_ocr (self, leitor: bot.imagem.LeitorOCR) -> list[tuple[str, tuple[int, int]]]:
        """Obter o texto e posição dos registros no elemento `painel_grid`
        - Feito `upper()` nos textos e separado por espaço"""
        coordenada = self.painel_grid.coordenada
        x_central = coordenada.x + (coordenada.largura // 2)
        extracao = leitor.ler_tela(self.painel_grid.coordenada)
        return [
            (linha.upper(), (x_central, y))
            for index, (linha, y) in enumerate(leitor.concatenar_linhas(extracao))
            if index != 0 # remover a linha com o nome das colunas
        ]

    def clicar_seta_enviar_selecionados_compromisso_via_imagem (self) -> Self:
        """Clicar na seta vermelha para enviar os registros selecionados para compromisso
        - O registro é removido do grid para a aba `Compromisso`
        - Erro caso apareça diálogo com mensagem"""
        assert self.full_hd, "Esperado resolução '1920x1080' para encontrar a imagem do botão"

        coordenada = self.IMAGEM_SETA_ENVIAR_SELECIONADOS_COMPROMISSO.procurar_imagem(
            regiao = self.painel_superior_aba.coordenada,
            segundos = 5
        )
        assert coordenada, f"Coordenada do botão não encontrado na janela '{self.janela.titulo}'"

        bot.mouse.clicar_mouse(coordenada=coordenada)
        self.painel_grid.aguardar()

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao clicar na imagem para enviar os registro selecionados para compromisso: '{mensagem}'")

        return self

    def clicar_seta_enviar_todos_compromisso_via_imagem (self) -> Self:
        """Clicar na seta azul para enviar todos os registros para compromisso
        - O registro é removido do grid para a aba `Compromisso`
        - Erro caso apareça diálogo com mensagem"""
        assert self.full_hd, "Esperado resolução '1920x1080' para encontrar a imagem do botão"

        coordenada = self.IMAGEM_SETA_ENVIAR_TODOS_COMPROMISSO.procurar_imagem(
            regiao = self.painel_superior_aba.coordenada,
            segundos = 5
        )
        assert coordenada, f"Coordenada do botão não encontrado na janela '{self.janela.titulo}'"

        bot.mouse.clicar_mouse(coordenada=coordenada)
        self.painel_grid.aguardar()

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao clicar na imagem para enviar todos os registro para compromisso: '{mensagem}'")

        return self

class AbaCompromisso:
    """Representação da aba `Compromisso` na janela `Impostos a Recolher`"""

    full_hd: bool
    janela: bot.sistema.JanelaW32

    IMAGEM_GERAR_COMPROMISSO = bot.imagem.Imagem.from_base64("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAVCAYAAACpF6WWAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACHSURBVDhP5Y+BCsAgCAX9/59uqHvmQq0xgkEHZqvX1aht4AApEVmN/Eta8Um6/NLqt0ZK6VOE0Jo4QqVcTugvicrguf++kRUeenjeLbsmRUA7XjbWDEmIzsJxj2TZJbLCg24ioB2HooNMticrPPQAQr1n0gxJ+xsx9xVR7b97gmOLtOJoaWsX3JgHTiCw/GYAAAAASUVORK5CYII=")
    """Imagem do botão `Procurar`, na resolução `1920x1080`"""

    def __init__ (self, janela: bot.sistema.JanelaW32) -> None:
        self.janela = janela
        janela.to_uia()\
              .elemento\
              .encontrar(lambda e: e.texto == "Compromisso" and e.item_aba)\
              .clicar()
        resolucao_atual, _ = bot.sistema.informacoes_resolucao()
        self.full_hd = resolucao_atual == (1920, 1080)

    @property
    def painel_aba (self) -> ElementoW32:
        return self.janela.elemento.encontrar(
            lambda e: e.class_name == "TTabSheet"
                      and e.texto == "Compromisso"
        )

    @property
    def painel_superior_aba (self) -> ElementoW32:
        elementos = self.janela.ordernar_elementos_coordenada(
            self.painel_aba.filhos(lambda e: e.class_name == "TPanel")
        )
        assert elementos, "Painel com elementos não encontrado"
        return elementos[0]

    @property
    def painel_grid (self) -> ElementoW32:
        return self.painel_aba.encontrar(
            lambda e: e.class_name == "TwwDBGrid"
        )

    def preencher_vencimento (self, data: date) -> Self:
        """Preencher o campo vencimento"""
        elemento = self.painel_aba.encontrar(
            lambda e: e.class_name == "TDateTimePicker"
        )

        data_formatada = data.strftime(r"%d/%m/%Y")
        dia, mes, ano = data_formatada.split("/")

        posicao_dia = elemento.coordenada.transformar(0.1)
        bot.mouse.clicar_mouse(coordenada=posicao_dia)
        elemento.digitar(dia, virtual=False, focar=False)\
            .apertar("right").digitar(mes, virtual=False, focar=False)\
            .apertar("right").digitar(ano, virtual=False, focar=False)

        texto = elemento.to_uia().texto
        assert data_formatada == texto, f"Falha ao preencher a elemento 'Vencimento' | Esperado '{data_formatada}' | Encontrado '{texto}'"
        return self

    def clicar_botao_gerar_compromisso_via_imagem (self) -> bot.sistema.JanelaW32:
        """Clicar no botão gerar compromisso para realizar a busca
        - Erro caso apareça diálogo com mensagem
        - Retornado janela aberta `Compromisso`"""
        assert self.full_hd, "Esperado resolução '1920x1080' para encontrar a imagem do botão"

        coordenada = self.IMAGEM_GERAR_COMPROMISSO.procurar_imagem(
            regiao = self.painel_superior_aba.coordenada,
            segundos = 5
        )
        assert coordenada, f"Coordenada do botão não encontrado na janela '{self.janela.titulo}'"

        bot.mouse.clicar_mouse(coordenada=coordenada)

        if dialogo := self.janela.dialogo(aguardar=0.5):
            mensagem = dialogo.elemento.textos()
            dialogo.clicar("OK")
            raise Exception(f"Falha ao clicar na imagem do botão para gerar compromisso: '{mensagem}'")

        try: return self.janela.janela_processo(
            lambda j: j.titulo == "Compromisso", aguardar=10
        )
        except Exception:
            raise Exception("Janela 'Compromisso' não foi encontrada")

__all__ = [
    "AbaLista",
    "AbaCompromisso",
    "abrir_menu_impostos_a_recolher"
]