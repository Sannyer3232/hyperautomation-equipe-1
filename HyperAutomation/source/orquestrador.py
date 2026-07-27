import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus

BASE_DIR = Path(__file__).resolve().parent
PATH_ROOT = BASE_DIR.parent
BROWSER_DATA_DIR = PATH_ROOT / "resources" / "browser_data"

sys.path.append(str(BASE_DIR))
sys.path.append(str(PATH_ROOT / "resources"))

from portal_bot import carregar_usuarios, preencher_portal_rapido, INDEX_HTML
from common.extracao import extrair_dados, extrair_todos_dados
from common.documento_email import criar_documento, enviar_email

def main():
    # Inicializa conexão com o BotCity Maestro SDK (se executado via Runner)
    maestro = BotMaestroSDK.from_sys_args()

    task_id = None
    modo = "unico"
    row_index = 9
    email_destino = "carvalhosannyer@gmail.com"
    headless = True if maestro.is_online else False
    remetente = None
    senha = None

    if maestro.is_online:
        execution = maestro.get_execution()
        task_id = execution.task_id
        print(f"[BOTCITY] Maestro detectado! Task ID: {task_id}")
        
        # Leitura de parâmetros do Maestro (se configurados na execução)
        params = execution.parameters or {}
        modo = params.get("modo", modo)
        try:
            row_index = int(params.get("row_index", row_index))
        except (ValueError, TypeError):
            row_index = 9
        email_destino = params.get("email_destino", email_destino)
        
        if "headless" in params:
            headless = str(params.get("headless")).lower() in ("true", "1", "yes")

        # Tenta obter credenciais do Maestro Vault se existirem
        try:
            remetente = maestro.get_credential(label="GMAIL_CREDS", key="username")
            senha = maestro.get_credential(label="GMAIL_CREDS", key="password")
        except Exception:
            pass

    try:
        executar_orquestracao(
            modo=modo,
            row_index=row_index,
            email_destino=email_destino,
            headless=headless,
            maestro=maestro,
            task_id=task_id,
            remetente=remetente,
            senha=senha
        )

        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.SUCCESS,
                message="Orquestração concluída com sucesso no BotCity Maestro."
            )
    except Exception as e:
        print(f"[ERRO] Erro durante a execucao: {e}")
        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.FAILED,
                message=f"Erro durante a execução: {e}"
            )
        raise e

def executar_orquestracao(modo="unico", row_index=0, email_destino="carvalhosannyer@gmail.com", 
                         headless=False, maestro=None, task_id=None, remetente=None, senha=None):
    """
    Executa a orquestração do RPA.
    - modo="unico": Extrai e gera documento apenas para a linha especificada (ex: row_index=0).
    - modo="todos": Extrai e gera documento para TODOS os cadastros do portal.
    """
    print("=" * 65)
    print("INICIANDO ORQUESTRAÇÃO RPA COMPLETA (HYPERAUTOMATION)")
    print("=" * 65)

    usuarios = carregar_usuarios()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA_DIR),
            headless=headless
        )
        page = context.new_page()

        portal_url = f"file://{INDEX_HTML.resolve()}"
        print(f"\n[Etapa 1] Abrindo Portal Fake: {portal_url}")
        page.goto(portal_url)

        # 1. Carga ultra-rápida no portal
        print("\n[Etapa 1] Executando preenchimento ultra-rápido dos dados no portal...")
        preencher_portal_rapido(page, usuarios, qtd=10)

        # Captura Print 1: Portal preenchido
        screenshots_dir = PATH_ROOT / "resources" / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        print_portal = screenshots_dir / "01_portal_preenchido.png"
        page.screenshot(path=str(print_portal), full_page=True)
        print(f"  [SCREENSHOT] Salvo: {print_portal.name}")

        if maestro and maestro.is_online and task_id:
            try:
                maestro.post_artifact(task_id=task_id, artifact_name=print_portal.name, filepath=str(print_portal))
            except Exception:
                pass

        # 2. Extração dos dados
        if modo == "todos":
            print("\n[Etapa 2] Extraindo dados de TODOS os cadastros...")
            lista_clientes = extrair_todos_dados(page)
        else:
            print(f"\n[Etapa 2] Extraindo dados do cadastro na linha {row_index}...")
            lista_clientes = [extrair_dados(page, row_index=row_index)]

        # Captura Print 2: Após extração dos dados
        print_extracao = screenshots_dir / "02_extracao_dados.png"
        page.screenshot(path=str(print_extracao), full_page=True)
        print(f"  [SCREENSHOT] Salvo: {print_extracao.name}")

        if maestro and maestro.is_online and task_id:
            try:
                maestro.post_artifact(task_id=task_id, artifact_name=print_extracao.name, filepath=str(print_extracao))
            except Exception:
                pass

        context.close()

    # 3. Geração de documentos, envio de e-mail e exclusão automática da ficha
    for i, cliente in enumerate(lista_clientes, start=1):
        print(f"\n[Etapa 3 - Cliente {i}/{len(lista_clientes)}] Processando: {cliente.get('Nome')} {cliente.get('Sobrenome')}")
        arquivo_docx = criar_documento(cliente)
        print(f"  Documento Word gerado: {arquivo_docx}")

        # Postar o documento como artefato no BotCity Maestro se estiver online
        if maestro and maestro.is_online and task_id:
            try:
                maestro.post_artifact(
                    task_id=task_id,
                    artifact_name=Path(arquivo_docx).name,
                    filepath=arquivo_docx
                )
                print(f"  Artefato publicado no BotCity Maestro: {Path(arquivo_docx).name}")
            except Exception as e_art:
                print(f"  Aviso: Nao foi possivel enviar artefato ao Maestro: {e_art}")

        print(f"  Enviando e-mail para {email_destino}...")
        try:
            enviar_email(email_destino, arquivo_docx, apagar_apos_envio=True, remetente=remetente, senha=senha)
        except Exception as e:
            print(f"  Aviso: Falha ao enviar e-mail do cliente {cliente.get('Nome')}: {e}")

    print("\nORQUESTRAÇÃO FINALIZADA COM SUCESSO!")

if __name__ == "__main__":
    main()
