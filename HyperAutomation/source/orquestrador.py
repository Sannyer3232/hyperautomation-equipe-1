import sys
import os
import time
import argparse
from pathlib import Path
from botcity.maestro import BotMaestroSDK, AutomationTaskFinishStatus

BASE_DIR = Path(__file__).resolve().parent
PATH_ROOT = BASE_DIR.parent
BROWSER_DATA_DIR = PATH_ROOT / "resources" / "browser_data"

sys.path.append(str(BASE_DIR))
sys.path.append(str(PATH_ROOT / "resources"))

from portal_bot import carregar_usuarios, CSV_PATH
from common.documento_email import criar_documento, enviar_email
from common.protocolo import gerar_protocolo_unico
from processo_organizacao.planilha_mestra import GerenciadorPlanilha
from processo_organizacao.extrator_dados import ExtratorPDF
from processo_atendimento.gestor_arquivos import GestorArquivos
from processo_atendimento.resposta_cliente import NotificadorCliente
from processo_atendimento.leitor_email import LeitorEmail
from processo_atendimento.validador_docs import ValidadorDocumentos
from processo_atendimento.processo_sac import ProcessoSAC, executar_processo_sac
from processo_cadastro import executar_processo3, OrquestradorCadastro
from processo_relatorios import executar_processo5


