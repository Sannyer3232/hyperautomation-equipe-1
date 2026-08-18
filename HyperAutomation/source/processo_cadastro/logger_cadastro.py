"""
Módulo de Logs e Monitoramento - Processo 3 (Cadastro)
Padronizado conforme Roteiro 13: Data/Hora → Processo → Status → Erro/Motivo
"""
import logging
from datetime import datetime
from pathlib import Path


class LoggerCadastro:
    """
    Sistema de log estruturado e monitoramento para o Processo 3 - Cadastro.
    Garante rastreabilidade de todas as etapas (Validação, Consulta, Cadastro, Fallback, Planilha).
    """

    def __init__(self, log_dir: Path = None):
        if log_dir is None:
            # Raiz do projeto / logs
            base_dir = Path(__file__).resolve().parents[3]
            self.log_dir = base_dir / "logs"
        else:
            self.log_dir = Path(log_dir)

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "processo3_cadastro.log"

        self.logger = logging.getLogger("Processo3_Cadastro")
        self.logger.setLevel(logging.INFO)

        # Evita duplicação de handlers
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "[%(asctime)s] [PROCESSO 3 - CADASTRO] [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def registrar(self, status: str, detalhe: str, erro_motivo: str = ""):
        """
        Registra uma linha de log no padrão estruturado do Roteiro 13:
        Data/Hora → Processo 3 → Status → Detalhe/Erro
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"{timestamp} → Processo 3 → {status} → {detalhe}"
        if erro_motivo:
            msg += f" | Motivo/Erro: {erro_motivo}"

        log_display = f"  [P3 LOG] [{status}] {detalhe}" + (f" (Motivo: {erro_motivo})" if erro_motivo else "")
        try:
            print(log_display)
        except UnicodeEncodeError:
            print(log_display.encode("ascii", errors="replace").decode("ascii"))

        if status.upper() in ("ERRO", "FALHA", "CRITICO"):
            self.logger.error(msg)
        elif status.upper() in ("AVISO", "FALLBACK", "DUPLICADO"):
            self.logger.warning(msg)
        else:
            self.logger.info(msg)

    def info(self, detalhe: str):
        self.registrar("INFO", detalhe)

    def sucesso(self, detalhe: str):
        self.registrar("SUCESSO", detalhe)

    def duplicado(self, detalhe: str, motivo: str = "Registro já existente no portal"):
        self.registrar("DUPLICADO", detalhe, erro_motivo=motivo)

    def aviso(self, detalhe: str, motivo: str = ""):
        self.registrar("AVISO", detalhe, erro_motivo=motivo)

    def erro(self, detalhe: str, erro: str = ""):
        self.registrar("ERRO", detalhe, erro_motivo=erro)

    def fallback(self, detalhe: str, motivo: str = ""):
        self.registrar("FALLBACK", detalhe, erro_motivo=motivo)
