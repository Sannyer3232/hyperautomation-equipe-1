"""
Módulo responsável pelo gerenciamento e organização física dos arquivos nas pastas do ERP.
"""
import os
import shutil
from pathlib import Path

class GestorArquivos:
    """
    Classe responsável por organizar e mover os arquivos recebidos
    nas pastas do ERP Simulado da Empresa Portal Fake.
    """
    def __init__(self, base_erp_path: str = None):
        if base_erp_path:
            self.base_dir = Path(base_erp_path).resolve()
        else:
            # Aponta para ERP_Portal_Fake na raiz do repositório
            self.base_dir = (Path(__file__).resolve().parents[3] / "ERP_Portal_Fake").resolve()
        
        self.dir_downloads = self.base_dir / "Downloads"
        self.dir_ok = self.base_dir / "Documentos_OK"
        self.dir_pendentes = self.base_dir / "Documentos_Pendentes"
        self.dir_encaminhados = self.base_dir / "Encaminhados"

    def garantir_estrutura_pastas(self):
        """Cria as pastas do ERP caso ainda não existam."""
        for pasta in [self.dir_downloads, self.dir_ok, self.dir_pendentes, self.dir_encaminhados]:
            pasta.mkdir(parents=True, exist_ok=True)
        print(f"[GESTOR ARQUIVOS] Estrutura de pastas garantida em: {self.base_dir}")

    def mover_para_status(self, nome_arquivo: str, status_ok: bool) -> Path:
        """
        Move um arquivo da pasta Downloads para Documentos_OK ou Documentos_Pendentes.
        """
        origem = self.dir_downloads / nome_arquivo
        destino_pasta = self.dir_ok if status_ok else self.dir_pendentes
        destino = destino_pasta / nome_arquivo

        if not origem.exists():
            # Tenta verificar se o arquivo está no diretório base ou no caminho original
            if Path(nome_arquivo).exists():
                origem = Path(nome_arquivo)

        if not origem.exists():
            raise FileNotFoundError(f"Arquivo não encontrado em Downloads: {origem}")

        shutil.move(str(origem), str(destino))
        status_nome = "Documentos_OK" if status_ok else "Documentos_Pendentes"
        print(f"[GESTOR ARQUIVOS] Arquivo '{Path(nome_arquivo).name}' movido para '{status_nome}'.")

        return destino

    def mover_para_encaminhados(self, nome_arquivo: str) -> Path:
        """
        Move o arquivo validado da pasta Documentos_OK para Encaminhados após o envio ao setor.
        """
        origem = self.dir_ok / nome_arquivo
        destino = self.dir_encaminhados / nome_arquivo

        if not origem.exists():
            if Path(nome_arquivo).exists():
                origem = Path(nome_arquivo)

        if not origem.exists():
            raise FileNotFoundError(f"Arquivo não encontrado em Documentos_OK: {origem}")

        shutil.move(str(origem), str(destino))
        print(f"[GESTOR ARQUIVOS] Arquivo '{Path(nome_arquivo).name}' movido para 'Encaminhados'.")

        return destino

def mover_para_pendentes(caminho_arquivo):
    gestor = GestorArquivos()
    return gestor.mover_para_status(Path(caminho_arquivo).name, status_ok=False)

def mover_para_ok(caminho_arquivo):
    gestor = GestorArquivos()
    return gestor.mover_para_status(Path(caminho_arquivo).name, status_ok=True)

def mover_para_encaminhados(caminho_arquivo):
    gestor = GestorArquivos()
    return gestor.mover_para_encaminhados(Path(caminho_arquivo).name)
