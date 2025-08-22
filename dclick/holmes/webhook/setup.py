# std
import datetime, functools, typing
from concurrent.futures import ThreadPoolExecutor
# interno
import dclick
from dclick.holmes.modelos import Processo, Activity
from dclick.holmes.webhook import modelos
# externo
import bot

STATUS_ABERTO = "opened"
TOKEN = bot.configfile.obter_opcao_ou("webhook", "token")

@functools.cache
def client_singleton () -> bot.http.Client:
    """Criar o http `Client` configurado com o `base_url`, `token` e timeout
    - O Client ficará aberto após a primeira chamada na função devido ao `@cache`"""
    base_url, *_ = bot.configfile.obter_opcoes_obrigatorias("webhook", "base_url")
    return bot.http.Client(
        base_url = base_url,
        params = { "token": TOKEN },
        timeout = 10
    )

def checar_conexao_webhook () -> None:
    """Checar se a conexão está online
    - `AssertionError` caso negativo"""
    mensagem = "Conexão com o Webhook não detectada"
    assert client_singleton().head("/webhook/holmes").status_code == 200, mensagem

class ProcessoWebhook[T]:
    """Representação do processo no Webhook validado pelo `QueryProcessosWebhook`

    ### Propriedades
    - `webhook` interno do banco de dados do processo recebidos via webhook
    - `[properties, author, documents]` enviados pelo webhook do Holmes

    ### Útil
    - `repr(processo)` ou `f"{processo!r}"` representação do processo como `str`. Usar em Logs
    - Implementado `==` e `hash()` para comparação e usar como chave de um `dict` ou `set`
    - `stringify_properties()` transformar o `properties` para um json string

    ### Manipular processo do `Webhook`
    - `remover_webhook()` remover o processo do banco de dados do webhook
    - `incrementar_tentativas_webhook()` incrementar o campo `tentativas` do processo no banco de dados do webhook
    - `atualizar_controle_webhook()` atualizar o campo `controle` do processo no banco de dados do webhook

    ### Acessar dados do processo no `Holmes`
    - `holmes` processo no Holmes
    - `processo_em_aberto` checar se o processo `self.holmes` está aberto
    - `tarefa_em_aberto` consultar a tarefa em aberto no processo `self.holmes`
    - `tarefa_atribuida_a(_id="", nome="")` checar se a `tarefa_em_aberto` está atribuido ao usuário `_id` e/ou `nome`

    ### Manipular tarefa
    - `encaminhar_tarefa(id_acao="")` tomar ação `id_acao` na `self.tarefa_em_aberto`
    """

    webhook: modelos.Webhook
    """Propriedades do `webhook`"""
    properties: T
    """Propriedade `processo.properties`"""
    author: modelos.Author
    """Propriedade `processo.author`"""
    documents: list[modelos.Document]
    """Propriedade `processo.documents`"""

    def __repr__ (self) -> str:
        return f"<{self.__class__.__name__} holmes({self.webhook.id_processo}) webhook({self.webhook.id_webhook})>"

    def __eq__ (self, value: object) -> bool:
        return self.webhook.id_processo == value.webhook.id_processo if isinstance(value, ProcessoWebhook) else False

    def __hash__ (self) -> int:
        return hash(self.webhook.id_processo)

    def stringify_properties (self) -> str:
        """Transformar o `properties` para um json string"""
        return bot.formatos.Json(self.properties).stringify(False)

    def remover_webhook (self) -> typing.Self:
        """Remover o processo do banco de dados do webhook"""
        bot.logger.informar(f"Removendo o {self!r}")
        response = client_singleton().delete(f"/webhook/holmes/{self.webhook.id_webhook}")
        assert response.is_success, f"Erro ao remover a {self!r} do webhook | Status code '{response.status_code}' inesperado"
        return self

    def incrementar_tentativas_webhook (self) -> typing.Self:
        """Incrementar o campo `tentativas` do processo no banco de dados do webhook
        - Incrementado `self.webhook.tentativas` para refletir com o banco"""
        bot.logger.informar(f"Incrementando o campo tentativas do {self!r}")
        response = client_singleton().patch(f"/webhook/holmes/{self.webhook.id_webhook}/tentativas")
        assert response.is_success, f"Erro ao incrementar tentativas do {self!r} no webhook | Status code '{response.status_code}' inesperado"
        self.webhook.tentativas += 1
        return self

    def atualizar_controle_webhook (self) -> typing.Self:
        """Atualizar o campo `controle` do processo no banco de dados do webhook
        - Utilizado o campo `self.webhook.controle`"""
        bot.logger.informar(f"Atualizando o campo controle {self!r}")
        response = client_singleton().put(
            f"/webhook/holmes/{self.webhook.id_webhook}/controle",
            json = self.webhook.controle
        )
        assert response.is_success, f"Erro ao atualizar o campo controle do {self!r} no webhook | Status code '{response.status_code}' inesperado"
        return self

    @functools.cached_property
    def holmes (self) ->  Processo:
        """Processo no Holmes"""
        return dclick.holmes.consultar_processo(self.webhook.id_processo)

    @property
    def processo_em_aberto (self) -> bool:
        """Checar se o processo `self.holmes` está aberto"""
        return self.holmes.status.lower().strip() == STATUS_ABERTO

    @functools.cached_property
    def tarefa_em_aberto (self) -> Activity:
        """Consultar a tarefa em aberto no processo `self.holmes`
        - `AssertionError` caso não possua tarefa em aberto"""
        tarefa = self.holmes.obter_atividade(
            lambda a: a.status.lower().strip() == STATUS_ABERTO
        )
        assert tarefa, f"Não há tarefa em aberto para o {self!r}"
        return tarefa

    def tarefa_atribuida_a (self, _id: str | None = None, nome: str | None = None) -> bool:
        """Checar se a `tarefa_em_aberto` está atribuido ao usuário `_id / nome`"""
        assert any((_id, nome)), "Nome ou id do usuário é necessário para a comparação"

        try: atribuido = self.tarefa_em_aberto.assignee
        except Exception: return False
        if not atribuido: return False

        return all((
            _id is None or atribuido.id == _id,
            nome is None or atribuido.name == nome,
        ))

    def encaminhar_tarefa (
            self, id_acao: str,
            propriedades: list[dict[typing.Literal['id', 'value', 'text'], str]] | None = None
        ) -> typing.Self:
        """Tomar ação `id_acao` na `self.tarefa_em_aberto`
        - `propriedades` caso seja necessário informar algum adicional"""        
        dclick.holmes.tomar_acao_tarefa(self.tarefa_em_aberto.id, id_acao, propriedades)
        return self

