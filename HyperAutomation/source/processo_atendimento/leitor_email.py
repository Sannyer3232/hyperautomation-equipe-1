"""
Módulo responsável pelo monitoramento da caixa de entrada, leitura de e-mails com respostas de clientes e download dos PDFs unificados com a Ficha Assinada.
"""
import os
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class LeitorEmail:
    """
    Classe responsável por conectar à caixa de entrada (IMAP) e monitorar e-mails de retorno
    enviados pelos clientes contendo a Ficha Assinada e os Documentos em um único PDF.
    """
    def __init__(self, download_dir: Path = None):
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.email_user = os.getenv("EMAIL_REMETENTE")
        self.email_pass = os.getenv("EMAIL_SENHA")

        if download_dir:
            self.download_dir = Path(download_dir)
        else:
            self.download_dir = (Path(__file__).resolve().parents[3] / "ERP_Portal_Fake" / "Downloads").resolve()

        self.download_dir.mkdir(parents=True, exist_ok=True)

    def ler_emails_pendentes(self) -> list:
        """
        Monitora a caixa de entrada por e-mails de resposta dos clientes contendo os documentos e a ficha assinada.
        """
        solicitacoes = []

        if self.email_user and self.email_pass and self.imap_server:
            try:
                print(f"[LEITOR EMAIL] Monitorando caixa de entrada no servidor IMAP {self.imap_server}...")
                mail = imaplib.IMAP4_SSL(self.imap_server)
                mail.login(str(self.email_user), str(self.email_pass))
                mail.select("inbox")

                # Busca por e-mails não lidos de resposta ou retorno de solicitação
                status, messages = mail.search(None, '(UNSEEN SUBJECT "Assinatura")')
                email_ids = messages[0].split()

                print(f"[LEITOR EMAIL] Encontrados {len(email_ids)} e-mails de retorno de clientes.")

                for mail_id in email_ids:
                    _, msg_data = mail.fetch(mail_id, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            solicitacao = self._processar_mensagem(msg)
                            if solicitacao:
                                solicitacoes.append(solicitacao)

                mail.close()
                mail.logout()
                if solicitacoes:
                    return solicitacoes

            except Exception as e:
                print(f"[AVISO LEITOR EMAIL] Não foi possível conectar via IMAP ({e}). Alternando para modo de monitoramento simulado.")

        # Modo de Teste e Monitoramento Simulado
        return self._gerar_retorno_simulado()

    def _processar_mensagem(self, msg) -> dict:
        """Processa a mensagem individual do e-mail retornado pelo cliente e baixa anexos."""
        remetente = msg.get("From", "cliente@exemplo.com")
        assunto = msg.get("Subject", "Retorno de Documentos")

        anexos_baixados = self.baixar_anexos(msg)

        return {
            "remetente": remetente,
            "assunto": assunto,
            "anexos": anexos_baixados,
            "dados_cliente": {
                "Nome": "Ana",
                "Sobrenome": "Silva",
                "CPF": "11122233344",
                "Email": remetente,
                "Telefone": "(92) 99888-1122",
                "Endereco": "Rua das Flores, 123 - Manaus/AM"
            }
        }

    def baixar_anexos(self, mensagem) -> list:
        """
        Extrai e salva os PDFs baixados da mensagem de e-mail na pasta ERP_Portal_Fake/Downloads.
        """
        anexos = []
        if not hasattr(mensagem, "walk"):
            return anexos

        for part in mensagem.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if filename:
                filename = decode_header(filename)[0][0]
                if isinstance(filename, bytes):
                    filename = filename.decode()

                caminho_salvo = self.download_dir / filename
                with open(caminho_salvo, "wb") as f:
                    f.write(part.get_payload(decode=True))

                anexos.append(caminho_salvo)
                print(f"[LEITOR EMAIL] PDF de retorno salvo em Downloads: {caminho_salvo.name}")

        return anexos

    def _gerar_retorno_simulado(self) -> list:
        """
        Cria o PDF unificado simulado (Ficha Assinada + Documentos) em ERP_Portal_Fake/Downloads
        para demonstrar a validação do retorno do cliente.
        """
        print("[LEITOR EMAIL] Monitoramento encontrou e-mail de retorno do cliente com PDF Único...")

        pdf_unificado = self.download_dir / "Ficha_Assinada_e_Documentos_Ana_Silva.pdf"

        if not pdf_unificado.exists():
            with open(pdf_unificado, "w", encoding="utf-8") as f:
                f.write("%PDF-1.4 Conteúdo Simulado: Ficha Cadastral Assinada + RG/CPF + Comprovante de Residência")

        retorno_cliente = {
            "id": "RET-001",
            "protocolo": "2026-0001",
            "remetente": "ana.silva@exemplo.com",
            "assunto": "RES: Assinatura de Ficha Cadastral - Protocolo #2026-0001",
            "dados_cliente": {
                "nome": "Ana",
                "sobrenome": "Silva",
                "cpf": "11122233344",
                "email": "ana.silva@exemplo.com",
                "telefone": "(92) 99888-1122",
                "nascimento": "1992-05-15",
                "endereco": "Rua das Flores, 123 - Manaus/AM",
                "observacao": "Ficha assinada e documentos anexados em PDF único."
            },
            "anexos": [str(pdf_unificado)]
        }

        return [retorno_cliente]

def ler_emails_pendentes():
    leitor = LeitorEmail()
    return leitor.ler_emails_pendentes()

def baixar_anexos(mensagem):
    leitor = LeitorEmail()
    return leitor.baixar_anexos(mensagem)
