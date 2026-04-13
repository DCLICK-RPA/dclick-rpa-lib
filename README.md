## Biblioteca com pacotes padronizados para as ferramentas utilizadas recorrentemente pelos bots da DClick

⚠️ <span style="color: red;"><strong>Python</strong> <code>&gt;=3.12</code></span> ⚠️  
⚠️ <span style="color: red;"><strong>Pacote dclick-rpa-python-bot-lib</strong> <code>==5.0</code></span> ⚠️

> **Instalação via url do release no github:**  
Via pip `pip install https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v2.1/dclick-2.1-py3-none-any.whl`  
Via uv `uv add https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v2.1/dclick-2.1-py3-none-any.whl`

> **Para referenciar como dependência:**  
Utilizar o link para o arquivo **whl** do release `dclick @ https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v2.1/dclick-2.1-py3-none-any.whl`  
Utilizar o caminho para o arquivo **whl** baixado `dclick @ file://.../dclick-2.1-py3-none-any.whl`

> Os pacotes podem ser encontrados diretamentes no namespace **dclick** após import da biblioteca **import dclick** ou importado diretamente o pacote desejado **from dclick import pacote**


## Changelog 🔧

<details>
<summary>v2.1</summary>

- Criado pacote `nora`

</details>
<details>
<summary>v2.0</summary>

- Migração para a versão do `bot==5.0`
- Removido pacote `dashboard`
- Criado pacote `cofre`
- Criado pacote `erros`
- Criado pacote `http`
- Criado pacote `logger`

</details>
<details>
<summary>v1.4</summary>

- Atualizado propriedades do `dclick.holmes.webhook.ProcessoWebhook`

</details>
<details>
<summary>v1.3</summary>

- Utilizado nova versão do `bot`

</details>
<details>
<summary>v1.2</summary>

- Refatorado `email.notificar_email_simples()` mas mantido funcionalidade
- Utilizado nova versão do `bot` e alterado pacotes dependentes onde houveram alterações
- Adicionado `nbs.pecas_compras`
- Adicionado `holmes.webhook`
- Adicionado funções de upload e remoção de documentos no `holmes`

</details>
<details>
<summary>v1.1</summary>

- Utilizado nova versão do `bot`
- Renomeado argumento `status` em `email.notificar_email_simples()` e adicionado opção para `parcial`
- Aplicado melhorias no pacote `nbs`

</details>
<details>
<summary>v1.0</summary>

- Criação dos pacotes `dashboard, dealernet, email, holmes, nbs`

</details>


## Importante
> Utilizado o **uv** como package-manager  

> Pacote criado de forma genérica visando reutilização.

Não se deve ter um **fluxo** que realiza diversas tarefas, mas sim partes especializadas que realizam apenas **1 ação**. Cabe ao desenvolvedor encaixar as partes da melhor forma.

Não utilizar valores fixos nas funções ou classes, mas sim possíveis de serem alterados por quem irá utilizar.  
Exemplo:
- parametrizar nas funções
- variáveis do arquivo .ini (vide `exemplo.ini`)
- propriedades das classes que pode ser feito o `@override`

## Build / Release
> Versão obtida no arquivo `pyproject.toml` propriedade `version`

> Os `releases` devem estar acompanhados das tags no formato `v{VERSION}`.  

> Indicar em comentário qual verão do pacote `dclick-rpa-python-bot-lib` o release utiliza

> **Manual**  
Utilizar o comando `uv build --wheel`.  
Irá ser criado no diretório `./dist` o arquivo **.whl** com a versão atual.  
Abrir a página `releases` do github e realizar o upload do arquivo no release correto para a versão atual

> **Automático**  
Configurar a seção `github` no .ini e executar o script `build_upload.py`

## Descrição breve dos pacotes com algumas funcionalidades
Veja a descrição dos pacotes para mais detalhes e inspecionar as funções e classes disponíveis para um melhor contexto