class QueryProcessosWebhook [T]:
    """Realizar a query para buscar processos no webhook
    #### Variáveis utilizadas
    - `[webhook] -> "base_url", "token"`
    - `[holmes] -> "host", "token"`

    ### `query`
    - QueryParameter enviado para se filtrar os processos retornados
    - Exemplos
    ```
    properties.Nota de Serviços = 'Sim'
    properties.Nota de Serviços != 'Sim'
    properties.Nota de Serviços ilike 'sim'
    properties.Nota de Serviços is not null
    ```

    ### `classe_validadora_properties`
    Informar uma classe com os nomes das propriedades e tipos esperados  
    Caso as properties do Processo desejado sejam `{ "Filial": "Mogi Guaçu", "Empresa": "Artvel Veículos Peças e Serviços Ltda", "Nota de Serviços": "Sim", "ISS - Alíquota": 2.0, ... }`  
    Pode ser criado uma classe para extrair e validar os campos desejados
    ```
    class PropertiesServico:
        filial: str
        empresa: str
        nota_de_servicos: typing.Literal["Sim"]
        iss_aliquota: int | float
        campo_opcional: str | None
    ```
    Default: tratado como `dict[str, Any]` sem validação

    # Utilização
    ```
    # Os processos terão as `properties` como `dict`
    query = QueryProcessosWebhook("properties.Nota de Serviços = 'Sim'")
    # Os processos terão as `properties` como `PropertiesServico`
    query = QueryProcessosWebhook("properties.Nota de Serviços = 'Sim'", PropertiesServico)
    # Procurar por processos
    processos = query.procurar(limite=50)
    # Processos do Webhook que falharam na validação das properties
    for processo in query.itens_webhook_com_properties_invalida:
        print(f"{processo!r} apresentou falha na validação das properties")
    ```

    ## Veja `ProcessoWebhook` para mais detalhes
    """

    query: str
    classe_validadora_properties: type[T]
    itens_webhook_com_properties_invalida: list[tuple["ProcessoWebhook[dict[str, typing.Any]]", str]]
    """Itens do webhook que falharem a validação do `$.dados.properties` conforme `classe_validadora_properties`
    - Formato `[(processo, mensagem_erro)]` o `processo.properties` é tratado como `dict`
    - Sugerido notificar o cliente do erro para alterar algo no processo"""

    def __init__ (self, query: str, classe_validadora_properties: type[T] = dict[str, typing.Any]) -> None:
        self.query = query
        self.itens_webhook_com_properties_invalida = []
        self.classe_validadora_properties = classe_validadora_properties

    @functools.cached_property
    def unmarshaller_item_webhook (self) -> bot.formatos.Unmarshaller[modelos._ItemWebhook]:
        return bot.formatos.Unmarshaller(modelos._ItemWebhook)

    @functools.cached_property
    def unmarshaller_properties (self) -> bot.formatos.Unmarshaller[T]:
        return bot.formatos.Unmarshaller(self.classe_validadora_properties)

    def parse (self, processo: typing.Any) -> ProcessoWebhook[T] | None:
        """Realizar o parse do `processo` para o `ProcessoWebhook[T]`"""
        try: item_webhook = self.unmarshaller_item_webhook.parse(processo)
        except Exception as erro:
            bot.logger.alertar("\n\t".join((
                f"Processo do webhook ignorado devido ao formato inválido",
                "Isso não deveria ser possível",
                str(erro),
                str(processo),
            )))
            return

        pw = ProcessoWebhook()
        pw.author = item_webhook.dados.author
        pw.documents = item_webhook.dados.documents
        pw.webhook = modelos.Webhook(
            id_webhook      = item_webhook.id_webhook,
            id_processo     = item_webhook.id_processo,
            tentativas      = item_webhook.tentativas,
            controle        = item_webhook.controle,
            criado_em       = datetime.datetime.fromisoformat(item_webhook.criado_em),
            atualizado_em   = datetime.datetime.fromisoformat(item_webhook.atualizado_em),
        )

        # Parse `processo.dados.properties` conforme `classe_validadora_properties`
        try: properties = item_webhook.dados.properties \
            if dict in (self.classe_validadora_properties, typing.get_origin(self.classe_validadora_properties))\
            else self.unmarshaller_properties.parse(item_webhook.dados.properties)
        except Exception as erro:
            pw.properties = item_webhook.dados.properties
            bot.logger.alertar("\n\t".join((
                f"Properties do {pw!r} não está com o formato esperado",
                str(pw.properties),
                mensagem_erro := str(erro),
            )))
            return self.itens_webhook_com_properties_invalida.append((pw, mensagem_erro))

        pw.properties = properties
        pw.holmes # aproveitar o ThreadPool e consultar o processo
        return pw

    @bot.util.decoradores.prefixar_erro("Erro ao se obter os Processos do Webhook")
    def procurar (self, limite: int = 50) -> list[ProcessoWebhook[T]]:
        """Procurar os processos no webhook e realizar a validação
        - `limite` quantidade máxima de processos retornados"""
        bot.logger.informar(f"Procurando por processos no webhook | Query({self.query}) | Limite({limite})")

        checar_conexao_webhook()
        response = client_singleton().get(
            "/webhook/holmes",
            params = {
                "limit": limite,
                "query": self.query,
            }
        )
        assert response.status_code == 200, f"Status code diferente de 200: '{response.status_code}'"

        json = response.json()
        assert isinstance(json, dict) and isinstance(processos := json.get("processos"), list), f"Formato inesperado na resposta do webhook: {json}"
        with ThreadPoolExecutor(max_workers=10) as pool:
            processos = [
                processo
                for processo in pool.map(self.parse, processos)
                if processo is not None
            ]

        bot.logger.informar(f"Encontrado '{len(processos)}' Processos(s)")
        return processos

__all__ = [
    "ProcessoWebhook",
    "QueryProcessosWebhook",
]