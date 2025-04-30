## Biblioteca com pacotes padronizados para as ferramentas utilizadas recorrentemente pelos bots da DClick

⚠️ <span style="color: red;"><strong>Python</strong> <code>&gt;=3.12</code></span> ⚠️  
⚠️ <span style="color: red;"><strong>Pacote dclick-rpa-python-bot-lib</strong> <code>==3.0</code></span> ⚠️

> **Instalação via url do release no github:**  
Via pip `pip install https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v3.0/dclick-1.0-py3-none-any.whl`  
Via uv `uv add https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v3.0/dclick-1.0-py3-none-any.whl`

> **Para referenciar como dependência:**  
Utilizar o link para o arquivo **whl** do release `dclick @ https://github.com/DCLICK-RPA/dclick-rpa-lib/releases/download/v3.0/dclick-1.0-py3-none-any.whl`  
Utilizar o caminho para o arquivo **whl** baixado `dclick @ file://.../dclick-1.0-py3-none-any.whl`

> Os pacotes podem ser encontrados diretamentes no namespace **dclick** após import da biblioteca **import dclick** ou importado diretamente o pacote desejado **from dclick import pacote**

## Importante
> Pacote criado de forma genérica visando reutilização.

Não se deve ter um **fluxo** que realizar diversas tarefas, mas sim partes que realiza **1 ação** bem estabelecidas. Cabe ao desenvolvedor montar da forma que interessa.

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
Irá ser criado no diretório `./build` o arquivo **.whl** com a versão atual.  
Abrir a página `releases` do github e realizar o upload do arquivo no release correto para a versão atual

> **Automático**  
Pendente

## Descrição breve dos pacotes com algumas funcionalidades
Veja a descrição dos pacotes para mais detalhes e inspecionar as funções e classes disponíveis para um melhor contexto