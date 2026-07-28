import sys
import os
import time
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
    modo = "demo_completo"
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
                message=f"Orquestração (Modo: {modo}) concluída com sucesso no BotCity Maestro."
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

def executar_orquestracao(modo="demo_completo", row_index=0, email_destino="carvalhosannyer@gmail.com", 
                         headless=True, maestro=None, task_id=None, remetente=None, senha=None):
    """
    Executa a orquestração do Processo 1 em modos operacionais distintos:
    - modo="enviar_solicitacoes": Gera a Ficha .docx e envia o e-mail de solicitação de assinatura ao cliente.
    - modo="processar_retornos": Monitora a caixa por e-mails NÃO LIDOS, valida o PDF e cadastra no Portal Fake.
    - modo="demo_completo": Executa as fases sequencialmente demonstrando o ciclo completo com pausa consciente.
    """
    print("=" * 75)
    print(f"INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION - PROCESSO 1 (MODO: {modo.upper()})")
    print("=" * 75)

    # 0. Inicialização dos Módulos
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

    screenshots_dir = PATH_ROOT / "resources" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

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

    # =========================================================================
    # FASE 1: GERAÇÃO DA FICHA E DISPARO DO E-MAIL DE SOLICITAÇÃO DE ASSINATURA
    # =========================================================================
    if modo in ["enviar_solicitacoes", "demo_completo"]:
        print("\n" + "-" * 60)
        print("[FASE 1] GERAÇÃO E ENVIO DE SOLICITAÇÃO DE ASSINATURA")
        print("-" * 60)

        path_ficha_docx = criar_documento({
            "Nome": cliente_dados["nome"],
            "Sobrenome": cliente_dados["sobrenome"],
            "CPF": cliente_dados["cpf"],
            "Email": cliente_dados["email"],
            "Telefone": cliente_dados["telefone"],
            "Endereco": cliente_dados["endereco"],
            "Status": "AGUARDANDO ASSINATURA E DOCUMENTOS"
        })
        print(f"  [FASE 1] Ficha DOCX gerada para assinatura: {Path(path_ficha_docx).name}")

        print(f"  [FASE 1] Enviando e-mail de solicitação de assinatura para {email_destino}...")
        notificador.enviar_solicitacao_assinatura(
            email_destino=email_destino,
            protocolo=protocolo,
            nome_cliente=f"{cliente_dados['nome']} {cliente_dados['sobrenome']}",
            caminho_ficha_docx=path_ficha_docx
        )
        print("  [FASE 1] Solicitação enviada! Cliente registrado no estado 'AGUARDANDO RETORNO'.")

        if modo == "enviar_solicitacoes":
            print("\n[FINALIÇÃO] Fase 1 concluída. O robô aguardará o envio do retorno do cliente para a Fase 2.")
            return

        # No modo demonstração completa, adiciona um pequeno delay consciente antes de checar o retorno
        print("\n  [DEMO] Simulando recebimento do retorno do cliente...")
        time.sleep(2)

    # =========================================================================
    # FASE 2 & 3: MONITORAMENTO DA CAIXA DE RETORNO, VALIDAÇÃO E CADASTRO
    # =========================================================================
    if modo in ["processar_retornos", "demo_completo"]:
        print("\n" + "-" * 60)
        print("[FASE 2 & 3] MONITORAMENTO DO RETORNO, VALIDAÇÃO E CADASTRO")
        print("-" * 60)

        # Para testes demonstrativos, cria o arquivo simulado em Downloads apenas se ainda não existir
        pdf_simulado = gestor_erp.dir_downloads / "Ficha_Assinada_e_Documentos_Ana_Silva.pdf"
        if not pdf_simulado.exists() and not (gestor_erp.dir_ok / pdf_simulado.name).exists() and not (gestor_erp.dir_encaminhados / pdf_simulado.name).exists():
            with open(pdf_simulado, "w", encoding="utf-8") as f:
                f.write("%PDF-1.4 Conteúdo Simulado: Ficha Cadastral Assinada + RG/CPF + Comprovante de Residência")

        print("  [FASE 2] Buscando novos e-mails de retorno não lidos (UNSEEN)...")
        solicitacoes_retornadas = leitor_email.ler_emails_pendentes(marcar_como_lido=True)

        if not solicitacoes_retornadas:
            print("  [FASE 2] Nenhum novo e-mail de retorno pendente localizado no momento.")
            print("\nORQUESTRAÇÃO CONCLUÍDA SEM NOVOS PROCESSAMENTOS.")
            return

        print(f"  [FASE 2] E-mails de retorno identificados para processar: {len(solicitacoes_retornadas)}")

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(BROWSER_DATA_DIR),
                headless=headless
            )
            page = context.new_page()

            portal_url = f"file://{INDEX_HTML.resolve()}"
            print(f"\n  [FASE 3] Conectando ao Portal Fake ERP: {portal_url}")
            page.goto(portal_url)

            usuarios_base = carregar_usuarios()
            preencher_portal_rapido(page, usuarios_base, qtd=5)

            print_portal = screenshots_dir / "01_portal_preenchido.png"
            page.screenshot(path=str(print_portal), full_page=True)
            print(f"    [SCREENSHOT] Salvo: {print_portal.name}")

            for idx, solic in enumerate(solicitacoes_retornadas, start=1):
                dados = solic.get("dados_cliente", cliente_dados)
                nome_cliente = f"{dados.get('nome', 'Cliente')} {dados.get('sobrenome', '')}".strip()
                anexos = solic.get("anexos", [])

                print(f"\n  [Processando Retorno {idx}/{len(solicitacoes_retornadas)}] Cliente: {nome_cliente} | Protocolo: #{protocolo}")
                print(f"    Anexos baixados: {[Path(a).name for a in anexos]}")

                # Validação documental
                res_validacao = validador.validar_documentos(anexos)

                if not res_validacao["valido"]:
                    print(f"    [VALIDAÇÃO] Documentação REPROVADA / PENDENTE para {nome_cliente}.")
                    for a in anexos:
                        try:
                            gestor_erp.mover_para_status(Path(a).name, status_ok=False)
                        except Exception as e_mov:
                            print(f"    [GESTOR ARQUIVOS] Aviso: {e_mov}")

                    notificador.enviar_resposta(
                        email_destino=email_destino,
                        protocolo=protocolo,
                        aprovado=False,
                        pendencias=res_validacao["pendencias"]
                    )
                else:
                    print(f"    [VALIDAÇÃO] Documentação e Ficha Assinada APROVADAS para {nome_cliente}.")

                    # Move de Downloads para Documentos_OK
                    for a in anexos:
                        try:
                            gestor_erp.mover_para_status(Path(a).name, status_ok=True)
                        except Exception as e_mov:
                            print(f"    [GESTOR ARQUIVOS] Aviso: {e_mov}")

                    # Cadastro no Portal Fake via Playwright
                    dados["status"] = "ATIVO"
                    portal_integracao.cadastrar_cliente(page, dados)

                    # Move de Documentos_OK para Encaminhados
                    for a in anexos:
                        try:
                            gestor_erp.mover_para_encaminhados(Path(a).name)
                        except Exception as e_mov:
                            print(f"    [GESTOR ARQUIVOS] Aviso: {e_mov}")

                    # Envia e-mail final informando a conclusão e aprovação
                    print(f"    [FASE 3] Enviando e-mail de CONFIRMAÇÃO DE CADASTRO para {email_destino}...")
                    notificador.enviar_resposta(
                        email_destino=email_destino,
                        protocolo=protocolo,
                        aprovado=True
                    )

            print_final = screenshots_dir / "02_extracao_dados.png"
            page.screenshot(path=str(print_final), full_page=True)
            print(f"    [SCREENSHOT] Salvo: {print_final.name}")

            context.close()

    print("\n" + "=" * 75)
    print("ORQUESTRAÇÃO DO PROCESSO 1 FINALIZADA COM SUCESSO!")
    print("=" * 75)

if __name__ == "__main__":
    main()
