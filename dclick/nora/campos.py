# std
from typing import Any

type Numerico = int | float
type TiposValores = str | Numerico | bool | list[Any]

class CampoObrigatorio[T: TiposValores]:
    """Campo com valor e confiança"""

    valor: T
    """Valor do campo"""
    confianca: float
    """Confiança na extração do valor
    - Entre 0 e 1.0"""

    def __init__ (self, valor: T, confianca: Numerico) -> None:
        self.valor = valor
        self.confianca = float(confianca)

    def __repr__ (self) -> str:
        return str(self.__dict__)

    @property
    def porcentagem (self) -> str:
        """Mensagem formatada sobre a `confiança`"""
        return f"Porcentagem de confiança '{self.confianca:.0%}'"

class CampoOpcional[T: TiposValores] (CampoObrigatorio[T]):
    """Campo com valor opcional e confiança"""

    valor: T | None
    """Valor do campo
    - `None` caso opcional"""

    def __init__ (self, valor: T | None, confianca: Numerico) -> None:
        self.valor = valor # type: ignore
        self.confianca = float(confianca)

__all__ = [
    "CampoOpcional",
    "CampoObrigatorio"
]