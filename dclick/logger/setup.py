# externo
from bot.logger.interfaces import MainLogger, TracerLogger

logger = MainLogger("DCLICK")
"""Classe pré-configurada para criar, consultar e tratar os arquivos de log
- Logger de `name: DCLICK`
- Utilizar `dclick.logger.obter_logger(nome)` ou importar o `MainLogger(nome)` para criar uma instância com outro nome

#### Inicializar manualmente `logger.inicializar_logger()` pela lib da `dclick` ou `bot` para inicializar os handlers
- Stream para o `stdout`
- Cria um LOG no diretório de execução para fácil acesso `CAMINHO_LOG_RAIZ`
- Salva um LOG no diretório de persistência `CAMINHO_LOG_PERSISTENCIA`
- Variáveis .ini `[logger] -> [dias_persistencia: 14, flag_debug: False]`"""