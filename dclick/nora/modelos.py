# std
from inspect import isclass
from datetime import datetime as Datetime
from typing import Literal, TypeAliasType, get_args, get_origin
# interno
from dclick.nora.campos import CampoObrigatorio, CampoOpcional, TiposValores, Numerico

type TStatus = Literal["pending", "processing", "success", "error"]

class Agent:
    id: str
    code: str
    name: str
    description: str | None
    isActive: bool

class Extraction:

    id: str
    """UUID da extração criada"""
    trackingCode: str
    """Código para acompanhar o progresso da extração"""
    status: TStatus
    """Status atual da extração
    - pending = aguardando
    - processing = em andamento
    - success = concluída com sucesso
    - error = concluída com erro"""
    createdAt: str
    """Datetime de criação formato ISO"""
    totalTokens: int | None
    """Total de tokens consumidos"""
    resultJson: str | None
    """Resultado da extração caso `status = success` no formato string de um Object json"""
    confidenceJson: str | None
    """Confiança da extração caso `status = success` no formato string de um Object json"""
    errorMessage: str | None
    """Mensagem de erro caso `status = error`"""
    agent: Agent
    """Informações sobre o Agente de extração"""

    @property
    def data_criacao (self) -> Datetime:
        return Datetime.fromisoformat(self.createdAt)

class ResponseExecutar:

    trackingCode: str
    """Código para acompanhar o progresso da extração"""
    extractionId: str
    """UUID da extração criada"""
    status: str
    """Status inicial da extração
    - `pending`"""
    message: str

class ResponseConsultar:

    extraction: Extraction

    def pendente (self) -> bool:
        """Checar se o `extraction.status` é `pending ou processing`"""
        return self.extraction.status in ("pending", "processing")

    def sucesso (self) -> bool:
        """Checar se o `extraction.status = success`"""
        return self.extraction.status == "success"

class ResponseAcompanhar:

    extraction: Extraction
    data: dict[str, TiposValores | None] | None
    """Um `dict` com o nome dos campos e seus valores extraídos
    - Preenchido caso `extraction.status` seja `success`"""
    confidence: dict[str, Numerico] | None
    """Um `dict` com o nome dos campos e o nível de confinaça na extração do campo em `data`
    - Preenchido caso `extraction.status = success`
    - De `0 a 1.0` representando porcentagem"""

    def pendente (self) -> bool:
        """Checar se o `extraction.status` é `pending ou processing`"""
        return self.extraction.status in ("pending", "processing")

    def sucesso (self) -> bool:
        """Checar se o `extraction.status = success`"""
        return self.extraction.status == "success"

    def erro_retry (self, *substring: str) -> bool:
        """Checar se o `extraction.errorMessage` possui mensagem sobre tentar novamente
        - `default` checado por `try again`, `tente novamente` e `retry`
        - `substring` para adicionar mais mensagens que podem ser realizados uma nova tentativa de extração"""
        if not self.extraction.errorMessage:
            return False

        mensagem_erro = self.extraction.errorMessage.lower().strip()
        return any(
            mensagem in mensagem_erro
            for mensagem in [
                "try again", "tente novamente", "retry",
                *map(lambda m: m.lower().strip(), substring)
            ]
        )

    def unmarshal[T] (self, classe_anotada_com_campos: type[T]) -> T:
        """Realizar o unmarshal dos campos de uma extação, com `status=sucesso`, conforme `classe_anotada_com_campos`
        # Exemplo
        ```
        from dclick.nora import acompanhar_extracao
        from dclick.nora.campos import CampoOpcional, CampoObrigatorio, Numerico

        class ExtracaoAgenteNotaFiscal:
            numero_nf:                  CampoObrigatorio[str]
            valor_total_nota:           CampoObrigatorio[Numerico]
            valor_liquido:              CampoObrigatorio[int | float]
            teste_possui_nome_jogador:  CampoObrigatorio[bool]
            teste_servicoes:            CampoObrigatorio[list]
            teste_nome_jogador:         CampoOpcional[str]

        response = acompanhar_extracao("F4SqBlBnIiXW")
        extracao = response.unmarshal(ExtracaoAgenteNotaFiscal)
        print(extracao.numero_nf.valor)
        print(extracao.numero_nf.confianca)
        print(extracao.numero_nf.porcentagem)
        ```"""
        # Confirmar classe
        cls = classe_anotada_com_campos
        assert isclass(cls) and cls.__module__ != "builtins", f"Esperado uma classe anotada ao extrair os campos do Nora: Recebido({cls})"
        # Confirmar existências dos dados
        assert self.sucesso(), f"Necessário status de extração de sucesso ao extrair os campos do Nora: Status({self.extraction.status})"
        assert self.data is not None and self.confidence is not None, "Dados da extração do Nora com valores nulos"

        # Extrair, Validar e Preencher campos
        obj = object.__new__(cls)
        tipos_esperados_campos = [str, int, float, bool, list]
        for nome_campo, TCampo in cls.__annotations__.items():

            # checar existência do campo na extração
            assert nome_campo in self.data, f"Nome do campo '{nome_campo}' não foi encontrado nos valores de extração do Nora"
            assert nome_campo in self.confidence, f"Nome do campo '{nome_campo}' não foi encontrado na confiança de extração do Nora"
            valor, confianca = self.data[nome_campo], self.confidence[nome_campo]

            # checar se a classe do TCampo está correta
            classe_campo = get_origin(TCampo) or TCampo
            assert classe_campo in (CampoObrigatorio, CampoOpcional),\
                f"Tipo inesperado para o campo '{nome_campo}' | Esperado{(CampoObrigatorio, CampoOpcional)} | Encontrado({classe_campo})"

            # checar se o tipo do TCampo é o esperado
            arg_campo, *_ = get_args(TCampo) or [None]
            arg_campo = arg_campo.__value__ if isinstance(arg_campo, TypeAliasType) else arg_campo
            assert arg_campo, f"Necessário anotar corretamente o tipo como genérico [T] para o campo '{nome_campo}'"
            tipos_campos: tuple[type, ...] = (arg_campo,) if isclass(arg_campo) else tuple(get_args(arg_campo))
            assert all(tipo_campo in tipos_esperados_campos for tipo_campo in tipos_campos),\
                f"Tipo inesperado para o campo '{nome_campo}' | Esperados({tipos_esperados_campos}) | Encontrados{tipos_campos}"

            # checar se o tipo do valor é o correto para o Campo[T]
            if valor is None:
                assert classe_campo is CampoOpcional, f"Valor do campo '{nome_campo}' é opcional. Utilizar o {CampoOpcional}"
                setattr(obj, nome_campo, CampoOpcional(valor, confianca))
            elif isinstance(valor, tipos_campos):
                setattr(obj, nome_campo, classe_campo(valor, confianca))
            else:
                raise ValueError(f"Tipo inesperado para o campo '{nome_campo}' | Esperados{tipos_campos} | Valor({valor}) | Tipo({type(valor)})")

        # Alterar __repr__ caso não implemente
        if cls.__repr__ is object.__repr__:
            cls.__repr__ = lambda self: f"<{self.__class__.__name__} com '{len(cls.__annotations__)}' campos>"

        return obj

__all__ = [
    "ResponseExecutar",
    "ResponseConsultar",
    "ResponseAcompanhar"
]