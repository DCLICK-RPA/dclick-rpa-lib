# std
from __future__ import annotations
import sys, typing
# externo
from bot.tipagem import SupportsStr
from bot.logger.interfaces import MainLogger, TracerLogger

type STATUS = typing.Literal["SUCCESS", "WARNING", "ERROR"]

class HistoricoTracers:

    dados: dict[STATUS, set[str]]

    def __init__ (self) -> None:
        self.dados = {
            "SUCCESS": set(),
            "WARNING": set(),
            "ERROR":   set(),
        }

    def adicionar (self, status: STATUS, chave: str) -> None:
        for v in self.dados.values():
            v.discard(chave)
        self.dados[status].add(chave)

    def total (self) -> int:
        """Contagem total dos tracers no histórico"""
        return sum(len(v) for v in self.dados.values())

    def chaves (self, status: STATUS) -> set[str]:
        """Obter as chaves dos tracers que encerraram com o `status`"""
        return self.dados[status].copy()

    def estatisticas (self) -> typing.Literal["sucesso", "parcial", "erro"]:
        """Gerar um log sobre estatísticas do total e status dos Tracers
        - Retornado `status` para ser usado no email"""
        total = self.total()
        partes = [f"Estatísticas Tracers | Total({total})"]

        for status in ("SUCCESS", "WARNING", "ERROR"):
            quantidade = len(self.dados[status])
            if status == "WARNING" and quantidade == 0: continue
            porcentagem = 0 if total == 0 else (quantidade / total) * 100
            partes.append(f"{status}({quantidade}, {porcentagem:.1f}%)")

        sucessos, _, erros = map(bool, self.dados.values())
        status = (
            "sucesso" if not erros else
            "erro" if not sucessos else
            "parcial"
        )

        logger.informar(" | ".join(partes), status=status)
        return status

class TracerDclick (TracerLogger):
    """Classe logger, obtida pelo `DclickLogger`, para realizar o rastreamento de itens relacionados
    - Utilizar o `tracer.encerrar()` para sinalizar a finalização do rastreamento
    - Pode ser usado com o `with` para encerramento automático"""

    def __repr__ (self) -> str:
        return f"<TracerDclick id={self.id!r} chave={self.chave!r}>"

    @typing.override
    def __exit__ (self, exc_type, exc: Exception | None, tb) -> None:
        if self.encerrado:
            return
        self.encerrado = True

        if exc is None:
            DclickLogger.historico.adicionar("SUCCESS", self.chave)
            self.logger.info(
                "Tracer encerrado automaticamente com sucesso",
                stacklevel = 2,
                extra = {
                    "extra": self.extra | self.extra,
                    "trace": {
                        "id": self.id,
                        "chave": self.chave,
                        "status": "SUCCESS",
                        "seconds": self.cronometro()
                    }
                }
            )

        else:
            DclickLogger.historico.adicionar("ERROR", self.chave)
            self.logger.error(
                "[BOT.ERRO.022] - Tracer encerrado automaticamente com erro",
                stacklevel = 2,
                exc_info = exc,
                extra = {
                    "extra": self.extra | self.extra,
                    "trace": {
                        "id": self.id,
                        "chave": self.chave,
                        "status": "ERROR",
                        "seconds": self.cronometro()
                    }
                }
            )

    @typing.override
    def __del__ (self) -> None:
        if self.encerrado: return
        DclickLogger.historico.adicionar("WARNING", self.chave)
        self.logger.warning(
            "Tracer não encerrado corretamente",
            extra = self.extra | {
                "trace": {
                    "id": self.id,
                    "chave": self.chave,
                    "status": "WARNING",
                    "seconds": self.cronometro()
                }
            }
        )

    @typing.override
    def encerrar (self, status: STATUS, mensagem: SupportsStr, excecao: Exception | None = None, **extra: object) -> None:
        if self.encerrado: return
        DclickLogger.historico.adicionar(status, self.chave)
        self.encerrado = True

        log_func = {
            "SUCCESS": self.logger.info,
            "WARNING": self.logger.warning,
            "ERROR": self.logger.error,
        }.get(status)
        assert log_func is not None, f"Status '{status}' inválido ao encerrar {self}"

        log_func(
            str(mensagem),
            stacklevel = 2,
            exc_info = excecao or (erro if any(erro := sys.exc_info()) else None),
            extra = {
                "extra": extra | self.extra,
                "trace": {
                    "id": self.id,
                    "chave": self.chave,
                    "status": status,
                    "seconds": self.cronometro()
                }
            }
        )

    @typing.override
    def alertar (self, mensagem: SupportsStr,
                       codigo: str = "BOT.ALERTA.000",
                       **extra: object) -> typing.Self:
        """Log nível `WARNING`
        - `codigo` de erro para identificação pelo portal"""
        self.logger.warning(
            f"[{codigo}] - {mensagem}",
            stacklevel = 2,
            extra = {
                "extra": extra | self.extra,
                "trace": {
                    "id": self.id,
                    "chave": self.chave,
                    "status": "PROCESSING",
                    "seconds": self.cronometro()
                }
            }
        )
        return self

    @typing.override
    def erro (self, mensagem: SupportsStr,
                    excecao: Exception | None = None,
                    codigo: str = "BOT.ERRO.000",
                    **extra: object) -> typing.Self:
        """Log nível `ERROR`
        - `codigo` de erro para identificação pelo portal
        - `excecao=None` capturada automaticamente, caso esteja dentro do `except`"""
        self.logger.error(
            f"[{codigo}] - {mensagem}",
            stacklevel = 2,
            exc_info = excecao or sys.exc_info(),
            extra = {
                "extra": extra | self.extra,
                "trace": {
                    "id": self.id,
                    "chave": self.chave,
                    "status": "PROCESSING",
                    "seconds": self.cronometro()
                }
            }
        )
        return self

