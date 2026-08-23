"""
Módulo de Integração Web e Automação no Portal Fake - Processo 3 (Cadastro)
"""
import re
from pathlib import Path
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

PATH_ROOT = Path(__file__).resolve().parents[2]
INDEX_HTML = PATH_ROOT / "resources" / "portal_fake" / "index.html"
SCREENSHOTS_DIR = PATH_ROOT / "resources" / "screenshots"


class CadastradorPortalFake:
    """
    Controlador de automação RPA via Playwright para o ERP Portal Fake.
    Executa consultas de duplicidade, cadastro de novos clientes, atualização de status e captura de evidências.
    """

    def __init__(self, page: Page = None, portal_url: str = None):
        self.page = page
        self.portal_url = portal_url or f"file://{INDEX_HTML.resolve()}"
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    def navegar_ao_portal(self, page: Page = None):
        """Abre o Portal Fake ERP e aguarda os componentes principais carregarem."""
        target_page = page or self.page
        if not target_page:
            raise ValueError("Uma página válida do Playwright deve ser fornecida.")

        target_page.goto(self.portal_url)
        target_page.wait_for_selector("#btnNovo", timeout=8000)
        # Trata diálogos nativos do navegador de forma automática
        target_page.on("dialog", lambda dialog: dialog.accept())

    def consultar_cpf(self, page: Page, cpf: str) -> dict:
        """
        Realiza a busca rápida pelo CPF no Portal Fake para verificar existência e evitar duplicidades.
        Retorna dicionário informando se o cliente já existe e quantidade encontrada.
        """
        target_page = page or self.page
        if not target_page:
            raise ValueError("Uma página válida do Playwright deve ser fornecida.")

        cpf_limpo = re.sub(r"\D", "", str(cpf)).zfill(11)

        try:
            target_page.fill("#q", cpf_limpo)
            target_page.click("#btnBuscar")
            target_page.wait_for_timeout(350)

            # Verifica mensagem de vazio ou contagem
            empty_el = target_page.locator("#empty")
            if empty_el.is_visible():
                return {"existe": False, "total": 0, "cpf": cpf_limpo, "cadastros": []}

            rows = target_page.locator("#tbody tr")
            count = rows.count()

            cadastros = []
            cpf_encontrado = False
            for i in range(count):
                row_text = rows.nth(i).inner_text()
                if cpf_limpo in re.sub(r"\D", "", row_text):
                    cpf_encontrado = True
                    cadastros.append(row_text)

            return {
                "existe": cpf_encontrado,
                "total": count if cpf_encontrado else 0,
                "cpf": cpf_limpo,
                "cadastros": cadastros,
            }

        except Exception as e:
            print(f"[PORTAL FAKE] Aviso ao consultar CPF '{cpf}': {e}")
            return {"existe": False, "total": 0, "cpf": cpf_limpo, "erro": str(e)}

    def cadastrar_cliente(self, page: Page, dados_cliente: dict) -> dict:
        """
        Executa o fluxo completo de inclusão de novo cadastro no Portal Fake:
        1. Clica no botão 'Novo cadastro'
        2. Preenche todos os inputs do modal
        3. Clica em 'Salvar'
        4. Trata mensagens de validação e confirma persistência
        """
        target_page = page or self.page
        if not target_page:
            raise ValueError("Uma página válida do Playwright deve ser fornecida.")

        nome = dados_cliente.get("nome", "")
        sobrenome = dados_cliente.get("sobrenome", "")
        cpf = re.sub(r"\D", "", str(dados_cliente.get("cpf", ""))).zfill(11)
        email = dados_cliente.get("email", "")
        telefone = dados_cliente.get("telefone", "")
        nascimento = dados_cliente.get("nascimento", "1995-01-01")
        status = (dados_cliente.get("status_portal") or dados_cliente.get("status") or "ATIVO").upper()
        endereco = dados_cliente.get("endereco", "")
        observacao = dados_cliente.get("observacoes", dados_cliente.get("observacao", "Cadastrado via Processo 3 - HyperAutomation"))

        print(f"[PORTAL FAKE] Iniciando preenchimento do formulário para {nome} {sobrenome} (CPF: {cpf})...")

        try:
            # 1. Abre o modal
            target_page.click("#btnNovo")
            target_page.wait_for_selector("#modal:not([hidden])", timeout=4000)

            # 2. Preenche os campos do formulário
            target_page.fill("#f_nome", nome)
            target_page.fill("#f_sobrenome", sobrenome)
            target_page.fill("#f_cpf", cpf)
            target_page.fill("#f_email", email)
            target_page.fill("#f_telefone", telefone)
            target_page.fill("#f_nascimento", nascimento)
            target_page.fill("#f_endereco", endereco)
            target_page.fill("#f_observacao", observacao)
            target_page.select_option("#f_status", status)

            # 3. Submete o formulário
            target_page.click("#btnSalvar")
            target_page.wait_for_timeout(300)

            # 4. Verifica se houve erro de validação no formulário (#formMsg)
            form_msg = target_page.locator("#formMsg").inner_text().strip()
            if form_msg:
                # Fecha o modal para não travar a aplicação
                target_page.click("#btnModalClose")
                target_page.wait_for_timeout(200)

                if "ja existe" in form_msg.lower() or "duplic" in form_msg.lower():
                    return {
                        "sucesso": False,
                        "status": "DUPLICADO",
                        "mensagem": f"CPF {cpf} já cadastrado no portal ({form_msg})",
                        "cpf": cpf
                    }
                else:
                    return {
                        "sucesso": False,
                        "status": "ERRO_VALIDACAO",
                        "mensagem": f"Validação do formulário rejeitou o cadastro: {form_msg}",
                        "cpf": cpf
                    }

            # 5. Confirma que o modal foi fechado
            target_page.wait_for_selector("#modal", state="hidden", timeout=4000)
            print(f"[PORTAL FAKE] Cadastro de '{nome} {sobrenome}' (CPF: {cpf}) salvo com sucesso.")

            return {
                "sucesso": True,
                "status": "CADASTRADO",
                "mensagem": f"Cliente {nome} {sobrenome} cadastrado com sucesso no Portal Fake.",
                "cpf": cpf,
                "nome_completo": f"{nome} {sobrenome}".strip()
            }

        except Exception as e:
            # Fallback em caso de exceção: tenta fechar o modal
            try:
                if target_page.locator("#modal:not([hidden])").is_visible():
                    target_page.click("#btnModalClose")
            except Exception:
                pass

            return {
                "sucesso": False,
                "status": "ERRO_EXECUCAO",
                "mensagem": f"Exceção durante cadastro no portal: {str(e)}",
                "cpf": cpf
            }

    def zerar_base(self, page: Page = None):
        """Zera a base de dados do Portal Fake no localStorage para testes limpos."""
        target_page = page or self.page
        if target_page:
            try:
                target_page.evaluate("() => localStorage.removeItem('PF_RPA_DB_V1')")
                target_page.reload()
                target_page.wait_for_selector("#btnNovo", timeout=8000)
                print("[PORTAL FAKE] Base de dados do portal resetada com sucesso.")
            except Exception as e:
                print(f"[PORTAL FAKE] Aviso ao zerar base: {e}")

    def limpar_filtros(self, page: Page = None):
        """Limpa a caixa de busca e filtros para exibir a listagem completa."""
        target_page = page or self.page
        if target_page:
            try:
                target_page.click("#btnLimpar")
                target_page.wait_for_timeout(300)
            except Exception:
                pass

    def capturar_screenshot(self, page: Page, nome_arquivo: str) -> Path:
        """Captura uma tela cheia como evidência de execução."""
        target_page = page or self.page
        if not target_page:
            return None

        caminho = SCREENSHOTS_DIR / nome_arquivo
        target_page.screenshot(path=str(caminho), full_page=True)
        print(f"  [EVIDÊNCIA SCREENSHOT] Salvo em: {caminho.name}")
        return caminho
