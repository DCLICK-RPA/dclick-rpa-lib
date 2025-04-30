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
        tipo: Literal["sucesso", "erro"],
        *mensagem: str,
        anexar_log: bool = True,
        anexos: list[bot.sistema.Caminho] | None = None,
        destinatarios: list[bot.tipagem.email] | None = None,
    ) -> None:
    """Enviar a notificação padrão DClick via e-mail com o Assunto `nome_bot - tipo`
    - `mensagem` será concatenada com `<br>`
    - `anexar_log` para anexar o log raiz
    - `anexos` caminhos para anexos adicionais
    - `destinatarios` especificar os destinatários da notificação
        - `destinatarios=None` Variáveis utilizadas `[email.destinatarios] -> "sucesso", "erro"`
    - Variáveis utilizadas `[email.enviar] -> user, password, host, [port: 587, ssl: False, ]`"""
    assunto = f"{nome_bot} - {tipo.capitalize()}"
    mensagem_email = "<br>".join(mensagem)
    destinatarios = destinatarios if destinatarios != None else separar_destinatarios(
        bot.configfile.obter_opcoes_obrigatorias("email.destinatarios", tipo)[0]
    )

    anexos = anexos.copy() if anexos else []
    if anexar_log:
        mensagem_email += "<br>Todos os detalhes do processamento estão no log em anexo."
        anexos.append(bot.logger.caminho_log_raiz())

    with open(CAMINHO_EMAIL_SIMPLES.string, encoding="utf-8") as arquivo:
        # ler corpo do html e formatar as variáveis
        html = arquivo.read().replace("{0}", assunto) \
                             .replace("{1}", mensagem_email) \
                             .replace("{2}", nome_bot)

    bot.email.enviar_email(destinatarios, assunto, html, anexos)

__all__ = [
    "notificar_email_simples",
]