class DclickLogger (MainLogger):
    """Classe pré-configurada para criar, consultar e tratar os arquivos de log
    - `name` o mesmo da propriedade que aparecerá nos logs

    #### Inicializar manualmente `logger.inicializar()`
    - Stream para o `stdout`
    - Cria um LOG no diretório de execução para fácil acesso `CAMINHO_LOG_RAIZ`
    - Salva um LOG no diretório de persistência `CAMINHO_LOG_PERSISTENCIA`
    - Variáveis .ini `[logger] -> [dias_persistencia: 14, flag_debug: False]`"""

    historico = HistoricoTracers()
    """Histórico de encerramento dos `Tracers`"""

    def __init__ (self, nome: str) -> None:
        self.__nome = nome
        super().__init__(nome)

    def __repr__ (self) -> str:
        return f"<DclickLogger id={self.IDENTIFICADOR_LOGGER!r} nome={self.__nome!r}>"

    @classmethod
    @typing.override
    def ObterLogger (cls, nome: str) -> DclickLogger:
        return DclickLogger(nome)

    @typing.override
    def obter_tracer (self, chave: str, **extra: object) -> TracerDclick:
        return (
            TracerDclick(self.logger, chave, extra)
            .debug(f"Iniciado um Tracer para a chave {chave}")
        )

    @typing.override
    def alertar (self, mensagem: SupportsStr,
                       codigo: str = "DCLICK.ALERTA.000",
                       **extra: object) -> typing.Self:
        """Log nível `WARNING`
        - `codigo` de erro para identificação pelo portal"""
        self.logger.warning(
            f"[{codigo}] - {mensagem}",
            stacklevel = 2,
            extra = { "extra": extra },
        )
        return self

    @typing.override
    def erro (self, mensagem: SupportsStr,
                    excecao: Exception | None = None,
                    codigo: str = "DCLICK.ERRO.000",
                    **extra: object) -> typing.Self:
        """Log nível `ERROR`
        - `codigo` de erro para identificação pelo portal
        - `excecao=None` capturada automaticamente, caso esteja dentro do `except`"""
        self.logger.error(
            f"[{codigo}] - {mensagem}",
            stacklevel = 2,
            extra = { "extra": extra },
            exc_info = excecao or sys.exc_info()
        )
        return self

logger = DclickLogger("DCLICK")
"""Classe pré-configurada para criar, consultar e tratar os arquivos de log
- Logger de `name: DCLICK`
- Utilizar `dclick.logger.ObterLogger(nome)` ou importar o `DclickLogger(nome)` para criar uma instância com outro nome

#### Inicializar manualmente `logger.inicializar()` para inicializar os handlers
- Stream para o `stdout`
- Cria um LOG no diretório de execução para fácil acesso `CAMINHO_LOG_RAIZ`
- Salva um LOG no diretório de persistência `CAMINHO_LOG_PERSISTENCIA`
- Variáveis .ini `[logger] -> [dias_persistencia: 14, flag_debug: False]`"""