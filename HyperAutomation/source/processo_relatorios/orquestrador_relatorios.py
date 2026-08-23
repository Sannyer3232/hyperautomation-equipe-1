"""
Orquestrador do Processo 5 - Relatórios e Gerência
Executa a consolidação, cálculo de indicadores e versionamento de relatórios gerenciais.
"""
from pathlib import Path
from typing import Dict, Any, Optional
from .logger_relatorios import LoggerRelatorios
from .consolidador import ConsolidadorDados
from .metricas import CalculadoraMetricas
from .gerador_relatorio import GeradorRelatorios


class ProcessoRelatorios:
    """Orquestrador do Processo 5 (Relatórios, Métricas e Governança)."""

    def __init__(
        self,
        caminho_planilha_mestra: Optional[Path] = None,
        caminho_planilha_sac: Optional[Path] = None,
        dir_saida: Optional[Path] = None
    ):
        self.logger = LoggerRelatorios()
        self.consolidador = ConsolidadorDados(
            caminho_mestra=caminho_planilha_mestra,
            caminho_sac=caminho_planilha_sac
        )
        self.gerador = GeradorRelatorios(dir_saida=dir_saida)

    def executar(self) -> Dict[str, Any]:
        """Executa a rotina completa do Processo 5."""
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO PROCESSO 5 - RELATÓRIOS E GERÊNCIA")
        self.logger.info("=" * 60)

        try:
            # 1. Consolidação dos dados
            self.logger.info("[ETAPA 1/3] Consolidando dados da Planilha Mestra e SAC...")
            dados_consolidados = self.consolidador.consolidar()
            total_clientes = dados_consolidados.get("total_clientes", 0)
            self.logger.info(f"  -> Total de registros consolidados: {total_clientes}")

            # 2. Cálculo de métricas e indicadores
            self.logger.info("[ETAPA 2/3] Calculando métricas e indicadores de performance (KPIs)...")
            metricas = CalculadoraMetricas.calcular(dados_consolidados)

            kpi_cad = metricas["kpis_cadastro_processo3"]
            kpi_sac = metricas["kpis_sac_processo4"]
            kpi_efi = metricas["kpis_eficiencia_global"]

            self.logger.metrica("Cadastros Aprovados", f"{kpi_cad['cadastrados_com_sucesso']} ({kpi_cad['taxa_aprovacao_percentual']}%)")
            self.logger.metrica("Atendimentos SAC", f"{kpi_sac['comunicados_com_sucesso']} ({kpi_sac['taxa_sucesso_comunicacao_percentual']}%)")
            self.logger.metrica("Eficiência Global", f"{kpi_efi['taxa_conclusao_ponta_a_ponta_percentual']}% [{kpi_efi['eficiencia_esteira']}]")

            # 3. Geração de relatórios versionados
            self.logger.info("[ETAPA 3/3] Gerando relatórios versionados (Excel, Markdown e JSON)...")
            arquivos_gerados = self.gerador.gerar_todos(dados_consolidados, metricas)

            self.logger.info(f"  [OK] Excel: {arquivos_gerados['excel'].name}")
            self.logger.info(f"  [OK] Markdown: {arquivos_gerados['markdown'].name}")
            self.logger.info(f"  [OK] JSON: {arquivos_gerados['json'].name}")
            self.logger.info(f"  [OK] Diretório: {arquivos_gerados['dir_saida']}")

            self.logger.info("=" * 60)
            self.logger.info("PROCESSO 5 FINALIZADO COM SUCESSO")
            self.logger.info("=" * 60)

            return {
                "sucesso": True,
                "total_clientes": total_clientes,
                "metricas": metricas,
                "relatorios": arquivos_gerados
            }

        except Exception as erro:
            self.logger.error("Falha durante a execução do Processo 5", exc=erro)
            return {
                "sucesso": False,
                "erro": str(erro),
                "total_clientes": 0
            }


def executar_processo5(
    caminho_planilha_mestra: Optional[Path] = None,
    caminho_planilha_sac: Optional[Path] = None,
    dir_saida: Optional[Path] = None
) -> Dict[str, Any]:
    """Função utilitária para execução direta do Processo 5."""
    processo = ProcessoRelatorios(
        caminho_planilha_mestra=caminho_planilha_mestra,
        caminho_planilha_sac=caminho_planilha_sac,
        dir_saida=dir_saida
    )
    return processo.executar()
