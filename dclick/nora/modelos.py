# std
from typing import Literal
from datetime import datetime as Datetime

TStatus = Literal["pending", "processing", "success", "error"]

class ResponseExecutar:

    trackingCode: str
    """Código para acompanhar o progresso da extração"""
    extractionId: str
    """UUID da extração criada."""
    status: str
    """Status inicial da extração
    - `pending`"""
    message: str

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

    @property
    def data_criacao (self) -> Datetime:
        return Datetime.fromisoformat(self.createdAt)

class ResponseAcompanhar:

    extraction: Extraction
    data: dict[str, str | int | float | bool | None] | None
    """Um `dict` com o nome dos campos e seus valores extraídos
    - Preenchido caso `extraction.status` seja `success`"""
    confidence: dict[str, float | int] | None
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

class ResponseConsultar:

    extraction: Extraction

    def pendente (self) -> bool:
        """Checar se o `extraction.status` é `pending ou processing`"""
        return self.extraction.status in ("pending", "processing")

    def sucesso (self) -> bool:
        """Checar se o `extraction.status = success`"""
        return self.extraction.status == "success"
