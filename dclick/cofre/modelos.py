# externo
from bot.formatos import Unmarshaller

class _Segredo (Unmarshaller):
    key: str
    description: str
    category: str | None
    status: str
    fields: dict[str, str]

class Segredo[T]:
    key: str
    description: str
    category: str | None
    status: str
    fields: T