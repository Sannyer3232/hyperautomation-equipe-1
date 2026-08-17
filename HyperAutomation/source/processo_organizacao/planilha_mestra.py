import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from pathlib import Path
from datetime import datetime, date
import re
import copy


class GerenciadorPlanilha:
    """
    Gerenciador da Planilha Mestra (Planilha_Mestra.xlsx).
    Utiliza OpenPyXL para manipular e gravar os dados consolidados,
    preservando 100% da formatação visual, bordas, cores, larguras de coluna e formatos numéricos.
    """

    COLUNAS_PADRAO = [
        "CPF",
        "Nome",
        "Data de Nascimento",
        "Endereço",
        "E-mail",
        "Telefone",
        "Status",
        "Data de Processamento",
        "Observações",
    ]

    LARGURAS_COLUNA = {
        "A": 18.0,
        "B": 30.0,
        "C": 20.0,
        "D": 40.0,
        "E": 35.0,
        "F": 18.0,
        "G": 18.0,
        "H": 22.0,
        "I": 40.0,
    }

    def __init__(self, caminho_planilha: Path):
        self.caminho_planilha = Path(caminho_planilha)

    def _obter_mapeamento_colunas(self, ws) -> dict:
        """Mapeia dinamicamente o índice (1-based) de cada coluna a partir do cabeçalho na linha 1."""
        header_map = {}
        for col in range(1, ws.max_column + 1):
            val = str(ws.cell(1, col).value or "").strip()
            norm = (
                val.lower()
                .replace("ç", "c")
                .replace("ã", "a")
                .replace("é", "e")
                .replace("ó", "o")
                .replace("\ufffd", "")
            )
            if "cpf" in norm:
                header_map["cpf"] = col
            elif "nome" in norm:
                header_map["nome"] = col
            elif "nasc" in norm:
                header_map["nascimento"] = col
            elif "ender" in norm:
                header_map["endereco"] = col
            elif "mail" in norm:
                header_map["email"] = col
            elif "tel" in norm:
                header_map["telefone"] = col
            elif "stat" in norm:
                header_map["status"] = col
            elif "proc" in norm or "data de proc" in norm:
                header_map["data_processamento"] = col
            elif "obs" in norm:
                header_map["observacoes"] = col

        # Fallback posicional padrão caso não encontre pelo nome
        defaults = {
            "cpf": 1,
            "nome": 2,
            "nascimento": 3,
            "endereco": 4,
            "email": 5,
            "telefone": 6,
            "status": 7,
            "data_processamento": 8,
            "observacoes": 9,
        }
        for k, v in defaults.items():
            if k not in header_map:
                header_map[k] = v

        return header_map

    def inicializar_planilha(self):
        """
        Cria a Planilha Mestra com estilização profissional caso ela ainda não exista ou esteja vazia.
        Se já existir, garante que os cabeçalhos estejam corretos e sem caracteres corrompidos.
        """
        self.caminho_planilha.parent.mkdir(parents=True, exist_ok=True)

        if not self.caminho_planilha.exists() or self.caminho_planilha.stat().st_size == 0:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Planilha_Mestra"

            # Estilos dos cabeçalhos
            header_fill = PatternFill(
                start_color="001F4E78", end_color="001F4E78", fill_type="solid"
            )
            header_font = Font(name="Calibri", size=11, bold=True, color="00FFFFFF")
            header_align = Alignment(horizontal="center", vertical="center")
            header_border = Border(
                bottom=Side(style="thin", color="00D9E1F2")
            )

            for col_idx, col_name in enumerate(self.COLUNAS_PADRAO, start=1):
                cell = ws.cell(row=1, column=col_idx, value=col_name)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_align
                cell.border = header_border

            # Configura larguras de coluna
            for col_letter, width in self.LARGURAS_COLUNA.items():
                ws.column_dimensions[col_letter].width = width

            # Configura formatos padrão para as linhas iniciais
            for r in range(2, 100):
                ws.cell(row=r, column=3).number_format = "DD/MM/YYYY"
                ws.cell(row=r, column=8).number_format = "DD/MM/YYYY HH:MM"

            wb.save(self.caminho_planilha)
            print(f"[PLANILHA MESTRA] Planilha criada com sucesso em: {self.caminho_planilha}")
        else:
            # Garante que os nomes de cabeçalho na linha 1 estejam limpos
            try:
                wb = openpyxl.load_workbook(self.caminho_planilha)
                ws = wb.active
                modificado = False
                for col_idx, col_name in enumerate(self.COLUNAS_PADRAO, start=1):
                    cell = ws.cell(row=1, column=col_idx)
                    if cell.value != col_name and (cell.value is None or "\ufffd" in str(cell.value) or str(cell.value).strip() == ""):
                        cell.value = col_name
                        modificado = True
                if modificado:
                    wb.save(self.caminho_planilha)
            except Exception as e:
                print(f"[PLANILHA MESTRA] Aviso ao verificar cabeçalhos: {e}")

    def adicionar_registro(self, dados: dict) -> bool:
        """
        Adiciona um novo registro consolidado na Planilha Mestra preservando 100% da formatação.
        Evita duplicidades checando o CPF sanitizado.
        Retorna True se inseriu, False se o CPF já existia.
        """
        self.inicializar_planilha()

        wb = openpyxl.load_workbook(self.caminho_planilha)
        ws = wb.active

        header_map = self._obter_mapeamento_colunas(ws)
        col_cpf = header_map.get("cpf", 1)

        # Sanitização rigorosa do CPF
        cpf_bruto = str(dados.get("cpf", "")).strip()
        cpf_digits = re.sub(r"\D", "", cpf_bruto)
        if 0 < len(cpf_digits) <= 11:
            cpf_atual = cpf_digits.zfill(11)
        else:
            cpf_atual = cpf_bruto

        # Validação de duplicidade na coluna de CPF existente
        for r in range(2, ws.max_row + 1):
            val_existente = ws.cell(r, col_cpf).value
            if val_existente is not None:
                val_limpo = re.sub(r"\D", "", str(val_existente)).zfill(11)
                if val_limpo == cpf_atual and cpf_atual not in ("", "NÃO ENCONTRADO"):
                    print(f"[PLANILHA MESTRA] Aviso: CPF {cpf_atual} já cadastrado na linha {r}. Ignorando duplicidade.")
                    wb.close()
                    return False

        # Localiza a primeira linha vazia (onde CPF e Nome estão vazios)
        col_nome = header_map.get("nome", 2)
        target_row = None
        for r in range(2, ws.max_row + 1):
            c_cpf = ws.cell(r, col_cpf).value
            c_nome = ws.cell(r, col_nome).value
            if (c_cpf is None or str(c_cpf).strip() == "") and (c_nome is None or str(c_nome).strip() == ""):
                target_row = r
                break

        if target_row is None:
            target_row = ws.max_row + 1

        # Tratamento do Nome
        nome_completo = dados.get("nome_completo")
        if not nome_completo:
            n = dados.get("nome", "") or ""
            s = dados.get("sobrenome", "") or ""
            nome_completo = f"{n} {s}".strip() if s else n.strip()

        # Tratamento da Data de Nascimento
        nascimento_val = None
        raw_nasc = str(dados.get("nascimento", "")).strip()
        if raw_nasc:
            formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
            for fmt in formatos:
                try:
                    dt = datetime.strptime(raw_nasc, fmt)
                    nascimento_val = dt.date()
                    break
                except ValueError:
                    continue
            if nascimento_val is None:
                nascimento_val = raw_nasc

        # Tratamento da Data de Processamento
        data_proc_val = datetime.now()

        # Gravação de cada campo na linha destino
        if "cpf" in header_map:
            cell = ws.cell(row=target_row, column=header_map["cpf"])
            cell.value = str(cpf_atual)
            cell.number_format = "@"  # Preserva como texto com zeros à esquerda

        if "nome" in header_map:
            ws.cell(row=target_row, column=header_map["nome"], value=nome_completo)

        if "nascimento" in header_map and nascimento_val is not None:
            cell = ws.cell(row=target_row, column=header_map["nascimento"])
            cell.value = nascimento_val
            cell.number_format = "DD/MM/YYYY"

        if "endereco" in header_map:
            ws.cell(row=target_row, column=header_map["endereco"], value=dados.get("endereco", ""))

        if "email" in header_map:
            ws.cell(row=target_row, column=header_map["email"], value=dados.get("email", ""))

        if "telefone" in header_map:
            ws.cell(row=target_row, column=header_map["telefone"], value=dados.get("telefone", ""))

        if "status" in header_map:
            ws.cell(row=target_row, column=header_map["status"], value=dados.get("status", "CONCLUIDO_P2"))

        if "data_processamento" in header_map:
            cell = ws.cell(row=target_row, column=header_map["data_processamento"])
            cell.value = data_proc_val
            cell.number_format = "DD/MM/YYYY HH:MM"

        if "observacoes" in header_map:
            ws.cell(row=target_row, column=header_map["observacoes"], value=dados.get("observacoes", ""))

        wb.save(self.caminho_planilha)
        print(f"[PLANILHA MESTRA] Registro de '{nome_completo}' (CPF: {cpf_atual}) adicionado na linha {target_row} com sucesso.")
        return True

    def ler_registros(self, status_filtro=None) -> list:
        """
        Lê todos os registros preenchidos da Planilha Mestra.
        :param status_filtro: Opcional. String ou lista de strings de status para filtrar (ex: 'CONCLUIDO_P2').
        :return: Lista de dicionários contendo os dados estruturados de cada linha da planilha.
        """
        if not self.caminho_planilha.exists():
            return []

        wb = openpyxl.load_workbook(self.caminho_planilha, data_only=True)
        ws = wb.active
        header_map = self._obter_mapeamento_colunas(ws)

        col_cpf = header_map.get("cpf", 1)
        col_nome = header_map.get("nome", 2)
        col_nasc = header_map.get("nascimento", 3)
        col_end = header_map.get("endereco", 4)
        col_email = header_map.get("email", 5)
        col_tel = header_map.get("telefone", 6)
        col_status = header_map.get("status", 7)
        col_dt_proc = header_map.get("data_processamento", 8)
        col_obs = header_map.get("observacoes", 9)

        registros = []
        for r in range(2, ws.max_row + 1):
            cpf_val = ws.cell(r, col_cpf).value
            nome_val = ws.cell(r, col_nome).value

            # Ignora linhas completamente em branco
            if (cpf_val is None or str(cpf_val).strip() == "") and (nome_val is None or str(nome_val).strip() == ""):
                continue

            # Sanitização do CPF
            cpf_str = str(cpf_val or "").strip()
            cpf_digits = re.sub(r"\D", "", cpf_str)
            if 0 < len(cpf_digits) <= 11:
                cpf_limpo = cpf_digits.zfill(11)
            else:
                cpf_limpo = cpf_str

            st_val = str(ws.cell(r, col_status).value or "").strip()

            if status_filtro:
                if isinstance(status_filtro, (list, tuple, set)):
                    filtros = [str(f).upper() for f in status_filtro]
                    if st_val.upper() not in filtros:
                        continue
                else:
                    if st_val.upper() != str(status_filtro).upper():
                        continue

            nasc_val = ws.cell(r, col_nasc).value
            if isinstance(nasc_val, (datetime, date)):
                nasc_str = nasc_val.strftime("%Y-%m-%d")
            else:
                nasc_str = str(nasc_val or "").strip()

            dt_proc_val = ws.cell(r, col_dt_proc).value

            item = {
                "linha": r,
                "cpf": cpf_limpo,
                "nome_completo": str(nome_val or "").strip(),
                "nascimento": nasc_str,
                "endereco": str(ws.cell(r, col_end).value or "").strip(),
                "email": str(ws.cell(r, col_email).value or "").strip(),
                "telefone": str(ws.cell(r, col_tel).value or "").strip(),
                "status": st_val,
                "data_processamento": dt_proc_val,
                "observacoes": str(ws.cell(r, col_obs).value or "").strip(),
            }
            registros.append(item)

        wb.close()
        return registros

    def atualizar_status_registro(self, cpf: str = None, linha: int = None, novo_status: str = "CONCLUIDO_P3", observacao: str = None) -> bool:
        """
        Atualiza o status, data de processamento e observações de um registro existente na Planilha Mestra.
        Localiza a linha diretamente pelo número ou pelo CPF sanitizado.
        """
        if not self.caminho_planilha.exists():
            return False

        wb = openpyxl.load_workbook(self.caminho_planilha)
        ws = wb.active
        header_map = self._obter_mapeamento_colunas(ws)

        col_cpf = header_map.get("cpf", 1)
        col_status = header_map.get("status", 7)
        col_dt_proc = header_map.get("data_processamento", 8)
        col_obs = header_map.get("observacoes", 9)

        target_row = None
        if linha and 2 <= linha <= ws.max_row:
            target_row = linha
        elif cpf:
            cpf_digits = re.sub(r"\D", "", str(cpf)).zfill(11)
            for r in range(2, ws.max_row + 1):
                val_cpf = ws.cell(r, col_cpf).value
                if val_cpf is not None:
                    c_limpo = re.sub(r"\D", "", str(val_cpf)).zfill(11)
                    if c_limpo == cpf_digits:
                        target_row = r
                        break

        if target_row is None:
            wb.close()
            return False

        if col_status:
            ws.cell(row=target_row, column=col_status, value=novo_status)

        if col_dt_proc:
            cell_dt = ws.cell(row=target_row, column=col_dt_proc)
            cell_dt.value = datetime.now()
            cell_dt.number_format = "DD/MM/YYYY HH:MM"

        if observacao and col_obs:
            cell_obs = ws.cell(row=target_row, column=col_obs)
            obs_atual = str(cell_obs.value or "").strip()
            if obs_atual and obs_atual != "None" and obs_atual != "":
                cell_obs.value = f"{obs_atual} | {observacao}"
            else:
                cell_obs.value = observacao

        wb.save(self.caminho_planilha)
        wb.close()
        print(f"[PLANILHA MESTRA] Linha {target_row} atualizada para status '{novo_status}'.")
        return True

    def obter_registro_por_cpf(self, cpf: str) -> dict:
        """Busca e retorna o registro correspondente ao CPF ou None caso não encontre."""
        registros = self.ler_registros()
        cpf_digits = re.sub(r"\D", "", str(cpf)).zfill(11)
        for reg in registros:
            if re.sub(r"\D", "", str(reg.get("cpf", ""))).zfill(11) == cpf_digits:
                return reg
        return None
