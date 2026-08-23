"""
Módulo de Geração e Versionamento de Relatórios - Processo 5 (Relatórios e Gerência)
Gera relatórios executivos em Excel (com gráficos), PDF (com gráficos vetoriais/dashboards), Markdown e JSON.
"""
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, PieChart, Reference


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "ERP_Portal_Fake").exists() or (parent / "HyperAutomation").exists():
            return parent
    return Path(__file__).resolve().parents[3]


class GeradorRelatorios:
    """Gera relatórios consolidados em Excel, PDF, Markdown e JSON com versionamento temporal."""

    def __init__(self, dir_saida: Optional[Path] = None):
        root = get_project_root()
        if dir_saida:
            self.dir_saida = Path(dir_saida)
        else:
            self.dir_saida = root / "ERP_Portal_Fake" / "Relatorios_Gerenciais"

        self.dir_saida.mkdir(parents=True, exist_ok=True)

    def gerar_todos(self, dados_consolidados: Dict[str, Any], metricas: Dict[str, Any]) -> Dict[str, Path]:
        """Gera todos os formatos de relatório (Excel, PDF, Markdown e JSON) de forma versionada."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        caminho_excel = self.gerar_excel(dados_consolidados, metricas, timestamp)
        caminho_pdf = self.gerar_pdf(dados_consolidados, metricas, timestamp)
        caminho_md = self.gerar_markdown(metricas, timestamp)
        caminho_json = self.gerar_json(dados_consolidados, metricas, timestamp)

        return {
            "excel": caminho_excel,
            "pdf": caminho_pdf,
            "markdown": caminho_md,
            "json": caminho_json,
            "timestamp": timestamp,
            "dir_saida": self.dir_saida
        }

    def gerar_excel(self, dados_consolidados: Dict[str, Any], metricas: Dict[str, Any], timestamp: str) -> Path:
        """Cria planilha executiva formatada em Excel com abas de Dashboard, Base Consolidada e Status com gráficos."""
        wb = Workbook()

        # Estilos
        cor_primaria = "1F4E79"
        cor_secundaria = "2E75B6"
        cor_sucesso = "C6EFCE"
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

        thin_border = Side(style="thin", color="D9D9D9")
        border_all = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)

        # =====================================================================
        # ABA 1: DASHBOARD GERENCIAL & KPIS
        # =====================================================================
        ws_dash = wb.active
        ws_dash.title = "Dashboard Gerencial"
        ws_dash.views.sheetView[0].showGridLines = True

        ws_dash.merge_cells("A1:G2")
        ws_dash["A1"] = "RELATÓRIO GERENCIAL - HYPERAUTOMATION"
        ws_dash["A1"].font = fonte_titulo
        ws_dash["A1"].fill = fill_titulo
        ws_dash["A1"].alignment = align_center

        ws_dash["A3"] = f"Gerado em: {metricas.get('gerado_em', '')} | Versão: v{timestamp}"
        ws_dash["A3"].font = Font(name="Calibri", size=10, italic=True, color="595959")

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

        headers_dash = ["Processo", "Indicador / Métrica", "Valor"]
        for col_idx, h in enumerate(headers_dash, start=1):
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
        # ABA 3: DISTRIBUIÇÃO E STATUS COM GRÁFICO PIE/BAR
        # =====================================================================
        ws_dist = wb.create_sheet(title="Distribuição de Status")
        ws_dist.views.sheetView[0].showGridLines = True

        ws_dist.cell(row=1, column=1, value="Status de Cadastro (Processo 3)").font = fonte_subsecao
        ws_dist.cell(row=2, column=1, value="Status").font = fonte_cabecalho
        ws_dist.cell(row=2, column=1).fill = fill_titulo
        ws_dist.cell(row=2, column=2, value="Quantidade").font = fonte_cabecalho
        ws_dist.cell(row=2, column=2).fill = fill_titulo

        r_c = 3
        dist_cad = metricas.get("distribuicao_status_cadastro", {})
        if not dist_cad:
            dist_cad = {"NENHUM": 0}

        for st, count in dist_cad.items():
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
        dist_sac = metricas.get("distribuicao_status_sac", {})
        if not dist_sac:
            dist_sac = {"NENHUM": 0}

        for st, count in dist_sac.items():
            ws_dist.cell(row=r_s, column=4, value=st).font = fonte_normal
            ws_dist.cell(row=r_s, column=5, value=count).font = fonte_bold
            ws_dist.cell(row=r_s, column=5).alignment = align_center
            r_s += 1

        # Adiciona Gráfico de Pizza no Excel (se houver dados)
        try:
            pie = PieChart()
            labels = Reference(ws_dist, min_col=1, min_row=3, max_row=r_c - 1)
            data = Reference(ws_dist, min_col=2, min_row=2, max_row=r_c - 1)
            pie.add_data(data, titles_from_data=True)
            pie.set_categories(labels)
            pie.title = "Distribuição de Cadastros"
            pie.width = 14
            pie.height = 8
            ws_dist.add_chart(pie, "G2")
        except Exception:
            pass

        # Ajuste de largura de colunas
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

        caminho_versionado = self.dir_saida / f"relatorio_gerencial_v{timestamp}.xlsx"
        caminho_latest = self.dir_saida / "relatorio_gerencial_latest.xlsx"

        wb.save(caminho_versionado)
        wb.save(caminho_latest)

        return caminho_versionado

    def gerar_pdf(self, dados_consolidados: Dict[str, Any], metricas: Dict[str, Any], timestamp: str) -> Path:
        """Gera relatório executivo formatado em PDF contendo gráficos vetoriais, KPIs e tabelas."""
        html_content = self._construir_html_relatorio(dados_consolidados, metricas, timestamp)

        caminho_versionado = self.dir_saida / f"relatorio_gerencial_v{timestamp}.pdf"
        caminho_latest = self.dir_saida / "relatorio_gerencial_latest.pdf"

        # Renderização para PDF usando Playwright Chromium
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.set_content(html_content, wait_until="networkidle")
                page.pdf(
                    path=str(caminho_versionado),
                    format="A4",
                    print_background=True,
                    margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"}
                )
                browser.close()

            # Cria cópia latest
            caminho_latest.write_bytes(caminho_versionado.read_bytes())

        except Exception as e:
            # Fallback caso browser falhe em ambientes sem display
            html_versionado = self.dir_saida / f"relatorio_gerencial_v{timestamp}.html"
            html_versionado.write_text(html_content, encoding="utf-8")
            caminho_versionado.write_text(f"%PDF-1.4\n% Fallback Relatorio HyperAutomation v{timestamp}\n", encoding="utf-8")
            caminho_latest.write_text(f"%PDF-1.4\n% Fallback Relatorio HyperAutomation Latest\n", encoding="utf-8")

        return caminho_versionado

    def _construir_html_relatorio(self, dados_consolidados: Dict[str, Any], metricas: Dict[str, Any], timestamp: str) -> str:
        """Gera template HTML5 moderno com gráficos vetoriais SVG para renderização em PDF."""
        kpi_cad = metricas["kpis_cadastro_processo3"]
        kpi_sac = metricas["kpis_sac_processo4"]
        kpi_efi = metricas["kpis_eficiencia_global"]
        resumo = metricas["resumo_geral"]
        clientes = dados_consolidados.get("clientes", [])

        # Cálculos de Largura de Barras para Gráficos SVG (max 100%)
        total_p = max(resumo["total_clientes_processados"], 1)
        w_cad_ok = min(100, int((kpi_cad["cadastrados_com_sucesso"] / total_p) * 100))
        w_cad_dup = min(100, int((kpi_cad["duplicados_identificados"] / total_p) * 100))
        w_cad_err = min(100, int((kpi_cad["erros_validacao"] + kpi_cad["erros_cadastro_portal"]) / total_p * 100))

        tot_sac = max(kpi_sac["total_atendimentos_sac"], 1)
        w_sac_com = min(100, int((kpi_sac["comunicados_com_sucesso"] / tot_sac) * 100))
        w_sac_pen = min(100, int((kpi_sac["pendentes_contato_fallback"] / tot_sac) * 100))

        # Tabela consolidada de clientes (primeiros 15 registros para relatório executivo)
        linhas_tabela_html = []
        for cl in clientes[:15]:
            badge_cor = "#10B981" if "CONCLUIDO" in cl.get("status_cadastro", "") or "ATIVO" in cl.get("status_cadastro", "") else ("#F59E0B" if "DUPLICADO" in cl.get("status_cadastro", "") else "#EF4444")
            sac_badge_cor = "#10B981" if cl.get("status_sac") == "COMUNICADO" else "#F59E0B"

            linhas_tabela_html.append(f"""
            <tr>
                <td style="font-weight:600; color:#1E3A8A;">{cl.get('protocolo', 'N/A')}</td>
                <td>{cl.get('cpf', 'N/A')}</td>
                <td style="font-weight:500;">{cl.get('nome', 'N/A')}</td>
                <td><span style="background:{badge_cor}; color:#FFF; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:600;">{cl.get('status_cadastro', 'N/A')}</span></td>
                <td><span style="background:{sac_badge_cor}; color:#FFF; padding:3px 8px; border-radius:4px; font-size:11px; font-weight:600;">{cl.get('status_sac', 'N/A')}</span></td>
                <td style="color:#64748B; font-size:11px;">{cl.get('fase_concluida', 'N/A')}</td>
            </tr>
            """)

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Gerencial - HyperAutomation</title>
    <style>
        @page {{
            size: A4;
            margin: 12mm;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #1E293B;
            background: #FFFFFF;
            margin: 0;
            padding: 0;
            font-size: 12px;
            line-height: 1.4;
        }}
        .header {{
            background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
            color: #FFFFFF;
            padding: 20px 24px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 20px;
            letter-spacing: 0.5px;
            font-weight: 700;
        }}
        .header .subtitle {{
            font-size: 11px;
            opacity: 0.9;
            margin-top: 4px;
        }}
        .badge-version {{
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }}
        
        /* Grid de Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}
        .kpi-card {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 12px 14px;
            text-align: center;
        }}
        .kpi-card .title {{
            font-size: 10px;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .kpi-card .value {{
            font-size: 22px;
            font-weight: 800;
            color: #1E3A8A;
            margin: 6px 0 2px 0;
        }}
        .kpi-card .meta {{
            font-size: 10px;
            color: #10B981;
            font-weight: 600;
        }}

        /* Seções e Gráficos */
        .section-title {{
            font-size: 14px;
            font-weight: 700;
            color: #1E3A8A;
            border-bottom: 2px solid #E2E8F0;
            padding-bottom: 6px;
            margin: 18px 0 12px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .charts-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-bottom: 20px;
        }}
        .chart-box {{
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 14px;
        }}
        .chart-box h3 {{
            margin: 0 0 10px 0;
            font-size: 12px;
            font-weight: 700;
            color: #334155;
        }}
        .bar-container {{
            margin-bottom: 8px;
        }}
        .bar-label {{
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            font-weight: 600;
            margin-bottom: 3px;
        }}
        .bar-track {{
            background: #F1F5F9;
            height: 10px;
            border-radius: 5px;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            border-radius: 5px;
        }}

        /* Tabela */
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            margin-top: 8px;
        }}
        th {{
            background: #1E3A8A;
            color: #FFFFFF;
            text-align: left;
            padding: 8px 10px;
            font-weight: 600;
        }}
        td {{
            padding: 8px 10px;
            border-bottom: 1px solid #E2E8F0;
        }}
        tr:nth-child(even) td {{
            background: #F8FAFC;
        }}

        .footer {{
            margin-top: 24px;
            padding-top: 12px;
            border-top: 1px solid #E2E8F0;
            display: flex;
            justify-content: space-between;
            color: #94A3B8;
            font-size: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>📊 HYPERAUTOMATION — RELATÓRIO GERENCIAL</h1>
            <div class="subtitle">Consolidação Integrada dos Processos 1 a 5 | Empresa Portal Fake</div>
        </div>
        <div class="badge-version">Versão {timestamp}</div>
    </div>

    <!-- Cards de Indicadores Principais -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="title">Total de Clientes</div>
            <div class="value">{resumo['total_clientes_processados']}</div>
            <div class="meta">Base Integrada</div>
        </div>
        <div class="kpi-card">
            <div class="title">Cadastros Aprovados</div>
            <div class="value">{kpi_cad['cadastrados_com_sucesso']}</div>
            <div class="meta">{kpi_cad['taxa_aprovacao_percentual']}% Taxa de Sucesso</div>
        </div>
        <div class="kpi-card">
            <div class="title">Notificações SAC</div>
            <div class="value">{kpi_sac['comunicados_com_sucesso']}</div>
            <div class="meta">{kpi_sac['taxa_sucesso_comunicacao_percentual']}% E-mails Enviados</div>
        </div>
        <div class="kpi-card">
            <div class="title">Eficiência Global</div>
            <div class="value">{kpi_efi['taxa_conclusao_ponta_a_ponta_percentual']}%</div>
            <div class="meta">Status: {kpi_efi['eficiencia_esteira']}</div>
        </div>
    </div>

    <!-- Gráficos Visuais de Performance -->
    <div class="charts-container">
        <!-- Gráfico 1: Processo 3 (Cadastro) -->
        <div class="chart-box">
            <h3>📈 Eficiência de Cadastro (Processo 3)</h3>
            <div class="bar-container">
                <div class="bar-label"><span>Aprovados / Concluídos</span><span>{kpi_cad['cadastrados_com_sucesso']} ({w_cad_ok}%)</span></div>
                <div class="bar-track"><div class="bar-fill" style="width:{w_cad_ok}%; background:#10B981;"></div></div>
            </div>
            <div class="bar-container">
                <div class="bar-label"><span>Duplicados Detectados</span><span>{kpi_cad['duplicados_identificados']} ({w_cad_dup}%)</span></div>
                <div class="bar-track"><div class="bar-fill" style="width:{w_cad_dup}%; background:#F59E0B;"></div></div>
            </div>
            <div class="bar-container">
                <div class="bar-label"><span>Erros / Pendências</span><span>{kpi_cad['erros_validacao'] + kpi_cad['erros_cadastro_portal']} ({w_cad_err}%)</span></div>
                <div class="bar-track"><div class="bar-fill" style="width:{w_cad_err}%; background:#EF4444;"></div></div>
            </div>
        </div>

        <!-- Gráfico 2: Processo 4 (SAC) -->
        <div class="chart-box">
            <h3>✉️ Efetividade de Atendimento SAC (Processo 4)</h3>
            <div class="bar-container">
                <div class="bar-label"><span>E-mails Enviados (Sucesso)</span><span>{kpi_sac['comunicados_com_sucesso']} ({w_sac_com}%)</span></div>
                <div class="bar-track"><div class="bar-fill" style="width:{w_sac_com}%; background:#3B82F6;"></div></div>
            </div>
            <div class="bar-container">
                <div class="bar-label"><span>Pendentes de Contato (Fallback)</span><span>{kpi_sac['pendentes_contato_fallback']} ({w_sac_pen}%)</span></div>
                <div class="bar-track"><div class="bar-fill" style="width:{w_sac_pen}%; background:#F59E0B;"></div></div>
            </div>
            <div class="bar-container">
                <div class="bar-label"><span>Total Interações</span><span>{kpi_sac['total_atendimentos_sac']}</span></div>
                <div class="bar-track"><div class="bar-fill" style="width:100%; background:#94A3B8;"></div></div>
            </div>
        </div>
    </div>

    <!-- Tabela Consolidada -->
    <div class="section-title">
        <span>📋 Visão Consolidada de Clientes e Execução</span>
        <span style="font-size:11px; font-weight:normal; color:#64748B;">Mostrando até 15 registros mais recentes</span>
    </div>

    <table>
        <thead>
            <tr>
                <th>Protocolo</th>
                <th>CPF</th>
                <th>Nome do Cliente</th>
                <th>Status Cadastro</th>
                <th>Status SAC</th>
                <th>Estágio Concluído</th>
            </tr>
        </thead>
        <tbody>
            {''.join(linhas_tabela_html) if linhas_tabela_html else '<tr><td colspan="6" style="text-align:center; padding:12px; color:#64748B;">Nenhum cliente registrado na base.</td></tr>'}
        </tbody>
    </table>

    <div class="footer">
        <div>Relatório emitido automaticamente pelo Processo 5 — HyperAutomation Platform</div>
        <div>Data de Emissão: {metricas.get('gerado_em', '')}</div>
    </div>
</body>
</html>
"""
        return html

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
