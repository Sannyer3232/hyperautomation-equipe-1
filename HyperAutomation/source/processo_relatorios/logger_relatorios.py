"""
Módulo de Logging e Monitoramento - Processo 5 (Relatórios e Gerência)
"""
import logging
from pathlib import Path
from datetime import datetime


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "ERP_Portal_Fake").exists() or (parent / "HyperAutomation").exists():
            return parent
    return Path(__file__).resolve().parents[3]


class LoggerRelatorios:
    """Gerenciador de logs e monitoramento para o Processo 5."""

    def __init__(self, log_dir: Path = None):
        self.root_dir = get_project_root()
        self.log_dir = Path(log_dir) if log_dir else (self.root_dir / "logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "processo5_relatorios.log"

        self.logger = logging.getLogger("processo5_relatorios")
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

            file_handler = logging.FileHandler(str(self.log_file), encoding="utf-8")
            file_handler.setFormatter(formatter)

            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(stream_handler)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str, exc: Exception = None):
        if exc:
            self.logger.error(f"{msg}: {exc}", exc_info=True)
        else:
            self.logger.error(msg)

    def metrica(self, nome: str, valor):
        self.logger.info(f"[MÉTRICA] {nome}: {valor}")
