"""Pacote com erros e suas codificações separadas por categorias
- Possível de realizar log de `alerta` e `erro`, com o `dclick.logger`, para cada erro existente
- A mensagem é no formato `[Código] - Descrição` e, na propriedade `extra`, é passado as informações sobre o erro"""

from dclick.erros import (
    api,
    arquivo,
    comunicacao,
    entrada,
    execucao,
    saida,
    sistema,
    sustentacao,
)