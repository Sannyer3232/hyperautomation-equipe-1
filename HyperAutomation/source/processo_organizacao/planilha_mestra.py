"""
Re-export do módulo unificado da Planilha Mestra a partir de common.planilha_mestra.
Mantém 100% de compatibilidade com os scripts e relatórios do Processo 2.
"""
from common.planilha_mestra import GerenciadorPlanilha, PlanilhaMestra

__all__ = ["GerenciadorPlanilha", "PlanilhaMestra"]
