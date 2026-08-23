"""
Ponto de Entrada Principal - HyperAutomation (Processos 1 a 5 Integrados)
Executa a orquestração ponta a ponta:
Processo 1 (Atendimento) -> Processo 2 (Organização) -> Processo 3 (Cadastro) -> Processo 4 (SAC) -> Processo 5 (Relatórios)
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "HyperAutomation"
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "source"))
sys.path.insert(0, str(BASE_DIR / "resources"))

from source.orquestrador import main

if __name__ == "__main__":
    main()