### `email`
Pacote destinado ao envio de e-mail
> Realizado logs de `erros.comunicacao` automaticamente de acordo com possíveis erros
```python
# Enviar a notificação padrão DClick via e-mail com o Assunto `nome_bot - status`
notificar_email_simples (
    nome_bot: str,
    status: Literal["sucesso", "parcial", "erro"],
    *mensagem: str,
    anexar_log: bool = True,
    anexos: list[bot.sistema.Caminho] | None = None,
    destinatarios: list[bot.tipagem.email] | None = None,
) -> None:
```

### `cofre`
Pacote destinado ao cofre de senhas do `Runner`
```python
# Consultar o segredo `nome` e retornar uma classe modelo de resposta.
# Exemplo com fields sendo um `dict`
segredo = dclick.cofre.consultar_segredo("EMAIL_CREDENTIALS")
username: str | None = segredo.fields.get("username", default=None)
# Exemplo com uma classe anotada e feito validação dos campos
class Fields:
    username: str
    password: str
segredo = dclick.cofre.consultar_segredo("EMAIL_CREDENTIALS", Fields)
print(segredo.fields.username, segredo.fields.password)
```

### `http`
Pacote destinado ao protocolo http
> Realizado logs de `erros.api` automaticamente para o `request e response` dos métodos novos/modificados
```python
# Enviar um request conforme parâmetros
# Retorna um `ResponseHttp` com métodos adicionais ao `httpx.Response`
# Realizado logs automáticos de erros de api para requests e responses com os métodos modificados
request(
    metodo: Literal['HEAD', 'OPTIONS', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    url: str,
    query: QueryParamTypes | None = None,
    headers: HeaderTypes | None = None,
    *,
    json: object | None = None,
    conteudo: RequestContent | None = None,
    dados: RequestData | None = None,
    arquivos: RequestFiles | None = None,
    follow_redirects: bool = False,
    timeout: TimeoutTypes = 60,
    verify: str | bool = True
) -> ResponseHttp

# Criar um cliente `HTTP` para realizar requests
# Extensão do `httpx.Client`
# Retorno dos métodos `request, get, post, put, ...` é um `ResponseHttp` com métodos adicionais ao `httpx.Response`
# Realizado logs automáticos de erros de api para requests e responses com os métodos modificados
ClienteHttp(
    base_url: URLTypes,
    headers: HeaderTypes | None = None,
    verify: str | bool = True,
    timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
    ...
)
```

### `erros`
Pacote com erros e suas codificações separadas por categorias.  
> Possível de realizar log de `alerta` e `erro`, com o `dclick.logger`, para cada erro existente

> A mensagem é no formato `[Código] - Descrição` e, na propriedade `extra`, é passado as informações sobre o erro
```python
# Gerar um log ERROR, da categoria arquivo
# Falha ao gerar/baixar PDF
dclick.erros.arquivo.FalhaPDF.erro()

# Gerar um log WARNING, da categoria execução
# Tentativa de acessar valor nulo/inexistente
dclick.erros.execucao.ValorNuloOuInexistente.alertar()
```

### `logger`
Pacote para realizar e tratar Logs
```python
# Log para diferentes níveis com o nome `DCLICK`
# Utilizado pelos pacotes da lib
logger.debug (mensagem: str) -> MainLogger
logger.informar (mensagem: str) -> MainLogger
logger.alertar (mensagem: str) -> MainLogger
logger.erro (mensagem: str, excecao: Exception | None = None) -> MainLogger
# Possível de se passar itens extra com os argumentos nomeados
# Aparecerão na propriedade `extra`
logger.informar (
    mensagem: str,
    # Exemplo
    quantidade = 10,
    itens = [...],
    dados = {...}
) -> MainLogger

# Criar um logger com nome próprio
# Útil para identificar uma execução
from dclick.logger.setup import MainLogger
logger = MainLogger("MEU_LOG")                 # 1
logger = dclick.logger.obter_logger("MEU_LOG") # 2

# Necessário inicializar manualmente para configurar os handlers e formatação
# Possível de se usar no logger criado ou no da `dclick.logger`
logger.inicializar_logger()

# Obter o `TracerLogger` utilizado para realizar o rastreamento de um processo
# Possível de se realizar os logs com a mesma interface que o `MainLogger`
from dclick.logger.setup import TracerLogger
tracer: TracerLogger = logger.obter_tracer()
# Sinalizar o encerramento do tracer
tracer.encerrar("SUCCESS", "Sucesso ao se realizar determinada Ação")
tracer.encerrar("ERROR", "Falha ao realizar determinada Ação")

# Loggar o tempo de execução de uma função
@logger.tempo_execucao
```

