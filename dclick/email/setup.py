# std
from typing import Literal
# externo
import bot

CAMINHO_EMAIL_SIMPLES = bot.sistema.Caminho(__file__).parente / "email_simples.html"

def separar_destinatarios (destinatarios: str) -> list[bot.tipagem.email]:
    """Separar um ou mais `destinatarios` concatenados por vírgula no configfile para uma lista"""
    return [
        d.strip()
        for d in destinatarios.split(",")
        if not d.isspace()
    ]

def notificar_email_simples (
        nome_bot: str,
        status: Literal["sucesso", "parcial", "erro"],
        *mensagem: str,
        anexar_log: bool = True,
        anexos: list[bot.sistema.Caminho] | None = None,
        destinatarios: list[bot.tipagem.email] | None = None,
    ) -> None:
    """Enviar a notificação padrão DClick via e-mail com o Assunto `nome_bot - status`
    - `mensagem` será concatenada com `<br>`
    - `anexar_log` para anexar o log raiz
    - `anexos` caminhos para anexos adicionais
    - `destinatarios` especificar os destinatários da notificação
        - `destinatarios=None` Variáveis utilizadas `[email.destinatarios] -> "sucesso", "erro"`
        - `destinatarios=None e tipo="parcial"` utiliza os destinatários do `erro`
    - Variáveis utilizadas `[email.enviar] -> user, password, host, [port: 587, ssl: False, ]`"""
    assunto = f"{nome_bot} - {status.capitalize()}"
    mensagem_email = "<br>".join(mensagem)
    destinatarios = destinatarios if destinatarios != None else separar_destinatarios(
        bot.configfile.obter_opcoes_obrigatorias(
            "email.destinatarios",
            "sucesso" if status == "sucesso" else "erro"
        )[0]
    )

    anexos = anexos.copy() if anexos else []
    if anexar_log:
        mensagem_email += "<br>Todos os detalhes do processamento estão no log em anexo."
        anexos.append(bot.logger.CAMINHO_LOG_RAIZ)

    # ler corpo do html e formatar as variáveis
    html = CAMINHO_EMAIL_SIMPLES.path.read_text(encoding="utf-8")
    for template, substituto in (("{nome_bot}", nome_bot),
                                 ("{assunto}",  assunto),
                                 ("{mensagem}", mensagem_email)):
        html = html.replace(template, substituto)

    bot.email.enviar_email(destinatarios, assunto, html, anexos)

__all__ = [
    "notificar_email_simples",
]