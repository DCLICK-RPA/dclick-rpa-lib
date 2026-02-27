# std
import sys, typing
from dataclasses import dataclass 
# interno
import dclick

@dataclass
class ModeloErroComLog:

    codigo:      str
    categoria:   str
    descricao:   str
    urgencia:    typing.Literal["Crítica", "Alta", "Média", "Baixa"]
    responsavel: typing.Literal["Área de Negócio", "TI", "Sistema", "TI/Área de Negócio", "TI/Sistema", "Bot"]
    fluxo:       typing.Literal["IN", "OUT", "Fluxo Principal", "Infra", "API"]

    @property
    def mensagem_log (self) -> str:
        """Mensagem padrão no log"""
        return f"[{self.codigo}] {self.descricao}"

    def alertar (self) -> None:
        """Log nível `WARNING`
        - `Exception` capturada automaticamente, caso dentro do `except`"""
        dclick.logger.logger.warning(
            self.mensagem_log,
            stacklevel = 2,
            extra = { "extra": self },
            exc_info = erro if any(erro := sys.exc_info()) else None
        )

    def erro (self, excecao: Exception | None = None) -> None:
        """Log nível `ERROR`
        - `excecao=None` capturada automaticamente, caso esteja dentro do `except`"""
        dclick.logger.logger.error(
            self.mensagem_log,
            stacklevel = 2,
            extra = { "extra": self },
            exc_info = excecao or sys.exc_info()
        )
