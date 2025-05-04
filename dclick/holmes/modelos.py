# std
from email.message import Message
from email.parser import HeaderParser
from typing import Any, Callable, Literal
# externo
from bot.util import normalizar
from bot.sistema import Caminho
from bot.tipagem import SupportsBool

class DocQueryTaskV2:
    id: str
    name: str
    type: Literal["task"]
    status: str
    task_id: str
    identifier: str
    assignee_id: str
    process_id: str
    process_name: str
    props: list[dict[str, Any]] | None

    def __eq__ (self, other: object) -> bool:
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__ (self) -> int:
        return hash(self.id)

    def obter_prop (self, filtro: Callable[[dict[str, Any]], bool | SupportsBool]) -> dict[str, Any] | None:
        """Obter o prop da `DoctTask` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for prop in (self.props or []):
            try:
                if filtro(prop): return prop
            except: pass

class RaizQueryTaskV2:
    total: int
    type: Literal["task"]
    docs: list[DocQueryTaskV2]

class DocQueryDocumentV2:
    document_id: str
    type: Literal["document"]
    nature_id: str
    nature_name: str
    file_name: str
    ext: str
    name: str
    props: list[dict[str, Any]] | None

    def __eq__ (self, other: object) -> bool:
        return isinstance(other, type(self)) and self.document_id == other.document_id

    def __hash__ (self) -> int:
        return hash(self.document_id)

    def obter_prop (self, filtro: Callable[[dict[str, Any]], bool | SupportsBool]) -> dict[str, Any] | None:
        """Obter o prop da `DoctTask` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for prop in (self.props or []):
            try:
                if filtro(prop): return prop
            except: pass

class RaizQueryDocumentV2:
    total: int
    type: Literal["document"]
    docs: list[DocQueryDocumentV2]

class Action:
    id: str
    name: str

class Property:
    id: str
    name: str
    value: Any

class Document:
    id: str
    conditional: str

class Table:
    id: str
    name: str

class Tarefa:

    id: str
    name: str
    status: str
    task_id: str
    identifier: str
    process_id: str
    process_name: str
    actions: list[Action]
    properties: list[Property]
    documents: list[Document]
    tables: list[Table]

    def __eq__ (self, other: object) -> bool:
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__ (self) -> int:
        return hash(self.id)

    def possui_acoes (self, *nomes: str) -> bool:
        """Checar se a `tarefa` possui todas as ações `nomes`"""
        existentes = [normalizar(a.name) for a in self.actions]
        return all(
            normalizar(nome) in existentes
            for nome in nomes
        )

    def obter_acao (self, filtro: Callable[[Action], bool | SupportsBool]) -> Action:
        """Obter a ação da `tarefa` se estiver de acordo com o `filtro`
        - `Exception` caso não encontre
        - Utilizar `possui_acoes()` para validação"""
        for action in self.actions:
            try: 
                if filtro(action): return action
            except: pass
        raise Exception("Nenhuma ação encontrada para o filtro informado")

    def obter_propriedade (self, filtro: Callable[[Property], bool | SupportsBool]) -> Property | None:
        """Obter a propriedade da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for propriedade in self.properties:
            try:
                if filtro(propriedade): return propriedade
            except: pass

    def obter_documento (self, filtro: Callable[[Document], bool | SupportsBool]) -> Document | None:
        """Obter o documento da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for document in self.documents:
            try:
                if filtro(document): return document
            except: pass

    def obter_tabela (self, filtro: Callable[[Table], bool | SupportsBool]) -> Table | None:
        """Obter a tabela da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for table in self.tables:
            try:
                if filtro(table): return table
            except: pass

class Documento:

    conteudo: bytes
    """Conteúdo do documento em bytes"""
    __message: Message

    def __init__ (self, conteudo: bytes, headers: dict[str, str]) -> None:
        self.conteudo = conteudo
        self.__message = HeaderParser().parsestr("\n".join(
            f"{header}: {valor}"
            for header, valor in headers.items()
        ))

    @property
    def tipo (self) -> str:
        return self.__message.get_content_type()

    @property
    def tamanho (self) -> int:
        return len(self.conteudo)

    @property
    def charset (self) -> str | None:
        return self.__message.get_content_charset() or None

    def nome_arquivo (self, default="blob") -> str:
        """Obter o nome do arquivo com o valor do header `Content-Disposition`
        - `default` caso não encontrado"""
        return self.__message.get_filename(default)

    def salvar (self, diretorio: Caminho) -> Caminho:
        """Salvar o conteúdo no `diretório`, conforme charset, e retornar o caminho"""
        charset = self.charset
        mode = "wb" if not charset else "w"
        destino = diretorio / self.nome_arquivo()
        with open(destino.path, mode, encoding=charset) as writer:
            writer.write(self.conteudo.decode(charset) if charset else self.conteudo)
        return destino

class Activity:
    id: str
    name: str
    task_id: str
    status: str

class Processo:
    id: str
    name: str
    status: str
    identifier: str
    solution_id: str
    current_activities: list[Activity]

    def __eq__ (self, other: object) -> bool:
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__ (self) -> int:
        return hash(self.id)

class PropertyRecursive (Property):
    property_values: list["PropertyRecursive"]

class DetalhesProcesso:
    id: str
    property_values: list[PropertyRecursive]

class ItemTabelaTarefa:
    id: str
    property_values: list[Property]

class Meta:
    count: int

class ItensTabelaTarefa:
    items: list[ItemTabelaTarefa]
    meta: Meta
