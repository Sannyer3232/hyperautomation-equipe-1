"""
Módulo de Validação de Regras de Negócio e Dados - Processo 3 (Cadastro)
"""
import re


class ValidadorCadastro:
    """
    Validador de dados cadastrais para o Processo 3.
    Verifica integridade de CPF, Nome, E-mail e campos obrigatórios antes do envio ao Portal Fake.
    """

    @staticmethod
    def sanitizar_cpf(cpf: str) -> str:
        """Extrai apenas dígitos e completa com zeros à esquerda até 11 dígitos."""
        if not cpf:
            return ""
        digitos = re.sub(r"\D", "", str(cpf).strip())
        if 0 < len(digitos) <= 11:
            return digitos.zfill(11)
        return digitos

    @staticmethod
    def validar_cpf(cpf: str) -> tuple[bool, str]:
        """Valida se o CPF possui 11 dígitos válidos."""
        if not cpf:
            return False, "CPF não informado."
        digitos = re.sub(r"\D", "", str(cpf).strip())
        if len(digitos) != 11:
            return False, f"CPF inválido (deve conter exatamente 11 dígitos, recebido {len(digitos)}: '{cpf}')"

        # CPFs com todos os dígitos iguais inválidos
        if len(set(digitos)) == 1:
            return False, f"CPF inválido (todos os dígitos são iguais: '{digitos}')"

        return True, "CPF válido"

    @staticmethod
    def validar_email(email: str) -> bool:
        """Verifica se o e-mail possui formato aceitável pelo portal."""
        if not email:
            return False
        padrao = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        return bool(re.match(padrao, str(email).strip()))

    @classmethod
    def validar_dados_cliente(cls, dados: dict) -> tuple[bool, list[str]]:
        """
        Valida todos os campos essenciais do cadastro.
        Retorna (True, []) se válido, ou (False, lista_de_erros) se inválido.
        """
        erros = []

        # 1. Validação de CPF
        cpf = dados.get("cpf", "")
        cpf_valido, motivo_cpf = cls.validar_cpf(cpf)
        if not cpf_valido:
            erros.append(motivo_cpf)

        # 2. Validação de Nome e Sobrenome
        nome = str(dados.get("nome", "")).strip()
        sobrenome = str(dados.get("sobrenome", "")).strip()
        nome_completo = str(dados.get("nome_completo", "")).strip()

        if not nome and not nome_completo:
            erros.append("Nome do cliente é obrigatório.")
        if not sobrenome and not nome_completo:
            erros.append("Sobrenome do cliente é obrigatório.")

        # 3. Validação de E-mail
        email = str(dados.get("email", "")).strip()
        if email and not cls.validar_email(email):
            erros.append(f"E-mail com formato inválido: '{email}'")

        if erros:
            return False, erros
        return True, []
