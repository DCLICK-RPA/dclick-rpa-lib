# std
from datetime import datetime
from typing import Any, Literal, TypedDict
# externo
from bot.formatos import Unmarshaller

type STATUS = Literal["opened", "closed", "canceled"]

class Action (Unmarshaller):
    id: str
    name: str

class Property (Unmarshaller):
    id: str
    name: str
    value: Any

class Document (Unmarshaller):
    id: str
    conditional: str

class Table (Unmarshaller):
    id: str
    name: str

class DocumentItem (Unmarshaller):
    id: str
    name: str
    status: str
    file: bool
    file_name: str
    document_id: str
    created_at: datetime
    removed: bool

class HistoryItem (Unmarshaller):
    id: str
    key: str
    message: str
    created_at: datetime
    performed_by: str
    properties: dict[str, Any] = {}

class UploadDocumento (Unmarshaller):
    id: str
    url: str

class Assignee (Unmarshaller):
    id: str
    name: str

class Activity (Unmarshaller):
    id: str
    name: str
    task_id: str
    status: STATUS
    created_at: datetime
    assignee: Assignee | None

class DetalhesProcesso (Property):
    property_values: list["DetalhesProcesso"]

class TableItem (Unmarshaller):
    id: str
    created_at: datetime
    updated_at: datetime | None
    property_values: list[Property]

class ClassificacaoDocumento (Unmarshaller):
    id: str
    nature_id: str | None
    file_name: str
    property_values: list[Property]

class ClassificacaoDocumentoPropertyDict (TypedDict):
    id: str
    value: str

class ClassificacaoDocumentoDict (TypedDict):
    nature_id: str
    property_values: list[ClassificacaoDocumentoPropertyDict]