### `nora`
Pacote destinado a `Nora AI`, agente de extração via IA
```python
import dclick
from bot.sistema import Caminho

# Executar uma extração para o `agente`
caminho_pdf = Caminho("./nfe_xpto.pdf")
response = dclick.nora.executar_extracao(
    agente = "yATCG7ty4u",
    mime_type = "application/pdf",
    file_name = caminho_pdf.nome,
    content = caminho_pdf.encode_base64()
) -> ResponseExecutar

# Acompanhar uma extração via `tracking_code`
dclick.nora.acompanhar_extracao (tracking_code: str) -> ResponseAcompanhar

# Consultar a extração `extraction_id`
dclick.nora.consultar_extracao (extraction_id: str) -> ResponseConsultar

# Classe para realizar o acompanhamento de extrações até o `status = sucesso/erro`
# Inicializar o Polling e adicionar os `tracking_codes`
polling = (
    dclick.nora.PollingExtracao()
    .adicionar("vXRdxHZRrUKj", "wjM3N9ej0Iza", "...")
)
while polling.pendente():
    try: response = polling.aguardar()
    # Tempo ao aguardar a extração demorou mais tempo que o esperado
    except TimeoutError: raise
    # Erro inesperado
    except Exception: raise

    tracking_code = response.extraction.trackingCode
    if response.sucesso():
        print("Sucesso", tracking_code, response.data, response.confidence)
    elif response.erro_retry():
        print("Erro passível de retentativa", tracking_code)
    else:
        print("Erro extração", response.extraction.errorMessage)
```

### `holmes`
Pacote destinado a API do Holmes  
Retorna classes com propriedades esperadas do endpoint
```python
# Classe para realizar a construção da Query das tasks e iteração sobre os resultados obtidos
# Customizável via arquivo .ini
QueryTaskV2()
    # Consultar a query e obter o resultado
    .consultar() -> modelos.RaizQueryTaskV2
    # Realizar a consulta da query com paginação até a quantidade `limite`
    # Filtro para se obter apenas as tarefas desejadas
    .paginar_query(
        filtro = lambda item: bool,
        limite = 50
    ) -> Generator[modelos.DocQueryTaskV2]
    # Realizar a consulta das tarefas da query com paginação até a quantidade `limite`
    # Filtro para se obter apenas as tarefas desejadas
    .paginar_tarefas_query(
        filtro = lambda tarefa: bool,
        limite = 50
    ) -> Generator[modelos.Tarefa]

# Consultar a tarefa `id_tarefa`
consultar_tarefa (id_tarefa: str) -> modelos.Tarefa
```

