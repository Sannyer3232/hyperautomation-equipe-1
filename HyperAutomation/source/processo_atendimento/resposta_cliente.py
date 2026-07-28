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
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        if not self.smtp_server:
            self.smtp_server = "smtp.gmail.com"
        
        smtp_port_env = os.getenv("SMTP_PORT", "587")
        self.smtp_port = int(smtp_port_env) if smtp_port_env and smtp_port_env.isdigit() else 587
        
        self.remetente = os.getenv("EMAIL_REMETENTE")
        self.senha = os.getenv("EMAIL_SENHA")

    def enviar_resposta(self, email_destino: str, protocolo: str, aprovado: bool, pendencias: list = None) -> bool:
        """
        Envia e-mail de notificação de status para o cliente.
        """
        if not self.remetente or not self.senha:
            print(f"[AVISO NOTIFICADOR] Credenciais de e-mail não configuradas no .env. Simulado envio para: {email_destino} (Aprovado: {aprovado})")
            return True

        msg = MIMEMultipart("alternative")
        msg["From"] = self.remetente
        msg["To"] = email_destino

        if aprovado:
            msg["Subject"] = f"Solicitação Aprovada - Protocolo #{protocolo}"
            corpo_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="background-color: #f4f6f8; padding: 20px; border-radius: 8px;">
                        <h2 style="color: #2e7d32; margin-top: 0;">Solicitação Aprovada com Sucesso!</h2>
                        <p>Olá,</p>
                        <p>Sua documentação referente ao protocolo <strong>#{protocolo}</strong> foi devidamente validada e aprovada pelo Setor de Atendimento da <strong>Empresa Portal Fake</strong>.</p>
                        <p>Seu cadastro foi registrado no sistema e encaminhado para os setores responsáveis para prosseguimento.</p>
                        <br>
                        <p style="font-size: 12px; color: #777;">Atenciosamente,<br><strong>Equipe de Atendimento Automatizado - Hyperautomation</strong></p>
                    </div>
                </body>
            </html>
            """
        else:
            msg["Subject"] = f"Pendência na Documentação - Protocolo #{protocolo}"
            itens_pendentes = "".join([f"<li style='margin-bottom: 5px;'>{item}</li>" for item in (pendencias or ["Documentação incompleta"])])
            corpo_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <div style="background-color: #fff4f4; padding: 20px; border-radius: 8px; border: 1px solid #ffcdd2;">
                        <h2 style="color: #c62828; margin-top: 0;">Pendência Identificada na Solicitação</h2>
                        <p>Olá,</p>
                        <p>Analisamos sua solicitação relativa ao protocolo <strong>#{protocolo}</strong> e identificamos as seguintes pendências na documentação:</p>
                        <ul style="color: #b71c1c;">
                            {itens_pendentes}
                        </ul>
                        <p>Por favor, envie os documentos corrigidos em anexo para darmos continuidade ao seu atendimento.</p>
                        <br>
                        <p style="font-size: 12px; color: #777;">Atenciosamente,<br><strong>Equipe de Atendimento Automatizado - Hyperautomation</strong></p>
                    </div>
                </body>
            </html>
            """

        msg.attach(MIMEText(corpo_html, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.remetente, self.senha)
                server.send_message(msg)
                print(f"[NOTIFICADOR] E-mail enviado com sucesso para {email_destino} (Protocolo: #{protocolo}).")
                return True
        except Exception as e:
            print(f"[AVISO NOTIFICADOR] Falha ao enviar e-mail real para {email_destino}: {e}. (Continuando execução do fluxo)")
            return False

def enviar_resposta_cliente(email_destino, aprovado=True, mensagem=""):
    notificador = NotificadorCliente()
    return notificador.enviar_resposta(email_destino, protocolo="2026-0001", aprovado=aprovado, pendencias=[mensagem] if mensagem else None)
