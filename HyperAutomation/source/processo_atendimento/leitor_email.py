"""
Módulo responsável pela leitura de e-mails de solicitação dos clientes e download de anexos.
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
    Classe responsável por conectar à caixa de entrada (IMAP) ou simular a leitura de solicitações
    recebidas por e-mail dos clientes e salvar os anexos no diretório Downloads do ERP.
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
        Lê os e-mails pendentes/não lidos da caixa de entrada.
        Retorna uma lista de dicionários contendo os metadados e caminhos dos anexos baixados.
        Possui fallback automático para solicitações simuladas se o IMAP não estiver disponível.
        """
        solicitacoes = []

        if self.email_user and self.email_pass and self.imap_server:
            try:
                print(f"[LEITOR EMAIL] Conectando ao servidor IMAP {self.imap_server}...")
                mail = imaplib.IMAP4_SSL(self.imap_server)
                mail.login(str(self.email_user), str(self.email_pass))
                mail.select("inbox")

                status, messages = mail.search(None, '(UNSEEN SUBJECT "Solicitação de Atendimento")')
                email_ids = messages[0].split()

                print(f"[LEITOR EMAIL] Encontrados {len(email_ids)} e-mails pendentes.")

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
                print(f"[AVISO LEITOR EMAIL] Não foi possível conectar via IMAP ({e}). Alternando para modo simulado de atendimento.")

        # Modo Simulado (Demonstrativo e Teste Local)
        return self._gerar_solicitacoes_simuladas()

    def _processar_mensagem(self, msg) -> dict:
        """Processa a mensagem individual do e-mail e salva anexos."""
        remetente = msg.get("From", "cliente@exemplo.com")
        assunto = msg.get("Subject", "Solicitação sem assunto")

        anexos_baixados = self.baixar_anexos(msg)

        return {
            "remetente": remetente,
            "assunto": assunto,
            "anexos": anexos_baixados,
            "dados_cliente": {
                "Nome": "Cliente",
                "Sobrenome": "Solicitante",
                "CPF": "11122233344",
                "Email": remetente,
                "Telefone": "(92) 99999-1111",
                "Endereco": "Av. Brasil, 1000 - Manaus/AM"
            }
        }

    def baixar_anexos(self, mensagem) -> list:
        """
        Extrai e baixa os anexos de uma mensagem de e-mail recebida para a pasta Downloads do ERP.
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
                print(f"[LEITOR EMAIL] Anexo salvo: {caminho_salvo.name}")

        return anexos

    def _gerar_solicitacoes_simuladas(self) -> list:
        """
        Cria arquivos de teste demonstrativos em ERP_Portal_Fake/Downloads para permitir
        a execução ponta a ponta do fluxo do Processo 1 sem depender de e-mails externos.
        """
        print("[LEITOR EMAIL] Carregando solicitações de teste em ERP_Portal_Fake/Downloads...")

        # Solicitação 1: Completa (Válida)
        arq_rg = self.download_dir / "Documento_Identidade_Ana_Silva.pdf"
        arq_comp = self.download_dir / "Comprovante_Residencia_Ana_Silva.pdf"
        arq_ficha = self.download_dir / "Ficha_Cadastro_Ana_Silva.docx"

        for arq in [arq_rg, arq_comp, arq_ficha]:
            if not arq.exists():
                with open(arq, "w", encoding="utf-8") as f:
                    f.write(f"Conteudo simulado de validação para {arq.name}")

        solic_1 = {
            "id": "SOLIC-001",
            "protocolo": "2026-0001",
            "remetente": "ana.silva@exemplo.com",
            "assunto": "Solicitação de Cadastro Completa - Ana Silva",
            "dados_cliente": {
                "nome": "Ana",
                "sobrenome": "Silva",
                "cpf": "11122233344",
                "email": "ana.silva@exemplo.com",
                "telefone": "(92) 99888-1122",
                "nascimento": "1992-05-15",
                "endereco": "Rua das Flores, 123 - Manaus/AM",
                "observacao": "Documentação completa enviada por e-mail."
            },
            "anexos": [str(arq_rg), str(arq_comp), str(arq_ficha)]
        }

        return [solic_1]

def ler_emails_pendentes():
    leitor = LeitorEmail()
    return leitor.ler_emails_pendentes()

def baixar_anexos(mensagem):
    leitor = LeitorEmail()
    return leitor.baixar_anexos(mensagem)
