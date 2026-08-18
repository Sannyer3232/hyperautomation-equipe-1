import re
import unicodedata
from pathlib import Path
from datetime import datetime
from pypdf import PdfReader


def _normalizar_espacos(texto: str) -> str:
    if not texto:
        return ""
    return re.sub(r"\s+", " ", str(texto)).strip()


class ExtratorPDF:
    """
    Responsável por abrir arquivos PDF (Fichas e Documentos),
    extrair o texto bruto utilizando 'pypdf' e realizar a extração estruturada
    de todos os dados cadastrais (CPF, Nome, Nascimento, Endereço, E-mail, Telefone, Status, Observações).
    """

    def __init__(self, caminho_pdf: Path):
        self.caminho_pdf = Path(caminho_pdf)

    def extrair_dados(self) -> dict:
        """
        Extrai todas as informações cadastrais e documentais a partir do arquivo PDF.
        Retorna um dicionário com os campos compatíveis com a Planilha Mestra.
        """
        if not self.caminho_pdf.exists():
            raise FileNotFoundError(f"Arquivo {self.caminho_pdf} não encontrado.")

        reader = PdfReader(self.caminho_pdf)
        paginas_texto = []
        for page in reader.pages:
            paginas_texto.append(page.extract_text() or "")

        texto_completo = "\n".join(paginas_texto)

        dados = {
            "nome": "",
            "sobrenome": "",
            "nome_completo": "",
            "cpf": "NÃO ENCONTRADO",
            "email": "",
            "telefone": "",
            "nascimento": "",
            "endereco": "",
            "status": "CONCLUIDO_P2",
            "protocolo": "",
            "observacoes": "Processado com sucesso via RPA",
        }

        # 1. Extração de Protocolo de Atendimento (se houver)
        m_prot = re.search(
            r"Protocolo(?:\s+de\s+Atendimento)?:\s*(#?PROT-[\w-]+)",
            texto_completo,
            re.IGNORECASE,
        )
        if m_prot:
            dados["protocolo"] = m_prot.group(1).strip()

        # 2. Formato 1: Extração linha a linha da Ficha de Cadastro Padrão
        for line in texto_completo.splitlines():
            line_clean = line.strip()
            if not line_clean:
                continue

            m_nome = re.match(r"^(?:1\.\s*)?Nome:\s*(.*)", line_clean, re.IGNORECASE)
            if m_nome and m_nome.group(1).strip() and not dados["nome"]:
                dados["nome"] = _normalizar_espacos(m_nome.group(1))

            m_sobrenome = re.match(
                r"^(?:2\.\s*)?Sobrenome:\s*(.*)", line_clean, re.IGNORECASE
            )
            if m_sobrenome and m_sobrenome.group(1).strip() and not dados["sobrenome"]:
                dados["sobrenome"] = _normalizar_espacos(m_sobrenome.group(1))

            m_cpf = re.match(r"^(?:3\.\s*)?CPF:\s*(.*)", line_clean, re.IGNORECASE)
            if m_cpf and m_cpf.group(1).strip() and dados["cpf"] == "NÃO ENCONTRADO":
                dados["cpf"] = _normalizar_espacos(m_cpf.group(1))

            m_email = re.match(r"^(?:4\.\s*)?E-?mail:\s*(.*)", line_clean, re.IGNORECASE)
            if m_email and m_email.group(1).strip() and not dados["email"]:
                val_email = _normalizar_espacos(m_email.group(1))
                if "@" in val_email:
                    dados["email"] = val_email

            m_tel = re.match(r"^(?:5\.\s*)?Telefone:\s*(.*)", line_clean, re.IGNORECASE)
            if m_tel and m_tel.group(1).strip() and not dados["telefone"]:
                dados["telefone"] = _normalizar_espacos(m_tel.group(1))

            m_nasc = re.match(
                r"^(?:6\.\s*)?Data\s+de\s+Nascimento:\s*(.*)", line_clean, re.IGNORECASE
            )
            if m_nasc and not dados["nascimento"]:
                val_nasc = _normalizar_espacos(m_nasc.group(1))
                if val_nasc:
                    dados["nascimento"] = val_nasc

            m_end = re.match(
                r"^(?:7\.\s*)?Endere[çc\ufffd]o:\s*(.*)", line_clean, re.IGNORECASE
            )
            if m_end and m_end.group(1).strip() and not dados["endereco"]:
                dados["endereco"] = _normalizar_espacos(m_end.group(1))

        # 3. Formato 2: Formato horizontal (Cliente: Nome Sobrenome | CPF: 12345678900 ...)
        m_horiz = re.search(
            r"Cliente:\s*([^|\n]+)\s*\|\s*CPF:\s*([\d.-]+)",
            texto_completo,
            re.IGNORECASE,
        )
        if m_horiz:
            if not dados["nome"]:
                nome_completo_raw = _normalizar_espacos(m_horiz.group(1))
                partes = nome_completo_raw.split(" ", 1)
                dados["nome"] = partes[0]
                if len(partes) > 1:
                    dados["sobrenome"] = partes[1]
            if dados["cpf"] == "NÃO ENCONTRADO":
                dados["cpf"] = m_horiz.group(2).strip()

        # 4. Fallback para Data de Nascimento em qualquer parte do texto
        if not dados["nascimento"]:
            m_nasc_regex = re.search(
                r"(?:Data\s+de\s+Nascimento|Nascimento|D\.N\.|Data\s+Nasc\.?):\s*([0-9]{2,4}[-/.][0-9]{2}[-/.][0-9]{2,4})",
                texto_completo,
                re.IGNORECASE,
            )
            if m_nasc_regex:
                dados["nascimento"] = m_nasc_regex.group(1).strip()

        # Normalização de Data de Nascimento para YYYY-MM-DD
        if dados["nascimento"]:
            raw_nasc = dados["nascimento"].strip()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"):
                try:
                    dt = datetime.strptime(raw_nasc, fmt)
                    dados["nascimento"] = dt.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    pass

        # 5. Fallback para CPF em qualquer parte do texto
        if dados["cpf"] == "NÃO ENCONTRADO" or not dados["cpf"]:
            m_cpfg = re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", texto_completo)
            if m_cpfg:
                dados["cpf"] = m_cpfg.group(0).strip()
            else:
                m_cpf11 = re.search(r"\b\d{11}\b", texto_completo)
                if m_cpf11:
                    dados["cpf"] = m_cpf11.group(0).strip()

        # Sanitização e formatação do CPF (11 dígitos numéricos com zeros à esquerda)
        if dados["cpf"] != "NÃO ENCONTRADO":
            digits_only = re.sub(r"\D", "", dados["cpf"])
            if 0 < len(digits_only) <= 11:
                dados["cpf"] = digits_only.zfill(11)

        # 6. Composição do Nome Completo
        if dados["nome"] and dados["sobrenome"]:
            if dados["sobrenome"].lower() not in dados["nome"].lower():
                dados["nome_completo"] = f"{dados['nome']} {dados['sobrenome']}".strip()
            else:
                dados["nome_completo"] = dados["nome"].strip()
        elif dados["nome"]:
            dados["nome_completo"] = dados["nome"].strip()
        elif dados["sobrenome"]:
            dados["nome_completo"] = dados["sobrenome"].strip()

        # 6. Fallbacks adicionais de E-mail (caso não tenha vindo na linha 4 da ficha)
        if not dados["email"]:
            emails_encontrados = re.findall(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", texto_completo
            )
            # Ignora emails de serviços/autenticação conhecidos
            emails_validos = [
                e
                for e in emails_encontrados
                if not any(
                    dom in e.lower()
                    for dom in [
                        "iti.gov.br",
                        "validar.iti",
                        "manausambiental",
                        "aguasdemanaus",
                    ]
                )
            ]
            if emails_validos:
                dados["email"] = emails_validos[0]

        # 7. Fallback para Telefone (caso não tenha sido capturado)
        if not dados["telefone"]:
            m_tel_gen = re.search(
                r"(?:\(?\d{2}\)?\s*)?(?:9\s*)?\d{4,5}[-\s]?\d{4}", texto_completo
            )
            if m_tel_gen:
                dados["telefone"] = _normalizar_espacos(m_tel_gen.group(0))

        # 8. Fallback para Endereço no Comprovante de Residência (Conta de Água / Luz)
        if not dados["endereco"]:
            m_end_fat = re.search(
                r"ENDERE[ÇC\ufffd]O DO IM[ÓO\ufffd]VEL[\s\S]*?(RUA[^\n]+MANAUS[^\n]*)",
                texto_completo,
                re.IGNORECASE,
            )
            if m_end_fat:
                dados["endereco"] = _normalizar_espacos(m_end_fat.group(1))

        # 9. Construção das Observações
        obs_lista = []
        if dados["protocolo"]:
            obs_lista.append(f"Protocolo: {dados['protocolo']}")
        if not obs_lista:
            obs_lista.append("Documentação validada e integrada via RPA")
        dados["observacoes"] = " - ".join(obs_lista)

        return dados
