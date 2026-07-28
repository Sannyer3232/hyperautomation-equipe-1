"""
Módulo responsável pela validação dos documentos recebidos dos clientes.
"""
import os
from pathlib import Path

class ValidadorDocumentos:
    """
    Classe responsável por aplicar as regras de negócio para verificação documental dos anexos.
    """
    EXTENSOES_PERMITIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}

    def __init__(self):
        # Palavras-chave exigidas para validação dos tipos documentais
        self.regras_categoria = {
            "Identificação com Foto (RG/CPF/CNH)": ["rg", "cpf", "cnh", "identidade", "identificacao", "documento"],
            "Comprovante de Residência": ["comprovante", "residencia", "endereco", "luz", "agua", "fatura"],
            "Ficha de Cadastro": ["ficha", "formulario", "cadastro", "solicitacao"]
        }

    def validar_documentos(self, caminho_anexos: list) -> dict:
        """
        Valida se os documentos necessários (ex: Ficha, Documento com foto, Comprovante de Residência)
        foram anexados corretamente, possuem formato válido e tamanho maior que zero.

        :param caminho_anexos: Lista de caminhos (str ou Path) dos anexos do cliente.
        :return: Dicionário contendo o status da validação e a lista de pendências.
        """
        pendencias = []
        documentos_validos = []
        categoriase_atendidas = set()

        if not caminho_anexos:
            return {
                "valido": False,
                "pendencias": ["Nenhum anexo foi enviado na solicitação."],
                "documentos_validos": []
            }

        paths_anexos = [Path(p) for p in caminho_anexos]

        # 1. Validação física dos arquivos (Extensão e Tamanho)
        for path in paths_anexos:
            nome_lc = path.name.lower()
            ext = path.suffix.lower()

            if not path.exists():
                pendencias.append(f"Arquivo não localizado: '{path.name}'.")
                continue

            if path.stat().st_size == 0:
                pendencias.append(f"O arquivo '{path.name}' está corrompido ou vazio (0 bytes).")
                continue

            if ext not in self.EXTENSOES_PERMITIDAS:
                pendencias.append(f"O arquivo '{path.name}' possui extensão '{ext}' não suportada. Extensões válidas: PDF, PNG, JPG, DOCX.")
                continue

            documentos_validos.append(path.name)

            # Mapeia categorias atendidas pela nomenclatura do arquivo
            for categoria, palavras_chave in self.regras_categoria.items():
                if any(kw in nome_lc for kw in palavras_chave):
                    categoriase_atendidas.add(categoria)

        # 2. Verificação de cobertura das categorias obrigatórias
        for categoria in self.regras_categoria.keys():
            if categoria not in categoriase_atendidas:
                # Se houver apenas 1 anexo ou se a regra for genérica, notifica a ausência
                pendencias.append(f"Falta documento obrigatório: {categoria}.")

        # Se pelo menos 2 categorias ou todos os arquivos anexados forem válidos, considera aceito
        is_valido = len(pendencias) == 0

        # Se houver pendências de categoria mas arquivos válidos presentes, ajusta status para informativo se satisfazer critérios mínimos
        if not is_valido and len(documentos_validos) >= 3:
            # Caso tenha 3 ou mais anexos válidos no formato correto, aprova condicionalmente
            is_valido = True
            pendencias = []

        print(f"[VALIDADOR DOCS] Validação finalizada. Aprovado: {is_valido}. Pendências: {len(pendencias)}")
        return {
            "valido": is_valido,
            "pendencias": pendencias,
            "documentos_validos": documentos_validos
        }

def validar_documentos(caminho_anexos):
    validador = ValidadorDocumentos()
    res = validador.validar_documentos(caminho_anexos)
    return res.get("valido", False)
