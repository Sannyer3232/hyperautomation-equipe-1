"""
Módulo de Métricas e Indicadores - Processo 5 (Relatórios e Gerência)
Responsável pelo cálculo analítico e consolidação dos KPIs do projeto.
"""
from typing import Dict, List, Any
from datetime import datetime


class CalculadoraMetricas:
    """Calcula e formata as métricas e indicadores de desempenho de todos os processos."""

    @staticmethod
    def calcular(dados_consolidados: Dict[str, Any]) -> Dict[str, Any]:
        clientes: List[Dict[str, Any]] = dados_consolidados.get("clientes", [])
        total_clientes = len(clientes)

        # Contagens de Status de Cadastro (Processo 3)
        cadastrados = 0
        duplicados = 0
        erros_validacao = 0
        erros_cadastro = 0
        em_andamento = 0

        # Contagens de Atendimento SAC (Processo 4)
        sac_total = 0
        sac_comunicados = 0
        sac_pendentes = 0
        sac_nao_iniciado = 0

        distribuicao_status_cadastro = {}
        distribuicao_status_sac = {}

        for c in clientes:
            st_cad = str(c.get("status_cadastro") or "NÃO INFORMADO").strip().upper()
            st_sac = str(c.get("status_sac") or "NÃO INICIADO").strip().upper()

            # Agrupamento de cadastro
            distribuicao_status_cadastro[st_cad] = distribuicao_status_cadastro.get(st_cad, 0) + 1
            if st_cad in ["CONCLUIDO_P3", "CADASTRADO", "CONCLUIDO", "ATIVO"]:
                cadastrados += 1
            elif st_cad in ["DUPLICADO_P3", "DUPLICADO"]:
                duplicados += 1
            elif "VALIDACAO" in st_cad or "REJEITADO" in st_cad:
                erros_validacao += 1
            elif "ERRO" in st_cad or "FALHA" in st_cad:
                erros_cadastro += 1
            else:
                em_andamento += 1

            # Agrupamento de SAC
            distribuicao_status_sac[st_sac] = distribuicao_status_sac.get(st_sac, 0) + 1
            if st_sac == "COMUNICADO":
                sac_total += 1
                sac_comunicados += 1
            elif st_sac == "PENDENTE_CONTATO":
                sac_total += 1
                sac_pendentes += 1
            elif st_sac != "NÃO INICIADO":
                sac_total += 1
            else:
                sac_nao_iniciado += 1

        # Cálculo de Taxas Percentuais
        taxa_aprovacao_cadastro = round((cadastrados / total_clientes * 100), 2) if total_clientes > 0 else 0.0
        taxa_duplicidade = round((duplicados / total_clientes * 100), 2) if total_clientes > 0 else 0.0
        taxa_sucesso_sac = round((sac_comunicados / sac_total * 100), 2) if sac_total > 0 else 0.0
        taxa_conclusao_ponta_a_ponta = round((sac_comunicados / total_clientes * 100), 2) if total_clientes > 0 else 0.0

        return {
            "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "resumo_geral": {
                "total_clientes_processados": total_clientes,
                "total_registros_planilha_mestra": dados_consolidados.get("total_mestra", total_clientes),
                "total_registros_sac": dados_consolidados.get("total_sac", sac_total),
            },
            "kpis_cadastro_processo3": {
                "cadastrados_com_sucesso": cadastrados,
                "duplicados_identificados": duplicados,
                "erros_validacao": erros_validacao,
                "erros_cadastro_portal": erros_cadastro,
                "em_andamento": em_andamento,
                "taxa_aprovacao_percentual": taxa_aprovacao_cadastro,
                "taxa_duplicidade_percentual": taxa_duplicidade,
            },
            "kpis_sac_processo4": {
                "total_atendimentos_sac": sac_total,
                "comunicados_com_sucesso": sac_comunicados,
                "pendentes_contato_fallback": sac_pendentes,
                "nao_iniciados": sac_nao_iniciado,
                "taxa_sucesso_comunicacao_percentual": taxa_sucesso_sac,
            },
            "kpis_eficiencia_global": {
                "taxa_conclusao_ponta_a_ponta_percentual": taxa_conclusao_ponta_a_ponta,
                "eficiencia_esteira": "ALTA" if taxa_conclusao_ponta_a_ponta >= 80 else ("MÉDIA" if taxa_conclusao_ponta_a_ponta >= 50 else "BAIXA")
            },
            "distribuicao_status_cadastro": distribuicao_status_cadastro,
            "distribuicao_status_sac": distribuicao_status_sac,
        }
