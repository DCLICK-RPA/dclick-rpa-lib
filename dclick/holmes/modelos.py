# std
from email.message import Message
from email.parser import HeaderParser
from typing import Any, Callable, TypedDict
# externo
from bot.tipagem import SupportsBool
from bot.formatos import Unmarshaller
from bot.estruturas import String, Caminho

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

class Tarefa (Unmarshaller):

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
        existentes = [String(a.name).normalizar() for a in self.actions]
        return all(
            String(nome).normalizar() in existentes
            for nome in nomes
        )

    def obter_acao (self, filtro: Callable[[Action], SupportsBool]) -> Action:
        """Obter a ação da `tarefa` se estiver de acordo com o `filtro`
        - `Exception` caso não encontre
        - Utilizar `possui_acoes()` para validação"""
        for action in self.actions:
            try: 
                if filtro(action): return action
            except Exception: pass
        raise Exception("Nenhuma ação encontrada para o filtro informado")

    def obter_propriedade (self, filtro: Callable[[Property], SupportsBool]) -> Property | None:
        """Obter a propriedade da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for propriedade in self.properties:
            try:
                if filtro(propriedade): return propriedade
            except Exception: pass

    def obter_documento (self, filtro: Callable[[Document], SupportsBool]) -> Document | None:
        """Obter o documento da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for document in self.documents:
            try:
                if filtro(document): return document
            except Exception: pass

    def obter_tabela (self, filtro: Callable[[Table], SupportsBool]) -> Table | None:
        """Obter a tabela da `tarefa` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for table in self.tables:
            try:
                if filtro(table): return table
            except Exception: pass

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
    status: str
    assignee: Assignee | None

class Processo (Unmarshaller):
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

    def obter_atividade (self, filtro: Callable[[Activity], SupportsBool]) -> Activity | None:
        """Obter a atividade do `processo` se estiver de acordo com o `filtro`
        - `None` caso não encontre"""
        for atividade in self.current_activities:
            try:
                if filtro(atividade): return atividade
            except Exception: pass

class PropertyRecursive (Property):
    property_values: list["PropertyRecursive"]

class DetalhesProcesso (Unmarshaller):
    id: str
    name: str
    property_values: list[PropertyRecursive]

class ItemTabelaTarefa (Unmarshaller):
    id: str
    property_values: list[Property]

class Meta (Unmarshaller):
    count: int

class ItensTabelaTarefa (Unmarshaller):
    items: list[ItemTabelaTarefa]
    meta: Meta

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
