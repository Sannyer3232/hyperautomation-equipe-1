"""
Pacote Processo 3 - Cadastro (HyperAutomation)
Módulo responsável pela consulta, validação, identificação de duplicidades e cadastro dos clientes no ERP Portal Fake a partir da Planilha Mestra.
"""
from .validador_cadastro import ValidadorCadastro
from .leitor_planilha import LeitorPlanilhaCadastro
from .integrador_portal import CadastradorPortalFake
from .logger_cadastro import LoggerCadastro
from .orquestrador_cadastro import OrquestradorCadastro, executar_processo3

__all__ = [
    "ValidadorCadastro",
    "LeitorPlanilhaCadastro",
    "CadastradorPortalFake",
    "LoggerCadastro",
    "OrquestradorCadastro",
    "executar_processo3",
]
