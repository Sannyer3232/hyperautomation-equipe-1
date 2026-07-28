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
from processo_atendimento.gestor_arquivos import GestorArquivos
from processo_atendimento.resposta_cliente import NotificadorCliente
<<<<<<< HEAD
=======
from processo_atendimento.leitor_email import LeitorEmail
from processo_atendimento.validador_docs import ValidadorDocumentos
from processo_atendimento.portal_integracao import PortalIntegracao
>>>>>>> feature/atendimento-email-validacao

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
                message="Orquestração do Processo 1 concluída com sucesso no BotCity Maestro."
            )
    except Exception as e:
        print(f"[ERRO] Erro durante a execução do orquestrador: {e}")
        if maestro.is_online and task_id:
            maestro.finish_task(
                task_id=task_id,
                status=AutomationTaskFinishStatus.FAILED,
                message=f"Erro durante a execução: {e}"
            )
        raise e

def executar_orquestracao(modo="unico", row_index=0, email_destino="carvalhosannyer@gmail.com", 
                         headless=True, maestro=None, task_id=None, remetente=None, senha=None):
    """
    Executa a orquestração do Processo 1 (Setor de Atendimento - Hyperautomation):
    1. GestorArquivos: Garante pastas do ERP Simulado.
    2. LeitorEmail: Lê solicitações recebidas dos clientes e baixa anexos em ERP_Portal_Fake/Downloads.
    3. ValidadorDocumentos: Analisa a conformidade documental dos anexos.
    4. PortalIntegracao & Playwright: Realiza o cadastro/atualização no ERP Portal Fake.
    5. NotificadorCliente: Dispara e-mail em HTML com o status (Aprovado ou Pendente).
    6. GestorArquivos: Organiza a movimentação física dos arquivos (OK -> Encaminhados / Pendentes).
    """
<<<<<<< HEAD
    print("=" * 65)
    print("INICIANDO ORQUESTRAÇÃO RPA COMPLETA (HYPERAUTOMATION - PROCESSO 1)")
    print("=" * 65)

    # 0. Inicializa Módulos do Processo 1 (Gestor ERP e Notificador)
    gestor_erp = GestorArquivos()
    gestor_erp.garantir_estrutura_pastas()
=======
    print("=" * 70)
    print("INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION - PROCESSO 1 (ATENDIMENTO)")
    print("=" * 70)

    # 0. Inicialização dos Módulos do Processo 1
    print("\n[Etapa 0] Inicializando Módulos do Processo 1...")
    gestor_erp = GestorArquivos()
    gestor_erp.garantir_estrutura_pastas()
    
>>>>>>> feature/atendimento-email-validacao
    notificador = NotificadorCliente()
    if remetente and senha:
        notificador.remetente = remetente
        notificador.senha = senha

<<<<<<< HEAD
    usuarios = carregar_usuarios()
=======
    leitor_email = LeitorEmail(download_dir=gestor_erp.dir_downloads)
    validador = ValidadorDocumentos()
    portal_integracao = PortalIntegracao()

    # 1. Leitura de solicitações de e-mail e extração de anexos
    print("\n[Etapa 1] Lendo e-mails de solicitação de atendimento dos clientes...")
    solicitacoes = leitor_email.ler_emails_pendentes()
    print(f"  Total de solicitações a processar: {len(solicitacoes)}")

    # 2. Execução da Automação Web via Playwright (Portal Fake)
    screenshots_dir = PATH_ROOT / "resources" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
