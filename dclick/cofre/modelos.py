class _Segredo:
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