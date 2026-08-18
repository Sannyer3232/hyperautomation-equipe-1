"""
Módulo de Leitura e Preparação de Dados da Planilha Mestra - Processo 3 (Cadastro)
"""
import re
from pathlib import Path
from datetime import datetime, date
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from processo_organizacao.planilha_mestra import GerenciadorPlanilha
from .validador_cadastro import ValidadorCadastro


class LeitorPlanilhaCadastro:
    """
    Responsável por ler e normalizar os registros da Planilha_Mestra.xlsx
    que foram processados pelo Processo 2 e aguardam cadastro no Portal Fake.
    """

    def __init__(self, caminho_planilha: Path = None):
        if caminho_planilha:
            self.caminho_planilha = Path(caminho_planilha).resolve()
        else:
            # Caminho padrão: ERP_Portal_Fake/Sistema_Integrador_Portal_Fake/Planilha_Mestra.xlsx
            raiz = Path(__file__).resolve().parents[3]
            self.caminho_planilha = (
                raiz / "ERP_Portal_Fake" / "Sistema_Integrador_Portal_Fake" / "Planilha_Mestra.xlsx"
            ).resolve()

        self.gerenciador = GerenciadorPlanilha(self.caminho_planilha)

    def obter_clientes_pendentes(self, status_filtro=None) -> list[dict]:
        """
        Lê os clientes na Planilha Mestra que aguardam cadastro.
        Por padrão, filtra registros com status 'CONCLUIDO_P2', 'PENDENTE_CADASTRO' ou 'PENDENTE'.
        Retorna uma lista de dicionários com todos os campos preparados para o formulário do portal.
        """
        if status_filtro is None:
            status_filtro = ["CONCLUIDO_P2", "PENDENTE_CADASTRO", "PENDENTE"]

        self.gerenciador.inicializar_planilha()
        registros_brutos = self.gerenciador.ler_registros(status_filtro=status_filtro)

        clientes_processados = []
        for reg in registros_brutos:
            cliente_preparado = self._preparar_dados_cliente(reg)
            clientes_processados.append(cliente_preparado)

        return clientes_processados

    def obter_todos_clientes(self) -> list[dict]:
        """Lê todos os clientes registrados na Planilha Mestra, independentemente de status."""
        self.gerenciador.inicializar_planilha()
        registros_brutos = self.gerenciador.ler_registros()
        return [self._preparar_dados_cliente(r) for r in registros_brutos]

    def obter_cliente_por_cpf(self, cpf: str) -> dict:
        """Busca um cliente específico na Planilha Mestra pelo CPF e retorna normalizado para o portal."""
        self.gerenciador.inicializar_planilha()
        reg = self.gerenciador.obter_registro_por_cpf(cpf)
        if reg:
            return self._preparar_dados_cliente(reg)
        return None

    def obter_cliente_por_linha(self, linha: int) -> dict:
        """Busca um cliente específico na Planilha Mestra pelo número da linha do Excel."""
        self.gerenciador.inicializar_planilha()
        todos = self.gerenciador.ler_registros()
        for reg in todos:
            if reg.get("linha") == linha:
                return self._preparar_dados_cliente(reg)
        return None

    def _preparar_dados_cliente(self, reg: dict) -> dict:
        """
        Normaliza os campos de um registro bruto para o formato esperado pelo Portal Fake.
        Trata separação de nome/sobrenome, formatação de CPF e fallbacks de e-mail e nascimento.
        """
        nome_completo = str(reg.get("nome_completo", "")).strip()
        partes_nome = nome_completo.split(" ", 1)
        nome = partes_nome[0] if partes_nome else "Cliente"
        sobrenome = partes_nome[1] if len(partes_nome) > 1 else "Solicitante"

        cpf_limpo = ValidadorCadastro.sanitizar_cpf(reg.get("cpf", ""))

        # Fallback de e-mail caso não conste na planilha
        email = str(reg.get("email", "")).strip()
        if not email or "@" not in email:
            nome_slug = re.sub(r"\W+", "", nome.lower())
            sobrenome_slug = re.sub(r"\W+", "", sobrenome.lower().replace(" ", ""))
            email = f"{nome_slug}.{sobrenome_slug}@email.com"

        # Fallback de telefone
        telefone = str(reg.get("telefone", "")).strip()
        if not telefone:
            telefone = "(92) 99999-0000"

        # Fallback de data de nascimento (o portal exige YYYY-MM-DD no input type="date")
        nasc_raw = reg.get("nascimento", "")
        nascimento_formatado = "1995-01-01"
        if nasc_raw:
            if isinstance(nasc_raw, (datetime, date)):
                nascimento_formatado = nasc_raw.strftime("%Y-%m-%d")
            else:
                str_nasc = str(nasc_raw).strip()
                # Tenta parsear formatos comuns
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                    try:
                        dt = datetime.strptime(str_nasc, fmt)
                        nascimento_formatado = dt.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue

        # Endereço
        endereco = str(reg.get("endereco", "")).strip()
        if not endereco:
            endereco = "Manaus/AM"

        # Observações
        obs = str(reg.get("observacoes", "")).strip()

        return {
            "linha": reg.get("linha"),
            "nome": nome,
            "sobrenome": sobrenome,
            "nome_completo": nome_completo or f"{nome} {sobrenome}",
            "cpf": cpf_limpo,
            "email": email,
            "telefone": telefone,
            "nascimento": nascimento_formatado,
            "endereco": endereco,
            "status_portal": "ATIVO",
            "status_planilha_origem": reg.get("status", ""),
            "observacoes": obs,
        }
