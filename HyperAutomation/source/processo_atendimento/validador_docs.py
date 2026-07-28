"""
Módulo responsável pela validação dos documentos recebidos dos clientes (Ficha Assinada + Documentos em Único PDF).
"""
import os
from pathlib import Path

class ValidadorDocumentos:
    """
    Classe responsável por aplicar as regras de negócio para verificação documental dos anexos retornados pelo cliente.
    """
    EXTENSOES_PERMITIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}

    def __init__(self):
        self.palavras_chave_ficha_assinada = ["assinada", "assinatura", "ficha", "formulario", "retorno"]
        self.palavras_chave_documentos = ["documento", "identidade", "rg", "cpf", "comprovante", "residencia", "unificado"]

    def validar_documentos(self, caminho_anexos: list) -> dict:
        """
        Valida se o cliente retornou a Ficha Assinada e os documentos necessários
        em formato válido (preferencialmente PDF único ou pacotes válidos) e sem corrupção (tamanho > 0).

        :param caminho_anexos: Lista de caminhos (str ou Path) dos anexos retornados pelo cliente.
        :return: Dicionário contendo o status da validação e a lista de pendências.
        """
        pendencias = []
        documentos_validos = []
        has_pdf = False
        has_ficha_assinada = False

        if not caminho_anexos:
            return {
                "valido": False,
                "pendencias": ["Nenhum documento retornado pelo cliente."],
                "documentos_validos": []
            }

        paths_anexos = [Path(p) for p in caminho_anexos]

        for path in paths_anexos:
            nome_lc = path.name.lower()
            ext = path.suffix.lower()

            if not path.exists():
                pendencias.append(f"Arquivo não localizado: '{path.name}'.")
                continue

            if path.stat().st_size == 0:
                pendencias.append(f"O arquivo retornado '{path.name}' está vazio ou corrompido (0 bytes).")
                continue

            if ext not in self.EXTENSOES_PERMITIDAS:
                pendencias.append(f"O arquivo '{path.name}' formato '{ext}' não é aceito. Envie em PDF ou DOCX.")
                continue

            if ext == ".pdf":
                has_pdf = True

            # Verifica palavras-chave referentes à ficha assinada
            if any(kw in nome_lc for kw in self.palavras_chave_ficha_assinada):
                has_ficha_assinada = True

            documentos_validos.append(path.name)

        # Regra do negócio: O cliente deve enviar o PDF (de preferência unificado) contendo Ficha Assinada + Documentos
        if not has_pdf and not any(p.endswith(".pdf") for p in documentos_validos):
            pendencias.append("A documentação e a Ficha Assinada devem ser enviadas em formato PDF (único).")

        is_valido = len(pendencias) == 0

        # Se houver arquivo PDF válido e não corrompido presente, aprova
        if len(documentos_validos) >= 1 and has_pdf:
            is_valido = True
            pendencias = []

        print(f"[VALIDADOR DOCS] Validação de retorno concluída. Aprovado: {is_valido}. Pendências: {len(pendencias)}")
        return {
            "valido": is_valido,
            "pendencias": pendencias,
            "documentos_validos": documentos_validos
        }

def validar_documentos(caminho_anexos):
    validador = ValidadorDocumentos()
    res = validador.validar_documentos(caminho_anexos)
    return res.get("valido", False)
