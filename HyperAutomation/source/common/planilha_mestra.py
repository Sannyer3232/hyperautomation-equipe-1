from pathlib import Path
from openpyxl import Workbook, load_workbook


class PlanilhaMestra:
    """
    Classe utilitária para manipulação e registro de clientes na Planilha Mestra (Excel).
    """

    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)

        if self.caminho.exists():
            self.wb = load_workbook(self.caminho)
            self.ws = self.wb.active
        else:
            self.wb = Workbook()
            self.ws = self.wb.active
            self.ws.title = "Planilha_Mestra"

            self.ws.append([
                "Protocolo",
                "Nome",
                "Sobrenome",
                "CPF",
                "Email",
                "Telefone",
                "Endereço",
                "Status"
            ])

            self.wb.save(self.caminho)

    def adicionar_cliente(self, dados: dict):
        """
        Adiciona um novo registro de cliente na planilha.
        """
        if not hasattr(self, "ws") or self.ws is None:
            self.wb = load_workbook(self.caminho)
            self.ws = self.wb.active

        self.ws.append([
            dados.get("protocolo", ""),
            dados.get("nome", ""),
            dados.get("sobrenome", ""),
            dados.get("cpf", ""),
            dados.get("email", ""),
            dados.get("telefone", ""),
            dados.get("endereco", ""),
            dados.get("status", "")
        ])

        self.wb.save(self.caminho)
        print(f"[PLANILHA MESTRA] Cliente {dados.get('nome', '')} {dados.get('sobrenome', '')} salvo na planilha com sucesso.")