def main():
    # Inicializa conexão com o BotCity Maestro SDK (se executado via Runner)
    try:
        maestro = BotMaestroSDK.from_sys_args()
    except Exception:
        maestro = BotMaestroSDK()

    parser = argparse.ArgumentParser(
        description="Orquestrador HyperAutomation - Processo Integrado (Atendimento, Organização, Cadastro, SAC e Relatórios)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "modo_pos",
        nargs="?",
        default=None,
        help="Modo de execução posicional:\n"
             "  cadastro            : Executa FASE 3 (Cadastro no Portal Fake lendo somente a Planilha Mestra)\n"
             "  sac / processo4     : Executa FASE 4 (SAC e registro de atendimentos na planilha de SAC)\n"
             "  relatorios / p5     : Executa FASE 5 (Consolidação, Métricas e Relatório Gerencial)\n"
             "  processar_retornos  : Executa FASE 2 & 3 (leitura de e-mails/documentos, gravação na Planilha Mestra e cadastro)\n"
             "  enviar_solicitacoes : Executa FASE 1 (leitura do CSV, geração e envio da ficha de assinatura)\n"
             "  demo_completo       : Executa FASES 1, 2, 3, 4 e 5 integradas (demonstração completa)"
    )
    parser.add_argument(
        "-m", "--modo",
        choices=["cadastro", "processo3", "sac", "processo4", "relatorios", "processo5", "processar_retornos", "enviar_solicitacoes", "demo_completo", "completo"],
        default=None,
        help="Modo de execução (sobrescreve o argumento posicional)"
    )
    parser.add_argument(
        "-i", "--id", "--id-solicitacao",
        dest="id_solicitacao",
        type=str,
        default=None,
        help="ID da solicitação no arquivo CSV (ex: 8 para Sannyer Nery)"
    )
    parser.add_argument(
        "-c", "--cpf",
        type=str,
        default=None,
        help="CPF do cliente a ser selecionado no arquivo CSV ou filtrado na Planilha Mestra"
    )
    parser.add_argument(
        "-r", "--row-index",
        type=int,
        default=None,
        help="Índice da linha do cliente no arquivo CSV de cadastros (padrão: 0 ou 2)"
    )
    parser.add_argument(
        "-e", "--email-destino",
        type=str,
        default="2026500534@ifam.edu.br",
        help="E-mail de destino padrão para as solicitações"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=None,
        help="Executar navegador em modo headless (sem interface gráfica)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Executar navegador com interface gráfica visível"
    )
    parser.add_argument(
        "--zerar-base",
        action="store_true",
        default=False,
        help="Zerar base de cadastros do Portal Fake antes da execução (útil para testes limpos)"
    )

    args, unknown = parser.parse_known_args()

    # Define valores via CLI
    modo = args.modo or args.modo_pos or "cadastro"
    row_index = args.row_index if args.row_index is not None else 2
    id_solicitacao = args.id_solicitacao
    cpf_filtro = args.cpf
    email_destino = args.email_destino
    headless = args.headless
    zerar_base = args.zerar_base

    task_id = None
    remetente = None
    senha = None

    if maestro.is_online:
        execution = maestro.get_execution()
        task_id = execution.task_id
        print(f"[BOTCITY] Maestro detectado! Task ID: {task_id}")

        params = execution.parameters or {}
        modo = params.get("modo", modo)
        if "id" in params or "id_solicitacao" in params:
            id_solicitacao = str(params.get("id") or params.get("id_solicitacao"))
        if "cpf" in params:
            cpf_filtro = str(params.get("cpf"))
        if "row_index" in params:
            try:
                row_index = int(params.get("row_index"))
            except (ValueError, TypeError):
                pass
        email_destino = params.get("email_destino", email_destino)

        if "headless" in params:
            headless = str(params.get("headless")).lower() in ("true", "1", "yes")
        if "zerar_base" in params:
            zerar_base = str(params.get("zerar_base")).lower() in ("true", "1", "yes")

        try:
            remetente = maestro.get_credential(label="GMAIL_CREDS", key="username")
            senha = maestro.get_credential(label="GMAIL_CREDS", key="password")
        except Exception:
            pass

    if headless is None:
        headless = True if (maestro and maestro.is_online) else False

    try:
        executar_orquestracao(
            modo=modo,
            row_index=row_index,
            id_solicitacao=id_solicitacao,
            cpf_filtro=cpf_filtro,
            email_destino=email_destino,
            headless=headless,
            maestro=maestro,
            task_id=task_id,
            remetente=remetente,
            senha=senha,
            zerar_base=zerar_base
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


def executar_orquestracao(modo="cadastro", row_index=2, id_solicitacao=None, cpf_filtro=None, email_destino="2026500534@ifam.edu.br", 
                         headless=True, maestro=None, task_id=None, remetente=None, senha=None, zerar_base=False):
    """
    Executa a orquestração HyperAutomation:
    - MODO CADASTRO (Padrão): Processo 3 exclusivo lendo os registros aprovados da Planilha_Mestra.xlsx.
    - MODO PROCESSAR_RETORNOS: Validação documental, registro na Planilha Mestra (Processo 2) e cadastro (Processo 3).
    - MODO ENVIAR_SOLICITACOES: Leitura do CSV e envio de ficha de cadastro para assinatura (Processo 1).
    - MODO DEMO_COMPLETO: Execução integrada de demonstração (Processos 1, 2 e 3).
    """
    print("=" * 75)
    print(f"INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION (MODO: {modo.upper()})")
    print("=" * 75)

    # 0. Inicialização dos Módulos
    print("\n[Etapa 0] Inicializando Módulos do Sistema...")
    gestor_erp = GestorArquivos()
    gestor_erp.garantir_estrutura_pastas()
    caminho_planilha = gestor_erp.dir_sistema_integrador / "Planilha_Mestra.xlsx"
    planilha = GerenciadorPlanilha(caminho_planilha)
    planilha.inicializar_planilha()

    notificador = NotificadorCliente()
    if remetente and senha:
        notificador.remetente = remetente
        notificador.senha = senha

    leitor_email = LeitorEmail(download_dir=gestor_erp.dir_downloads)
    validador = ValidadorDocumentos()

    screenshots_dir = PATH_ROOT / "resources" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    nome = "Cliente"
    sobrenome = "Solicitante"
    cpf = cpf_filtro or "11122233344"
    email_cliente = email_destino or "2026500534@ifam.edu.br"
    telefone = "(92) 99888-1122"
    nascimento = "1995-01-01"
    endereco = "Manaus/AM"
    protocolo = gerar_protocolo_unico()

    # Carrega do CSV apenas se o modo requisitar Fase 1 / Demo
    if modo in ["enviar_solicitacoes", "demo_completo"]:
        csv_file = CSV_PATH if Path(CSV_PATH).exists() else (PATH_ROOT / "resources" / "cadastros_portal_fake_20.csv")
        print(f"\n[Etapa 1] Carregando clientes para envio de solicitações do CSV: {csv_file.name}")
        usuarios_csv = carregar_usuarios(csv_file)

        if not usuarios_csv:
            raise ValueError(f"Nenhum cadastro encontrado no CSV em: {csv_file}")

        cliente_csv = None
        idx_selecionado = 0
        if id_solicitacao is not None:
            id_str = str(id_solicitacao).strip()
            for idx, u in enumerate(usuarios_csv):
                if str(u.get("id_solicitacao", "")).strip() == id_str:
                    cliente_csv = u
                    idx_selecionado = idx
                    break
            if cliente_csv:
                print(f"  [Busca por ID] Cliente localizado pelo id_solicitacao='{id_str}': {cliente_csv.get('nome')} {cliente_csv.get('sobrenome')}")

        if cliente_csv is None and cpf_filtro is not None:
            cpf_digs = "".join(filter(str.isdigit, str(cpf_filtro)))
            for idx, u in enumerate(usuarios_csv):
                u_cpf_digs = "".join(filter(str.isdigit, str(u.get("cpf", ""))))
                if u_cpf_digs == cpf_digs:
                    cliente_csv = u
                    idx_selecionado = idx
                    break
            if cliente_csv:
                print(f"  [Busca por CPF] Cliente localizado pelo CPF='{cpf_filtro}': {cliente_csv.get('nome')} {cliente_csv.get('sobrenome')}")

        if cliente_csv is None:
            idx_selecionado = min(max(0, row_index), len(usuarios_csv) - 1)
            cliente_csv = usuarios_csv[idx_selecionado]

        nome = cliente_csv.get("nome", "Cliente").strip()
        sobrenome = cliente_csv.get("sobrenome", "Solicitante").strip()
        cpf = cliente_csv.get("cpf", "11122233344").strip()

        if email_destino:
            email_cliente = email_destino
        elif cliente_csv.get("email", "").strip() and "@" in cliente_csv.get("email", ""):
            email_cliente = cliente_csv.get("email", "").strip()

        telefone = cliente_csv.get("telefone", "(92) 99888-1122").strip()
        nascimento = cliente_csv.get("nascimento", "1995-01-01").strip()
        endereco = cliente_csv.get("endereco", "Manaus/AM").strip()

        print(f"  [Cliente Selecionado (ID: {cliente_csv.get('id_solicitacao', 'N/A')}, Linha CSV: {idx_selecionado})]: {nome} {sobrenome} | CPF: {cpf} | Email: {email_cliente}")

    # =========================================================================
    # FASE 1: GERAÇÃO DA FICHA E DISPARO DO E-MAIL DE SOLICITAÇÃO DE ASSINATURA
    # =========================================================================
    if modo in ["enviar_solicitacoes", "demo_completo"]:
        print("\n" + "-" * 60)
        print(f"[FASE 1] GERAÇÃO E ENVIO DE FICHA PARA ASSINATURA ({nome} {sobrenome}) | Protocolo: #{protocolo}")
        print("-" * 60)

        path_ficha_docx = criar_documento({
            "Nome": nome,
            "Sobrenome": sobrenome,
            "CPF": cpf,
            "E-mail": email_cliente,
            "Telefone": telefone,
            "Nascimento": nascimento,
            "Endereco": endereco,
            "Status": "AGUARDANDO ASSINATURA E DOCUMENTOS"
        })
        print(f"  [FASE 1] Ficha DOCX gerada com sucesso: {Path(path_ficha_docx).name}")

        print(f"  [FASE 1] Enviando e-mail de solicitação de assinatura para {email_cliente}...")
        notificador.enviar_solicitacao_assinatura(
            email_destino=email_cliente,
            protocolo=protocolo,
            nome_cliente=f"{nome} {sobrenome}",
            caminho_ficha_docx=path_ficha_docx
        )
        print("  [FASE 1] Solicitação enviada! Cliente registrado no estado 'AGUARDANDO RETORNO'.")

        if modo == "enviar_solicitacoes":
            print("\n[FINALIZAÇÃO] Fase 1 concluída com sucesso. O robô aguardará o envio do retorno do cliente.")
            return

        print("\n  [DEMO] Simulando recebimento do retorno do cliente...")
        time.sleep(2)

    # =========================================================================
    # FASE 2: MONITORAMENTO DA CAIXA DE RETORNO E ORGANIZAÇÃO NA PLANILHA MESTRA
    # =========================================================================
    if modo in ["processar_retornos", "demo_completo"]:
        print("\n" + "-" * 60)
        print(f"[FASE 2] MONITORAMENTO DO RETORNO E VALIDAÇÃO DOCUMENTAL ({nome} {sobrenome}) | Protocolo: #{protocolo}")
        print("-" * 60)

        # Gera arquivo PDF simulado válido contendo os 3 documentos obrigatórios no modo demo
        if modo == "demo_completo":
            nome_limpo_pdf = f"Ficha_Assinada_e_Documentos_{nome}_{sobrenome}".replace(" ", "_")
            pdf_simulado = gestor_erp.dir_downloads / f"{nome_limpo_pdf}.pdf"
            if not pdf_simulado.exists() and not (gestor_erp.dir_ok / pdf_simulado.name).exists() and not (gestor_erp.dir_arquivados / pdf_simulado.name).exists():

                pdf_content = (
                    f"%PDF-1.4\n"
                    f"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
                    f"2 0 obj\n<< /Type /Pages /Kids [3 0 R 4 0 R 5 0 R] /Count 3 >>\nendobj\n"
                    f"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 6 0 R /Resources << /Font << /F1 9 0 R >> >> >>\nendobj\n"
                    f"4 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 7 0 R /Resources << /Font << /F1 9 0 R >> >> >>\nendobj\n"
                    f"5 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 8 0 R /Resources << /Font << /F1 9 0 R >> >> >>\nendobj\n"
                    f"6 0 obj\n<< /Length 120 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Ficha Cadastral Assinada - Portal Fake Solucoes Digitais) Tj\n0 -20 Td\n(Cliente: {nome} {sobrenome} | CPF: {cpf}) Tj\nET\nendstream\nendobj\n"
                    f"7 0 obj\n<< /Length 120 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Documento Oficial com Foto - RG / CPF / Identidade) Tj\n0 -20 Td\n(Registro Geral - SSP) Tj\nET\nendstream\nendobj\n"
                    f"8 0 obj\n<< /Length 120 >>\nstream\nBT\n/F1 12 Tf\n50 700 Td\n(Comprovante de Residencia - Conta de Luz / Agua / Fatura) Tj\n0 -20 Td\n(Endereco Residencial Confirmado) Tj\nET\nendstream\nendobj\n"
                    f"9 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
                    f"xref\n0 10\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000125 00000 n \n0000000244 00000 n \n0000000363 00000 n \n0000000482 00000 n \n0000000652 00000 n \n0000000812 00000 n \n0000000972 00000 n \ntrailer\n<< /Size 10 /Root 1 0 R >>\nstartxref\n1053\n%%EOF\n"
                )
                with open(pdf_simulado, "wb") as f:
                    f.write(pdf_content.encode('latin1'))

        print("  [FASE 2] Buscando novos e-mails de retorno não lidos (UNSEEN)...")
        permitir_sim = (modo == "demo_completo")
        solicitacoes_retornadas = leitor_email.ler_emails_pendentes(marcar_como_lido=True, permitir_simulacao=permitir_sim)

        if not solicitacoes_retornadas:
            print("  [FASE 2] Nenhum novo e-mail de retorno pendente localizado no momento.")
        else:
            print(f"  [FASE 2] E-mails de retorno identificados para processar: {len(solicitacoes_retornadas)}")

            for idx, solic in enumerate(solicitacoes_retornadas, start=1):
                anexos = solic.get("anexos", [])

                print(f"\n  [Processando Retorno {idx}/{len(solicitacoes_retornadas)}] Cliente: {nome} {sobrenome} | Protocolo: #{protocolo}")
                print(f"    Anexos baixados: {[Path(a).name for a in anexos]}")

                # Validação documental
                res_validacao = validador.validar_documentos(anexos)

                if not res_validacao["valido"]:
                    print(f"    [VALIDAÇÃO] Documentação REPROVADA / PENDENTE para {nome} {sobrenome}.")
                    for a in anexos:
                        try:
                            gestor_erp.mover_para_status(Path(a).name, status_ok=False)
                        except Exception as e_mov:
                            print(f"    [GESTOR ARQUIVOS] Aviso: {e_mov}")

                    notificador.enviar_resposta(
                        email_destino=email_cliente,
                        protocolo=protocolo,
                        aprovado=False,
                        pendencias=res_validacao["pendencias"]
                    )
                else:
                    print(f"    [VALIDAÇÃO] Documentação e Ficha Assinada APROVADAS para {nome} {sobrenome}.")

                    # Move de Downloads para Documentos_OK
                    for a in anexos:
                        try:
                            gestor_erp.mover_para_status(Path(a).name, status_ok=True)
                        except Exception as e_mov:
                            print(f"    [GESTOR ARQUIVOS] Aviso: {e_mov}")

                    # Extração do PDF e Registro na Planilha Mestra (Processo 2)
                    for a in anexos:
                        p_anexo = gestor_erp.dir_ok / Path(a).name
                        if p_anexo.exists() and p_anexo.suffix.lower() == ".pdf":
                            try:
                                extrator = ExtratorPDF(p_anexo)
                                dados_extraidos_pdf = extrator.extrair_dados()

                                # Busca no CSV pelo CPF extraído para obter dados oficiais caso faltem no PDF
                                cpf_extraido = dados_extraidos_pdf.get("cpf")
                                info_oficial = None
                                if cpf_extraido and cpf_extraido != "NÃO ENCONTRADO":
                                    try:
                                        csv_path_ref = CSV_PATH if Path(CSV_PATH).exists() else (PATH_ROOT / "resources" / "cadastros_portal_fake_20.csv")
                                        if csv_path_ref.exists():
                                            usuarios_ref = carregar_usuarios(csv_path_ref)
                                            for u_ref in usuarios_ref:
                                                if "".join(filter(str.isdigit, str(u_ref.get("cpf", "")))) == cpf_extraido:
                                                    info_oficial = u_ref
                                                    break
                                    except Exception:
                                        pass

                                # Fallbacks caso algum campo não conste no PDF
                                if dados_extraidos_pdf.get("cpf") in ("NÃO ENCONTRADO", "", None):
                                    dados_extraidos_pdf["cpf"] = cpf
                                if not dados_extraidos_pdf.get("nome"):
                                    dados_extraidos_pdf["nome"] = (info_oficial.get("nome") if info_oficial else nome)
                                    dados_extraidos_pdf["sobrenome"] = (info_oficial.get("sobrenome") if info_oficial else sobrenome)
                                    dados_extraidos_pdf["nome_completo"] = f"{dados_extraidos_pdf['nome']} {dados_extraidos_pdf['sobrenome']}".strip()
                                if not dados_extraidos_pdf.get("email"):
                                    dados_extraidos_pdf["email"] = (info_oficial.get("email") if info_oficial else email_cliente)
                                if not dados_extraidos_pdf.get("telefone"):
                                    dados_extraidos_pdf["telefone"] = (info_oficial.get("telefone") if info_oficial else telefone)
                                if not dados_extraidos_pdf.get("nascimento"):
                                    dados_extraidos_pdf["nascimento"] = (info_oficial.get("nascimento") if info_oficial else nascimento)
                                if not dados_extraidos_pdf.get("endereco"):
                                    dados_extraidos_pdf["endereco"] = (info_oficial.get("endereco") if info_oficial else endereco)

                                dados_extraidos_pdf["status"] = "CONCLUIDO_P2"
                                dados_extraidos_pdf["protocolo"] = protocolo

                                inseriu = planilha.adicionar_registro(dados_extraidos_pdf)
                                if not inseriu:
                                    planilha.atualizar_status_registro(
                                        cpf=dados_extraidos_pdf["cpf"],
                                        novo_status="CONCLUIDO_P2",
                                        observacao="Atualizado para novo ciclo de cadastro"
                                    )

                                print(f"    [PLANILHA MESTRA] Dados registrados para CPF {dados_extraidos_pdf['cpf']} com status CONCLUIDO_P2.")
                                gestor_erp.arquivar_documento(p_anexo.name, pasta_origem="Documentos_OK")
                            except Exception as e_proc2:
                                print(f"    [ERRO EXTRAÇÃO PDF / PLANILHA] {e_proc2}")

    # =========================================================================
    # FASE 3: CADASTRO NO ERP PORTAL FAKE LENDO A PLANILHA MESTRA (PROCESSO 3)
    # =========================================================================
    if modo in ["cadastro", "processo3", "processar_retornos", "demo_completo"]:
        print("\n" + "-" * 60)
        print(f"[FASE 3] CADASTRO NO ERP PORTAL FAKE LENDO A PLANILHA MESTRA ({caminho_planilha.name})")
        print("-" * 60)

        res_p3 = executar_processo3(
            caminho_planilha=caminho_planilha,
            headless=headless,
            maestro=maestro,
            task_id=task_id,
            cpf=cpf_filtro,
            zerar_base=zerar_base
        )

        cadastrados = res_p3.get("cadastrados", [])
        duplicados = res_p3.get("duplicados", [])
        erros = res_p3.get("erros", [])

        print(f"\n[FASE 3 - RESUMO] Cadastrados: {len(cadastrados)} | Duplicados: {len(duplicados)} | Erros: {len(erros)}")

        # Envia e-mails de confirmação final para os clientes cadastrados
        for c in cadastrados:
            em = c.get("email") or email_cliente
            print(f"    [FASE 3] Enviando e-mail de CONFIRMAÇÃO DE CADASTRO para {em} ({c.get('nome_completo')})...")
            notificador.enviar_resposta(
                email_destino=em,
                protocolo=protocolo,
                aprovado=True
            )

        for d in duplicados:
            print(f"    [FASE 3] Cliente {d.get('nome_completo')} (CPF: {d.get('cpf')}) já cadastrado previamente.")

        for err in erros:
            print(f"    [FASE 3] Falha no cadastro de {err.get('nome_completo')}: {err.get('motivo')}")

    # =========================================================================
    # FASE 4: PROCESSAMENTO DE SAC E COMUNICAÇÃO DE ATENDIMENTO (PROCESSO 4)
    # =========================================================================
    if modo in ["sac", "processo4", "demo_completo", "completo"]:
        print("\n" + "-" * 60)
        print(f"[FASE 4] PROCESSAMENTO DE SAC E ATENDIMENTO AO CLIENTE (PROCESSO 4)")
        print("-" * 60)

        caminho_sac = gestor_erp.dir_sistema_integrador / "atendimentos_sac.xlsx"
        res_sac = executar_processo_sac(
            caminho_planilha_mestra=caminho_planilha,
            caminho_planilha_sac=caminho_sac
        )
        print(f"  [FASE 4 - RESUMO] SAC Concluído: {res_sac.get('total_processados', 0)} registros processados / registrados em '{caminho_sac.name}'.")

    # =========================================================================
    # FASE 5: CONSOLIDAÇÃO, MÉTRICAS E RELATÓRIO GERENCIAL (PROCESSO 5)
    # =========================================================================
    if modo in ["relatorios", "processo5", "demo_completo", "completo"]:
        print("\n" + "-" * 60)
        print(f"[FASE 5] CONSOLIDAÇÃO DE DADOS, MÉTRICAS E RELATÓRIO GERENCIAL (PROCESSO 5)")
        print("-" * 60)

        caminho_sac = gestor_erp.dir_sistema_integrador / "atendimentos_sac.xlsx"
        dir_relatorios = gestor_erp.base_dir / "Relatorios_Gerenciais"

        res_p5 = executar_processo5(
            caminho_planilha_mestra=caminho_planilha,
            caminho_planilha_sac=caminho_sac,
            dir_saida=dir_relatorios
        )

        if res_p5.get("sucesso"):
            rel_info = res_p5.get("relatorios", {})
            kpi_cad = res_p5.get("metricas", {}).get("kpis_cadastro_processo3", {})
            kpi_sac = res_p5.get("metricas", {}).get("kpis_sac_processo4", {})
            kpi_efi = res_p5.get("metricas", {}).get("kpis_eficiencia_global", {})

            print(f"\n[FASE 5 - RESUMO EXECUTIVO]")
            print(f"  -> Total de Clientes Consolidados: {res_p5.get('total_clientes', 0)}")
            print(f"  -> Cadastros Aprovados no Portal : {kpi_cad.get('cadastrados_com_sucesso', 0)} ({kpi_cad.get('taxa_aprovacao_percentual', 0)}%)")
            print(f"  -> Atendimentos SAC Comunicados  : {kpi_sac.get('comunicados_com_sucesso', 0)} ({kpi_sac.get('taxa_sucesso_comunicacao_percentual', 0)}%)")
            print(f"  -> Eficiência da Esteira Global  : {kpi_efi.get('taxa_conclusao_ponta_a_ponta_percentual', 0)}% [{kpi_efi.get('eficiencia_esteira', 'N/A')}]")
            if "excel" in rel_info:
                print(f"  [ARQUIVO] Relatório Excel    : {Path(rel_info['excel']).name}")
            if "markdown" in rel_info:
                print(f"  [ARQUIVO] Relatório Markdown : {Path(rel_info['markdown']).name}")
            if "json" in rel_info:
                print(f"  [ARQUIVO] Relatório JSON     : {Path(rel_info['json']).name}")
        else:
            print(f"  [FASE 5 - AVISO] Falha na geração do relatório: {res_p5.get('erro')}")

    print("\n" + "=" * 75)
    print("ORQUESTRAÇÃO HYPERAUTOMATION FINALIZADA COM SUCESSO!")
    print("=" * 75)


if __name__ == "__main__":
    main()
