"""
Módulo de Geração e Versionamento de Relatórios - Processo 5 (Relatórios e Gerência)
Gera relatórios executivos em Excel estilizado, Markdown e JSON estruturado com versionamento.
"""
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "ERP_Portal_Fake").exists() or (parent / "HyperAutomation").exists():
            return parent
    return Path(__file__).resolve().parents[3]


class GeradorRelatorios:
    """Gera relatórios consolidados em Excel, Markdown e JSON com versionamento temporal."""

    def __init__(self, dir_saida: Optional[Path] = None):
        root = get_project_root()
        if dir_saida:
            self.dir_saida = Path(dir_saida)
        else:
            self.dir_saida = root / "ERP_Portal_Fake" / "Relatorios_Gerenciais"

        self.dir_saida.mkdir(parents=True, exist_ok=True)

    def gerar_todos(self, dados_consolidados: Dict[str, Any], metricas: Dict[str, Any]) -> Dict[str, Path]:
        """Gera todos os formatos de relatório (Excel, Markdown e JSON) de forma versionada."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        caminho_excel = self.gerar_excel(dados_consolidados, metricas, timestamp)
        caminho_md = self.gerar_markdown(metricas, timestamp)
        caminho_json = self.gerar_json(dados_consolidados, metricas, timestamp)

        return {
            "excel": caminho_excel,
            "markdown": caminho_md,
            "json": caminho_json,
            "timestamp": timestamp,
            "dir_saida": self.dir_saida
        }

    def gerar_excel(self, dados_consolidados: Dict[str, Any], metricas: Dict[str, Any], timestamp: str) -> Path:
        """Cria planilha executiva formatada em Excel com abas de Dashboard, Base Consolidada e Status."""
        wb = Workbook()

        # Estilos profissionais
        cor_primaria = "1F4E79"       # Azul Corporativo
        cor_secundaria = "2E75B6"     # Azul Claro
        cor_sucesso = "C6EFCE"        # Verde suave
        cor_texto_sucesso = "006100"
        cor_alerta = "FFEB9C"         # Amarelo suave
        cor_fundo_cinza = "F2F2F2"

        fonte_titulo = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
        fonte_secao = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
        fonte_subsecao = Font(name="Calibri", size=11, bold=True, color="1F4E79")
        fonte_cabecalho = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        fonte_destaque = Font(name="Calibri", size=14, bold=True, color="1F4E79")
        fonte_normal = Font(name="Calibri", size=10)
        fonte_bold = Font(name="Calibri", size=10, bold=True)

        fill_titulo = PatternFill(start_color=cor_primaria, end_color=cor_primaria, fill_type="solid")
        fill_secao = PatternFill(start_color=cor_secundaria, end_color=cor_secundaria, fill_type="solid")
        fill_cinza = PatternFill(start_color=cor_fundo_cinza, end_color=cor_fundo_cinza, fill_type="solid")
        fill_sucesso = PatternFill(start_color=cor_sucesso, end_color=cor_sucesso, fill_type="solid")

        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_left = Alignment(horizontal="left", vertical="center")
        align_right = Alignment(horizontal="right", vertical="center")

        thin_border = Side(style="thin", color="D9D9D9")
        border_all = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)

        # =====================================================================
        # ABA 1: DASHBOARD GERENCIAL & KPIS
        # =====================================================================
        ws_dash = wb.active
        ws_dash.title = "Dashboard Gerencial"
        ws_dash.views.sheetView[0].showGridLines = True

        # Banner de Título
        ws_dash.merge_cells("A1:G2")
        ws_dash["A1"] = "RELATÓRIO GERENCIAL - HYPERAUTOMATION"
        ws_dash["A1"].font = fonte_titulo
        ws_dash["A1"].fill = fill_titulo
        ws_dash["A1"].alignment = align_center

        ws_dash["A3"] = f"Gerado em: {metricas.get('gerado_em', '')} | Versão: v{timestamp}"
        ws_dash["A3"].font = Font(name="Calibri", size=10, italic=True, color="595959")

        # Cartões de Destaque Executivo (Linha 5 a 7)
        kpis_topo = [
            ("TOTAL DE CLIENTES", metricas["resumo_geral"]["total_clientes_processados"], "B5:C6"),
            ("CADASTROS APROVADOS", metricas["kpis_cadastro_processo3"]["cadastrados_com_sucesso"], "D5:E6"),
            ("ATENDIMENTOS SAC", metricas["kpis_sac_processo4"]["comunicados_com_sucesso"], "F5:G6"),
        ]

        for label, valor, range_celulas in kpis_topo:
            c1 = range_celulas.split(":")[0]
            col_letter = c1[0]
            row_num = int(c1[1:])

            ws_dash.cell(row=row_num, column=ord(col_letter) - ord('A') + 1, value=label).font = fonte_bold
            ws_dash.cell(row=row_num, column=ord(col_letter) - ord('A') + 1).fill = fill_cinza
            ws_dash.cell(row=row_num, column=ord(col_letter) - ord('A') + 1).alignment = align_center

            val_cell = ws_dash.cell(row=row_num + 1, column=ord(col_letter) - ord('A') + 1, value=valor)
            val_cell.font = fonte_destaque
            val_cell.fill = fill_sucesso
            val_cell.alignment = align_center

        # Tabela Detalhada de Indicadores por Processo (Linha 9 em diante)
        ws_dash.cell(row=9, column=1, value="INDICADORES DE PERFORMANCE (KPIS)").font = fonte_secao
        ws_dash.cell(row=9, column=1).fill = fill_secao
        ws_dash.merge_cells("A9:G9")

        linhas_indicadores = [
            ("Processo 1 & 2 - Recepção e Organização", "Total de Registros na Planilha Mestra", metricas["resumo_geral"]["total_registros_planilha_mestra"]),
            ("Processo 3 - Cadastro Portal Fake", "Cadastros Concluídos com Sucesso", metricas["kpis_cadastro_processo3"]["cadastrados_com_sucesso"]),
            ("Processo 3 - Cadastro Portal Fake", "Cadastros Duplicados Identificados", metricas["kpis_cadastro_processo3"]["duplicados_identificados"]),
            ("Processo 3 - Cadastro Portal Fake", "Erros de Validação de Dados", metricas["kpis_cadastro_processo3"]["erros_validacao"]),
            ("Processo 3 - Cadastro Portal Fake", "Falhas / Erros de Submissão no Portal", metricas["kpis_cadastro_processo3"]["erros_cadastro_portal"]),
            ("Processo 3 - Cadastro Portal Fake", "Taxa de Sucesso no Cadastro", f"{metricas['kpis_cadastro_processo3']['taxa_aprovacao_percentual']}%"),
            ("Processo 4 - SAC e Comunicação", "Total de Notificações SAC Processadas", metricas["kpis_sac_processo4"]["total_atendimentos_sac"]),
            ("Processo 4 - SAC e Comunicação", "E-mails Enviados com Sucesso (COMUNICADO)", metricas["kpis_sac_processo4"]["comunicados_com_sucesso"]),
            ("Processo 4 - SAC e Comunicação", "Contatos Pendentes / Fallback", metricas["kpis_sac_processo4"]["pendentes_contato_fallback"]),
            ("Processo 4 - SAC e Comunicação", "Taxa de Sucesso no Envio de E-mails", f"{metricas['kpis_sac_processo4']['taxa_sucesso_comunicacao_percentual']}%"),
            ("Eficiência Global da Automação", "Taxa de Conclusão Ponta a Ponta", f"{metricas['kpis_eficiencia_global']['taxa_conclusao_ponta_a_ponta_percentual']}%"),
            ("Eficiência Global da Automação", "Avaliação de Desempenho da Esteira", metricas["kpis_eficiencia_global"]["eficiencia_esteira"]),
        ]

        # Cabeçalho da Tabela
        headers_dash = ["Processo", "Indicador / Métrica", "Valor", "", "", "", ""]
        for col_idx, h in enumerate(headers_dash[:3], start=1):
            cell = ws_dash.cell(row=10, column=col_idx, value=h)
            cell.font = fonte_cabecalho
            cell.fill = fill_titulo
            cell.alignment = align_center

        for r_idx, (proc, ind, val) in enumerate(linhas_indicadores, start=11):
            c_proc = ws_dash.cell(row=r_idx, column=1, value=proc)
            c_ind = ws_dash.cell(row=r_idx, column=2, value=ind)
            c_val = ws_dash.cell(row=r_idx, column=3, value=val)

            c_proc.font = fonte_normal
            c_ind.font = fonte_bold if "Taxa" in ind or "Total" in ind else fonte_normal
            c_val.font = fonte_bold
            c_val.alignment = align_center

            for c in [c_proc, c_ind, c_val]:
                c.border = border_all

        # =====================================================================
        # ABA 2: BASE CONSOLIDADA (DETALHADA)
        # =====================================================================
        ws_base = wb.create_sheet(title="Base Consolidada")
        ws_base.views.sheetView[0].showGridLines = True

        headers_base = [
            "Protocolo", "CPF", "Nome do Cliente", "E-mail", "Telefone",
            "Status Cadastro", "Status SAC", "Tipo SAC", "Data Atendimento SAC",
            "Fase Concluída", "Observações"
        ]

        for col_idx, h in enumerate(headers_base, start=1):
            cell = ws_base.cell(row=1, column=col_idx, value=h)
            cell.font = fonte_cabecalho
            cell.fill = fill_titulo
            cell.alignment = align_center
            cell.border = border_all

        clientes: List[Dict[str, Any]] = dados_consolidados.get("clientes", [])
        for row_idx, cl in enumerate(clientes, start=2):
            valores = [
                cl.get("protocolo", ""),
                cl.get("cpf", ""),
                cl.get("nome", ""),
                cl.get("email", ""),
                cl.get("telefone", ""),
                cl.get("status_cadastro", ""),
                cl.get("status_sac", ""),
                cl.get("tipo_atendimento_sac", ""),
                cl.get("data_atendimento_sac", ""),
                cl.get("fase_concluida", ""),
                cl.get("observacao_sac") or cl.get("observacoes_cadastro") or ""
            ]
            for col_idx, val in enumerate(valores, start=1):
                cell = ws_base.cell(row=row_idx, column=col_idx, value=val)
                cell.font = fonte_normal
                cell.border = border_all
                if col_idx in [1, 2, 5, 6, 7, 8, 9]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

        # =====================================================================
        # ABA 3: DISTRIBUIÇÃO E STATUS
        # =====================================================================
        ws_dist = wb.create_sheet(title="Distribuição de Status")
        ws_dist.views.sheetView[0].showGridLines = True

        ws_dist.cell(row=1, column=1, value="Status de Cadastro (Processo 3)").font = fonte_subsecao
        ws_dist.cell(row=2, column=1, value="Status").font = fonte_cabecalho
        ws_dist.cell(row=2, column=1).fill = fill_titulo
        ws_dist.cell(row=2, column=2, value="Quantidade").font = fonte_cabecalho
        ws_dist.cell(row=2, column=2).fill = fill_titulo

        r_c = 3
        for st, count in metricas.get("distribuicao_status_cadastro", {}).items():
            ws_dist.cell(row=r_c, column=1, value=st).font = fonte_normal
            ws_dist.cell(row=r_c, column=2, value=count).font = fonte_bold
            ws_dist.cell(row=r_c, column=2).alignment = align_center
            r_c += 1

        ws_dist.cell(row=1, column=4, value="Status de Atendimento SAC (Processo 4)").font = fonte_subsecao
        ws_dist.cell(row=2, column=4, value="Status SAC").font = fonte_cabecalho
        ws_dist.cell(row=2, column=4).fill = fill_titulo
        ws_dist.cell(row=2, column=5, value="Quantidade").font = fonte_cabecalho
        ws_dist.cell(row=2, column=5).fill = fill_titulo

        r_s = 3
        for st, count in metricas.get("distribuicao_status_sac", {}).items():
            ws_dist.cell(row=r_s, column=4, value=st).font = fonte_normal
            ws_dist.cell(row=r_s, column=5, value=count).font = fonte_bold
            ws_dist.cell(row=r_s, column=5).alignment = align_center
            r_s += 1

        # Ajuste automático de largura de colunas
        for sheet in [ws_dash, ws_base, ws_dist]:
            for col in sheet.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    val_str = str(cell.value or "")
                    if "\n" in val_str:
                        val_str = max(val_str.split("\n"), key=len)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
                sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

        # Salva o arquivo versionado e o latest
        caminho_versionado = self.dir_saida / f"relatorio_gerencial_v{timestamp}.xlsx"
        caminho_latest = self.dir_saida / "relatorio_gerencial_latest.xlsx"

        wb.save(caminho_versionado)
        wb.save(caminho_latest)

        return caminho_versionado

    def gerar_markdown(self, metricas: Dict[str, Any], timestamp: str) -> Path:
        """Gera relatório executivo em formato Markdown."""
        kpi_cad = metricas["kpis_cadastro_processo3"]
        kpi_sac = metricas["kpis_sac_processo4"]
        kpi_efi = metricas["kpis_eficiencia_global"]

        linhas_md = [
            "# 📊 Relatório Gerencial de HyperAutomation",
            f"**Data de Geração:** {metricas.get('gerado_em', '')}  ",
            f"**Versão do Relatório:** `v{timestamp}`  ",
            "",
            "---",
            "",
            "## 📌 Sumário Executivo",
            f"- **Total de Clientes Processados:** {metricas['resumo_geral']['total_clientes_processados']}",
            f"- **Cadastros Concluídos no Portal:** {kpi_cad['cadastrados_com_sucesso']} ({kpi_cad['taxa_aprovacao_percentual']}%)",
            f"- **Atendimentos SAC Comunicados:** {kpi_sac['comunicados_com_sucesso']} ({kpi_sac['taxa_sucesso_comunicacao_percentual']}%)",
            f"- **Eficiência Global da Esteira:** **{kpi_efi['taxa_conclusao_ponta_a_ponta_percentual']}%** ({kpi_efi['eficiencia_esteira']})",
            "",
            "---",
            "",
            "## 📈 Detalhamento por Processo",
            "",
            "### Processo 3 — Cadastro no Portal Fake",
            "| Métrica | Valor |",
            "| :--- | :---: |",
            f"| Cadastrados com Sucesso | `{kpi_cad['cadastrados_com_sucesso']}` |",
            f"| Duplicados Identificados | `{kpi_cad['duplicados_identificados']}` |",
            f"| Erros de Validação | `{kpi_cad['erros_validacao']}` |",
            f"| Erros de Cadastro no Portal | `{kpi_cad['erros_cadastro_portal']}` |",
            f"| **Taxa de Aprovação** | **`{kpi_cad['taxa_aprovacao_percentual']}%`** |",
            "",
            "### Processo 4 — SAC e Atendimento",
            "| Métrica | Valor |",
            "| :--- | :---: |",
            f"| Total de Atendimentos SAC | `{kpi_sac['total_atendimentos_sac']}` |",
            f"| E-mails Enviados (Sucesso) | `{kpi_sac['comunicados_com_sucesso']}` |",
            f"| Pendentes de Contato / Fallback | `{kpi_sac['pendentes_contato_fallback']}` |",
            f"| **Taxa de Sucesso SAC** | **`{kpi_sac['taxa_sucesso_comunicacao_percentual']}%`** |",
            "",
            "---",
            "",
            "## 📊 Distribuição de Status",
            "",
            "### Status de Cadastro",
            "| Status | Quantidade |",
            "| :--- | :---: |",
        ]

        for st, count in metricas.get("distribuicao_status_cadastro", {}).items():
            linhas_md.append(f"| `{st}` | {count} |")

        linhas_md.extend([
            "",
            "### Status SAC",
            "| Status | Quantidade |",
            "| :--- | :---: |",
        ])

        for st, count in metricas.get("distribuicao_status_sac", {}).items():
            linhas_md.append(f"| `{st}` | {count} |")

        linhas_md.append("\n*Relatório gerado automaticamente pelo Processo 5 da plataforma HyperAutomation.*")

        conteudo = "\n".join(linhas_md)

        caminho_versionado = self.dir_saida / f"relatorio_gerencial_v{timestamp}.md"
        caminho_latest = self.dir_saida / "relatorio_gerencial_latest.md"

        caminho_versionado.write_text(conteudo, encoding="utf-8")
        caminho_latest.write_text(conteudo, encoding="utf-8")

        return caminho_versionado

    def gerar_json(self, dados_consolidados: Dict[str, Any], metricas: Dict[str, Any], timestamp: str) -> Path:
        """Gera arquivo JSON estruturado para consumo em APIs e dashboards."""
        payload = {
            "metadata": {
                "versao": f"v{timestamp}",
                "timestamp": timestamp,
                "gerado_em": metricas.get("gerado_em", "")
            },
            "metricas": metricas,
            "clientes": dados_consolidados.get("clientes", [])
        }

        caminho_versionado = self.dir_saida / f"relatorio_gerencial_v{timestamp}.json"
        caminho_latest = self.dir_saida / "relatorio_gerencial_latest.json"

        def json_serial(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            return str(obj)

        conteudo = json.dumps(payload, indent=2, ensure_ascii=False, default=json_serial)
        caminho_versionado.write_text(conteudo, encoding="utf-8")
        caminho_latest.write_text(conteudo, encoding="utf-8")

        return caminho_versionado
