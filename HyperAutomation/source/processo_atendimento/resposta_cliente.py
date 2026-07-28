"""
Módulo responsável por enviar respostas por e-mail informando o status ao cliente.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class NotificadorCliente:
        """
        Classe responsável por enviar e-mails de resposta automática aos clientes.
        """
        def __init__(self):
            smtp_server_env = os.getenv("SMTP_SERVER")
            self.smtp_server = smtp_server_env if smtp_server_env else "smtp.gmail.com"

            smtp_port_env = os.getenv("SMTP_PORT")
            if smtp_port_env and smtp_port_env.strip().isdigit():
                self.smtp_port = int(smtp_port_env.strip())
            else:
                self.smtp_port = 587

            self.remetente = os.getenv("EMAIL_REMETENTE")
            self.senha = os.getenv("EMAIL_SENHA")

        def enviar_resposta(self, email_destino: str, protocolo: str, aprovado: bool, pendencias: list = None) -> bool:
            """
            Envia e-mail de notificação de status para o cliente.
            """
            if not self.remetente or not self.senha:
                print("[AVISO NOTIFICADOR] Credenciais de e-mail não configuradas no .env. Ignorando envio real.")
                return False

            msg = MIMEMultipart("alternative")
            msg["From"] = self.remetente
            msg["To"] = email_destino

            if aprovado:
                msg["Subject"] = f"Solicitação Aprovada - Protocolo #{protocolo}"
                corpo_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2 style="color: #2e7d32;">Solicitação Recebida com
                        Sucesso!</h2>
                        <p>Olá,</p>
                        <p>Sua documentação relativa ao protocolo
                         <strong>#{protocolo}</strong> foi validada e aprovada pelo Setor de Atendimento da
                 <strong>Empresa Portal Fake</strong>.</p>
                        <p>Sua solicitação foi encaminhada para o setor responsável
                         para prosseguimento.</p>
                        <br>
                        <p>Atenciosamente,<br><strong>Equipe de Atendimento
                        Automatizado</strong></p>
                    </body>
                </html>
                """
            else:
                msg["Subject"] = f"Pendência na Documentação - Protocolo #{protocolo}"
                itens_pendentes = "".join([f"<li>{item}</li>" for item in (pendencias or ["Documentação incompleta"])])
                corpo_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2 style="color: #c62828;">Pendência Identificada na
                         Solicitação</h2>
                        <p>Olá,</p>
                        <p>Analisamos sua solicitação relativa ao protocolo
                        <strong>#{protocolo}</strong> e identificamos as seguintes pendências:</p>
                        <ul>
                            {itens_pendentes}
                        </ul>
                        <p>Por favor, responda a este e-mail enviando os documentos
                         corrigidos.</p>
                        <br>
                        <p>Atenciosamente,<br><strong>Equipe de Atendimento
                        Automatizado</strong></p>
                    </body>
                </html>
                """

            msg.attach(MIMEText(corpo_html, "html"))

            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.remetente, self.senha)
                    server.send_message(msg)
                    print(f"[NOTIFICADOR] E-mail enviado com sucesso para {email_destino}.")

                    return True

            except Exception as e:

                    print(f"[ERRO NOTIFICADOR] Falha ao enviar e-mail para {email_destino}: {e}")

                    return False