### `holmes.webhook`
Pacote destinado a consulta e manipulação dos processos no [Webhook do Holmes](https://github.com/DCLICK-RPA/dclick-webhook-notificacao-holmes)

> Veja a descrição das classes para um melhor contexto

```python
# Os processos terão as `properties` como `dict`
query = QueryProcessosWebhook("properties.Nota de Serviços = 'Sim'")

# Os processos terão as `properties` como `PropertiesServico`
class PropertiesServico:
    filial: str
    empresa: str
    nota_de_servicos: typing.Literal["Sim"]
    iss_aliquota: int | float
    campo_opcional: str | None
query = QueryProcessosWebhook("properties.Nota de Serviços = 'Sim'", PropertiesServico)

# Procurar por processos
processos = query.procurar(limite=50)
# Processos do Webhook que falharam na validação das properties
for processo in query.itens_webhook_com_properties_invalida:
    print(f"{processo!r} apresentou falha na validação das properties")
```

### `dealernet`
Pacote destinado ao **Sistema Web Dealer-Net**  
```Python
# Realizar o login no dealernet
def login (navegador: bot.navegador.Edge) -> None:
```

#### Descrição sobre alguns pacotes internos

> Existem mais pacotes internos especializados para uma tela do **Menu**

`menus`  
Pacote para tratar a seleção da opção desejada nos menus, como Empresa e Produto, presentes no rodapé e cabeçalho do sistema
```Python
# Classe com os Localizadores dos menus suportados
class Menus (Enum): ...

# Clicar no localizador do `menu` e navegar pelas `opcoes` clicando em cada opção do menu de acordo com o texto
# Exemplo: `selecionar_opcao_menu(navegador, ["Nota Fiscal", "NF Entrada Item Avulso"], Menus.PRODUTOS)`
selecionar_opcao_menu(
    navegador: bot.navegador.Edge,
    opcoes: Iterable[str],
    menu: Menus = Menus.EMPRESA,
) -> None

# Acessar o iframe do menu aberto com o `nome_menu`
# `nome_menu` observado ser a última parte das opções em `selecionar_opcao_menu()`
def acessar_iframe_janela_menu (
    navegador: bot.navegador.Edge,
    nome_menu: str
) -> None:
```

`integracao.nota_fiscal_item_avulso`  
Pacote para tratar o menu **Integração -> XML - Importação -> Nota Fiscal de Item Avulso**
```Python
# Importar todas as `nfe` em `["XML - Importação", "Nota Fiscal de Item Avulso"]`
def importar_nfe (
    navegador: bot.navegador.Edge,
    *nfe: bot.estruturas.Caminho
) -> None:

# Classe especializada para obter e filtrar os registros na tabela
class TabelaRegistro: ...

# Classe para tratar a atualização dos dados de um registro
class AtualizarDadosRegistro: ...

# Classe para tratar o processamento dos dados de um registro
# Iniciado a partir do `AtualizarDadosRegistro`
class ProcessarDadosRegistro: ...
```

### `nbs`
Pacote destinado ao sistema NBSi
> Necessário instalar a dependência adicional `dclick[ocr]` caso seja usado o `LeitorOCR` da biblioteca `bot`

```Python
# Abrir o NBS e realizar o login
# Retorna a janela shortcut
janela_shortcut = nbs.abrir_e_login()

# Fecha as janelas do NBS
# Útil para o encerramento do bot
nbs.fechar_janelas_nbs()
```

> Os pacotes internos do `nbs` representam os módulos da janela `Shortcut`  
> Cada pacote fica responsável pela sua manipulação

Exemplo com o pacote `nbs.nbs_fiscal`
```Python
# Abrir o módulo `Nbs Fiscal`
# Retornado `SelecaoEmpresaFilial
selecao_empresa = nbs.nbs_fiscal.abrir_modulo_nbs_fiscal(janela_shortcut)

# Classe para tratar a seleção da empresa e filial do menu `Nbs Fiscal`
selecao_empresa.selecionar_empresa("empresa")\
               .selecionar_filial("filial")
janela_sistema_fiscal = selecao_empresa.confirmar()
selecao_empresa.checar_selecao() # Checar se a seleção da Empresa/Filial aconteceu com sucesso

# Fecha a janela `Nbs Fiscal` e todas as janelas descendentes abertas
# Útil para um loop de processamento das notas fiscais
nbs.nbs_fiscal.fechar_janela_nbs_fiscal()

# Pacotes internos ao `nbs.nbs_fiscal` para navegação e manipulação das janelas
```