"""Biblioteca com pacotes padronizados para as ferramentas utilizadas recorrentemente pelos bots da **DClick**
### Dependência `dclick[nbs]` necessária para utilizar `dclick.nbs`
### Dependência `dclick[dealernet]` necessária para utilizar `dclick.dealernet`"""

from dclick.logger.setup import logger
from dclick import (
    erros,
    http,
    cofre,
    email,
    holmes,
    nora,
)