## Biblioteca com pacotes padronizados para as ferramentas utilizadas recorrentemente pelos bots da DClick

⚠️ <span style="color: red;"><strong>Python</strong> <code>&gt;=3.12</code></span> ⚠️  
⚠️ <span style="color: red;"><strong>Pacote dclick-rpa-python-bot-lib</strong> <code>==4.0</code></span> ⚠️

> **Instalação via url do release no github:**  
Via pip `pip install https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v1.2/dclick-1.2-py3-none-any.whl`  
Via uv `uv add https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v1.2/dclick-1.2-py3-none-any.whl`

> **Para referenciar como dependência:**  
Utilizar o link para o arquivo **whl** do release `dclick @ https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v1.2/dclick-1.2-py3-none-any.whl`  
Utilizar o caminho para o arquivo **whl** baixado `dclick @ file://.../dclick-1.2-py3-none-any.whl`

> Os pacotes podem ser encontrados diretamentes no namespace **dclick** após import da biblioteca **import dclick** ou importado diretamente o pacote desejado **from dclick import pacote**


## Changelog 🔧

<details>
<summary>v1.2</summary>

- Refatorado `email.notificar_email_simples()` mas mantido funcionalidade
- Utilizado nova versão do `bot` e alterado pacotes dependentes onde houveram alterações
- Adicionado `nbs.pecas_compras`
- Adicionado `holmes.webhook`

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

### `dashboard`
Pacote destinado ao dashboard da DClick
```python
# Gravar transação na dashboard com os dados para a automação `codigo_automacao`
# `codigo_automacao` obtido do arquivo .ini
gravar_transacao (
    chave: str,
    identificador: str,
    mensagem: str = "",
    data_hora: Datetime | None = None
) -> None
```

### `email`
Pacote destinado ao envio de e-mail
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

<br>

`holmes.webhook`  
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

# Consultar os processos
processos = query.consultar(limite=50)
# Processos do Webhook que falharam na validação das properties
for item in query.itens_webhook_com_properties_invalida:
    print(f"Item {item.id_processo} apresentou falha na validação das properties")
```

<br><br>

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

<br><br>

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