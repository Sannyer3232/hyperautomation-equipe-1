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
from processo_atendimento.leitor_email import LeitorEmail
from processo_atendimento.validador_docs import ValidadorDocumentos
from processo_atendimento.portal_integracao import PortalIntegracao

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

        params = execution.parameters or {}
        modo = params.get("modo", modo)
        try:
            row_index = int(params.get("row_index", row_index))
        except (ValueError, TypeError):
            row_index = 9
        email_destino = params.get("email_destino", email_destino)

        if "headless" in params:
            headless = str(params.get("headless")).lower() in ("true", "1", "yes")

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
    Executa o fluxo completo do Processo 1 (Setor de Atendimento):
    1. Geração da Ficha Cadastral para Assinatura (.docx) e Envio ao Cliente.
    2. Monitoramento da Caixa de Entrada por E-mails de Retorno com a Ficha Assinada + Documentos (PDF Único).
    3. Validação Documental dos anexos salvos em ERP_Portal_Fake/Downloads.
    4. Movimentação física no ERP (Downloads -> Documentos_OK / Documentos_Pendentes -> Encaminhados).
    5. Automação Web via Playwright para cadastro/atualização no ERP Portal Fake.
    6. Disparo do e-mail HTML com o status final (Aprovado ou Pendente).
    """
    print("=" * 75)
    print("INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION - PROCESSO 1 (CICLO COMPLETO DE ATENDIMENTO)")
    print("=" * 75)

    # 0. Inicialização dos Módulos do Processo 1
    print("\n[Etapa 0] Inicializando Módulos do Processo 1...")
    gestor_erp = GestorArquivos()
    gestor_erp.garantir_estrutura_pastas()

    notificador = NotificadorCliente()
    if remetente and senha:
        notificador.remetente = remetente
        notificador.senha = senha

    leitor_email = LeitorEmail(download_dir=gestor_erp.dir_downloads)
    validador = ValidadorDocumentos()
    portal_integracao = PortalIntegracao()

    # 1. FASE 1: Geração da Ficha Cadastral e Envio de Solicitação de Assinatura
    print("\n[FASE 1] Gerando Ficha de Dados para Assinatura e enviando solicitação ao cliente...")
    cliente_dados = {
        "nome": "Ana",
        "sobrenome": "Silva",
        "cpf": "11122233344",
        "email": email_destino,
        "telefone": "(92) 99888-1122",
        "endereco": "Rua das Flores, 123 - Manaus/AM",
        "status": "PENDENTE"
    }

    protocolo = "2026-0001"
    path_ficha_docx = criar_documento({
        "Nome": cliente_dados["nome"],
        "Sobrenome": cliente_dados["sobrenome"],
        "CPF": cliente_dados["cpf"],
        "Email": cliente_dados["email"],
        "Telefone": cliente_dados["telefone"],
        "Endereco": cliente_dados["endereco"],
        "Status": "AGUARDANDO ASSINATURA E DOCUMENTOS"
    })
    print(f"  Ficha DOCX gerada para assinatura: {Path(path_ficha_docx).name}")

    notificador.enviar_solicitacao_assinatura(
        email_destino=email_destino,
        protocolo=protocolo,
        nome_cliente=f"{cliente_dados['nome']} {cliente_dados['sobrenome']}",
        caminho_ficha_docx=path_ficha_docx
    )

    # 2. FASE 2: Monitoramento da Caixa de Entrada pelo Retorno do Cliente (PDF Único)
    print("\n[FASE 2] Monitorando e-mail de retorno do cliente (Ficha Assinada + Documentos em PDF Único)...")
    solicitacoes_retornadas = leitor_email.ler_emails_pendentes()
    print(f"  E-mails de retorno identificados: {len(solicitacoes_retornadas)}")

    # 3. FASE 3: Validação Documental e Automação Web no Portal Fake
    screenshots_dir = PATH_ROOT / "resources" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA_DIR),
            headless=headless
        )
        page = context.new_page()

        portal_url = f"file://{INDEX_HTML.resolve()}"
        print(f"\n[FASE 3] Conectando ao Portal Fake ERP: {portal_url}")
        page.goto(portal_url)

        # Carga inicial se necessário
        usuarios_base = carregar_usuarios()
        preencher_portal_rapido(page, usuarios_base, qtd=5)

        # Screenshot 1: Portal Carregado
        print_portal = screenshots_dir / "01_portal_preenchido.png"
        page.screenshot(path=str(print_portal), full_page=True)
        print(f"  [SCREENSHOT] Salvo: {print_portal.name}")

        if maestro and maestro.is_online and task_id:
            try:
                maestro.post_artifact(task_id=task_id, artifact_name=print_portal.name, filepath=str(print_portal))
            except Exception:
                pass

        # Processamento das solicitações retornadas
        for idx, solic in enumerate(solicitacoes_retornadas, start=1):
            dados = solic.get("dados_cliente", cliente_dados)
            nome_cliente = f"{dados.get('nome', 'Cliente')} {dados.get('sobrenome', '')}".strip()
            anexos = solic.get("anexos", [])

            print(f"\n[Processando Retorno {idx}/{len(solicitacoes_retornadas)}] Cliente: {nome_cliente} | Protocolo: #{protocolo}")
            print(f"  Anexos salvos em ERP_Portal_Fake/Downloads: {[Path(a).name for a in anexos]}")

            # a) Validação Documental do Retorno
            res_validacao = validador.validar_documentos(anexos)

            if not res_validacao["valido"]:
                print(f"  [VALIDAÇÃO] Documentação REPROVADA para {nome_cliente}.")
                for a in anexos:
                    try:
                        gestor_erp.mover_para_status(Path(a).name, status_ok=False)
                    except Exception as e_mov:
                        print(f"  [GESTOR ARQUIVOS] Aviso: {e_mov}")

                notificador.enviar_resposta(
                    email_destino=email_destino,
                    protocolo=protocolo,
                    aprovado=False,
                    pendencias=res_validacao["pendencias"]
                )
            else:
                print(f"  [VALIDAÇÃO] Documentação e Ficha Assinada APROVADAS para {nome_cliente}.")

                # Move de Downloads para Documentos_OK
                for a in anexos:
                    try:
                        gestor_erp.mover_para_status(Path(a).name, status_ok=True)
                    except Exception as e_mov:
                        print(f"  [GESTOR ARQUIVOS] Aviso: {e_mov}")

                # Cadastro do Cliente no Portal Fake ERP via Playwright
                dados["status"] = "ATIVO"
                portal_integracao.cadastrar_cliente(page, dados)

                # Move de Documentos_OK para Encaminhados
                for a in anexos:
                    try:
                        gestor_erp.mover_para_encaminhados(Path(a).name)
                    except Exception as e_mov:
                        print(f"  [GESTOR ARQUIVOS] Aviso: {e_mov}")

                # E-mail final de aprovação em HTML
                notificador.enviar_resposta(
                    email_destino=email_destino,
                    protocolo=protocolo,
                    aprovado=True
                )

        # Screenshot 2: Finalização do Processo
        print_final = screenshots_dir / "02_extracao_dados.png"
        page.screenshot(path=str(print_final), full_page=True)
        print(f"  [SCREENSHOT] Salvo: {print_final.name}")

        if maestro and maestro.is_online and task_id:
            try:
                maestro.post_artifact(task_id=task_id, artifact_name=print_final.name, filepath=str(print_final))
            except Exception:
                pass

        context.close()

    print("\n" + "=" * 75)
    print("ORQUESTRAÇÃO DO PROCESSO 1 FINALIZADA COM SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    main()