>>>>>>> feature/atendimento-email-validacao

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA_DIR),
            headless=headless
        )
        page = context.new_page()

        portal_url = f"file://{INDEX_HTML.resolve()}"
        print(f"\n[Etapa 2] Conectando ao Portal Fake: {portal_url}")
        page.goto(portal_url)

        # Carga inicial se necessário
        usuarios_base = carregar_usuarios()
        preencher_portal_rapido(page, usuarios_base, qtd=5)

        # Print 1: Portal Carregado
        print_portal = screenshots_dir / "01_portal_preenchido.png"
        page.screenshot(path=str(print_portal), full_page=True)
        print(f"  [SCREENSHOT] Salvo: {print_portal.name}")

        if maestro and maestro.is_online and task_id:
            try:
                maestro.post_artifact(task_id=task_id, artifact_name=print_portal.name, filepath=str(print_portal))
            except Exception:
                pass

        # 3. Processamento individual de cada solicitação
        for idx, solic in enumerate(solicitacoes, start=1):
            dados = solic.get("dados_cliente", {})
            nome_cliente = f"{dados.get('nome', 'Cliente')} {dados.get('sobrenome', '')}".strip()
            protocolo = solic.get("protocolo", f"2026-{idx:04d}")
            email_cliente = solic.get("remetente", email_destino)
            if "@" not in email_cliente:
                email_cliente = email_destino

            anexos = solic.get("anexos", [])

            print(f"\n[Etapa 3 - Solicitação {idx}/{len(solicitacoes)}] Cliente: {nome_cliente} | Protocolo: #{protocolo}")
            print(f"  Anexos recebidos ({len(anexos)}): {[Path(a).name for a in anexos]}")

            # a) Validação Documental
            res_validacao = validador.validar_documentos(anexos)

            if not res_validacao["valido"]:
                print(f"  [STATUS] Documentação REPROVADA / PENDENTE para {nome_cliente}.")
                # Move arquivos para Documentos_Pendentes
                for a in anexos:
                    try:
                        gestor_erp.mover_para_status(Path(a).name, status_ok=False)
                    except Exception as e_mov:
                        print(f"  [GESTOR ARQUIVOS] Aviso: {e_mov}")

                # Envia e-mail de pendência em HTML
                notificador.enviar_resposta(
                    email_destino=email_cliente,
                    protocolo=protocolo,
                    aprovado=False,
                    pendencias=res_validacao["pendencias"]
                )
            else:
                print(f"  [STATUS] Documentação APROVADA para {nome_cliente}.")
                # Move arquivos de Downloads para Documentos_OK
                for a in anexos:
                    try:
                        gestor_erp.mover_para_status(Path(a).name, status_ok=True)
                    except Exception as e_mov:
                        print(f"  [GESTOR ARQUIVOS] Aviso: {e_mov}")

                # Realiza o cadastro do cliente no Portal Fake ERP via Playwright
                sucesso_cadastro = portal_integracao.cadastrar_cliente(page, dados)

                # Move arquivos de Documentos_OK para Encaminhados
                for a in anexos:
                    try:
                        gestor_erp.mover_para_encaminhados(Path(a).name)
                    except Exception as e_mov:
                        print(f"  [GESTOR ARQUIVOS] Aviso: {e_mov}")

                # Envia e-mail em HTML informando aprovação e encaminhamento
                notificador.enviar_resposta(
                    email_destino=email_cliente,
                    protocolo=protocolo,
                    aprovado=True
                )

                # Gera Ficha Cadastral em .docx para histórico interno
                arquivo_docx = criar_documento({
                    "Nome": dados.get("nome", "Cliente"),
                    "Sobrenome": dados.get("sobrenome", ""),
                    "CPF": dados.get("cpf", "11122233344"),
                    "Email": email_cliente,
                    "Telefone": dados.get("telefone", ""),
                    "Endereco": dados.get("endereco", ""),
                    "Status": "APROVADO E ENCAMINHADO"
                })
                print(f"  Ficha DOCX gerada: {Path(arquivo_docx).name}")

                if maestro and maestro.is_online and task_id:
                    try:
                        maestro.post_artifact(task_id=task_id, artifact_name=Path(arquivo_docx).name, filepath=str(arquivo_docx))
                    except Exception:
                        pass

        # Print 2: Finalização dos Cadastros
        print_final = screenshots_dir / "02_extracao_dados.png"
        page.screenshot(path=str(print_final), full_page=True)
        print(f"  [SCREENSHOT] Salvo: {print_final.name}")

        if maestro and maestro.is_online and task_id:
            try:
                maestro.post_artifact(task_id=task_id, artifact_name=print_final.name, filepath=str(print_final))
            except Exception:
                pass

        context.close()

<<<<<<< HEAD
    # 3. Geração de documentos, organização no ERP e envio de notificação ao cliente
    for i, cliente in enumerate(lista_clientes, start=1):
        nome_completo = f"{cliente.get('Nome')} {cliente.get('Sobrenome')}"
        protocolo = f"2026-{i:04d}"
        print(f"\n[Etapa 3 - Cliente {i}/{len(lista_clientes)}] Processando: {nome_completo} (Protocolo: #{protocolo})")
        
        # Geração da Ficha Word
        arquivo_docx = criar_documento(cliente)
        path_docx = Path(arquivo_docx)
        print(f"  Documento Word gerado: {path_docx.name}")

        # Movimentação física no ERP Simulado
        # Coloca em Downloads e em seguida move para Documentos_OK
        dest_downloads = gestor_erp.dir_downloads / path_docx.name
        if path_docx.exists():
            import shutil
            shutil.copy(str(path_docx), str(dest_downloads))
            gestor_erp.mover_para_status(path_docx.name, status_ok=True)
            gestor_erp.mover_para_encaminhados(path_docx.name)

        # Postar o documento como artefato no BotCity Maestro se estiver online
        if maestro and maestro.is_online and task_id:
            try:
                maestro.post_artifact(
                    task_id=task_id,
                    artifact_name=path_docx.name,
                    filepath=str(path_docx)
                )
                print(f"  Artefato publicado no BotCity Maestro: {path_docx.name}")
            except Exception as e_art:
                print(f"  Aviso: Nao foi possivel enviar artefato ao Maestro: {e_art}")

        # Notificação HTML via NotificadorCliente
        print(f"  Enviando notificação por e-mail para {email_destino}...")
        try:
            notificador.enviar_resposta(
                email_destino=email_destino,
                protocolo=protocolo,
                aprovado=True
            )
            # Envio legado do anexo .docx
            enviar_email(email_destino, arquivo_docx, apagar_apos_envio=True, remetente=remetente, senha=senha)
        except Exception as e:
            print(f"  Aviso: Falha no processo de notificação do cliente {nome_completo}: {e}")

    print("\nORQUESTRAÇÃO FINALIZADA COM SUCESSO!")
=======
    print("\n" + "=" * 70)
    print("ORQUESTRAÇÃO DO PROCESSO 1 FINALIZADA COM SUCESSO!")
    print("=" * 70)
>>>>>>> feature/atendimento-email-validacao

if __name__ == "__main__":
    main()
