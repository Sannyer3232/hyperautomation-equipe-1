"""
Módulo Orquestrador do Processo 3 - Cadastro
Coordena leitura da Planilha Mestra, validação, verificação de duplicidades, cadastro web no Portal Fake,
atualização dos status na planilha e retorno estruturado para o Processo 4 (SAC).
"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parents[1]
PATH_ROOT = BASE_DIR.parent
BROWSER_DATA_DIR = PATH_ROOT / "resources" / "browser_data"

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from processo_organizacao.planilha_mestra import GerenciadorPlanilha
from .logger_cadastro import LoggerCadastro
from .validador_cadastro import ValidadorCadastro
from .leitor_planilha import LeitorPlanilhaCadastro
from .integrador_portal import CadastradorPortalFake


class OrquestradorCadastro:
    """
    Orquestrador responsável pela execução do Processo 3 (Cadastro).
    Integração: Processo 2 (Planilha Mestra) → Consulta/Validação → Cadastro → Registro de Resultados → Processo 4 (SAC).
    """

    def __init__(self, caminho_planilha: Path = None):
        self.leitor = LeitorPlanilhaCadastro(caminho_planilha)
        self.caminho_planilha = self.leitor.caminho_planilha
        self.gerenciador_planilha = GerenciadorPlanilha(self.caminho_planilha)
        self.validador = ValidadorCadastro()
        self.portal = CadastradorPortalFake()
        self.logger = LoggerCadastro()

    def executar(self, headless: bool = False, page = None, context = None, maestro = None, task_id = None, cpf: str = None, linha: int = None, zerar_base: bool = False) -> dict:
        """
        Executa o fluxo completo do Processo 3:
        1. Consulta e extrai registros pendentes da Planilha Mestra (ou um registro específico se informado CPF/linha)
        2. Inicia/conecta ao Portal Fake ERP via Playwright
        3. Realiza validação prévia de dados
        4. Consulta e trata duplicidades de CPF
        5. Efetua o cadastro dos novos clientes
        6. Atualiza o status consolidado na Planilha Mestra
        7. Captura evidências e retorna o payload preparado para o Processo 4 (SAC)
        """
        print("=" * 75)
        print("INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION - PROCESSO 3 (Cadastro)")
        print("=" * 75)
        self.logger.info("Iniciando orquestração do Processo 3 - Cadastro.")

        # 1. Leitura dos clientes da Planilha Mestra (específico ou pendentes)
        print(f"\n[Etapa 1] Carregando registros da Planilha Mestra em: {self.caminho_planilha.name}")
        if cpf:
            cliente_especifico = self.leitor.obter_cliente_por_cpf(cpf)
            clientes_pendentes = [cliente_especifico] if cliente_especifico else []
            if cliente_especifico:
                print(f"[PROCESSO 3] Filtrando exclusivamente pelo CPF: '{cpf}' (Linha {cliente_especifico.get('linha')})")
        elif linha:
            cliente_especifico = self.leitor.obter_cliente_por_linha(linha)
            clientes_pendentes = [cliente_especifico] if cliente_especifico else []
            if cliente_especifico:
                print(f"[PROCESSO 3] Filtrando exclusivamente pela Linha: {linha} (CPF: {cliente_especifico.get('cpf')})")
        else:
            clientes_pendentes = self.leitor.obter_clientes_pendentes(
                status_filtro=[
                    "CONCLUIDO_P2", "APROVADO", "APROVADA", "APROVADOS", "APROVADAS",
                    "PENDENTE_CADASTRO", "PENDENTE", "DOCUMENTOS_OK", "DOCS_OK", "VALIDADO"
                ]
            )

        if not clientes_pendentes:
            msg_filtro = f" para o filtro informado (CPF: {cpf}, Linha: {linha})" if (cpf or linha) else ""
            print(f"[PROCESSO 3] Nenhum registro pendente de cadastro encontrado na Planilha Mestra{msg_filtro}.")
            self.logger.aviso(f"Nenhum registro encontrado na Planilha Mestra{msg_filtro}.")
            return {
                "sucesso": True,
                "total_processados": 0,
                "cadastrados": [],
                "duplicados": [],
                "erros": [],
                "resultados": []
            }

        print(f"[Etapa 1] {len(clientes_pendentes)} registro(s) identificado(s) para cadastro.\n")
        self.logger.info(f"Identificados {len(clientes_pendentes)} clientes para processar na Planilha Mestra.")

        # 2. Execução da Automação Web via Playwright
        fechar_navegador_ao_final = False
        playwright_instance = None

        resultados = []
        cadastrados = []
        duplicados = []
        erros = []

        try:
            if page is None:
                playwright_instance = sync_playwright().start()
                try:
                    context = playwright_instance.chromium.launch_persistent_context(
                        user_data_dir=str(BROWSER_DATA_DIR),
                        headless=headless
                    )
                except Exception as e_launch:
                    self.logger.aviso(f"Fallback para navegador isolado sem persistência: {e_launch}")
                    browser = playwright_instance.chromium.launch(headless=headless)
                    context = browser.new_context()

                page = context.new_page()
                fechar_navegador_ao_final = True

            # Conecta e garante acesso ao Portal Fake
            print("[Etapa 2] Conectando ao ERP Portal Fake...")
            self.portal.navegar_ao_portal(page)

            if zerar_base:
                self.portal.zerar_base(page)

            # 3. Processamento de cada cliente da planilha
            for idx, cliente in enumerate(clientes_pendentes, start=1):
                nome = cliente["nome"]
                sobrenome = cliente["sobrenome"]
                nome_completo = cliente["nome_completo"]
                cpf = cliente["cpf"]
                email = cliente["email"]
                linha = cliente["linha"]

                print("-" * 65)
                print(f"[Cliente {idx}/{len(clientes_pendentes)}] Processando: {nome_completo} | CPF: {cpf}")
                self.logger.info(f"Processando cadastro para {nome_completo} (CPF: {cpf}, Linha {linha})")

                # a) Validação de regras de negócio
                valido, motivos_erro = self.validador.validar_dados_cliente(cliente)
                if not valido:
                    erro_msg = "; ".join(motivos_erro)
                    print(f"  [VALIDAÇÃO] Dados inválidos para {nome_completo}: {erro_msg}")
                    self.logger.erro(f"Validação falhou para {nome_completo}", erro=erro_msg)

                    self.gerenciador_planilha.atualizar_status_registro(
                        cpf=cpf,
                        linha=linha,
                        novo_status="ERRO_VALIDACAO_P3",
                        observacao=f"Dados rejeitados na validação: {erro_msg}"
                    )

                    res_item = {
                        "cpf": cpf,
                        "nome_completo": nome_completo,
                        "email": email,
                        "telefone": cliente.get("telefone", ""),
                        "status_cadastro": "ERRO_VALIDACAO",
                        "sucesso": False,
                        "motivo": erro_msg,
                        "observacoes": cliente.get("observacoes", "")
                    }
                    erros.append(res_item)
                    resultados.append(res_item)
                    continue

                # b) Consulta prévia de duplicidade no Portal Fake
                print(f"  [CONSULTA] Verificando existência prévia do CPF '{cpf}' no portal...")
                res_consulta = self.portal.consultar_cpf(page, cpf)

                if res_consulta.get("existe"):
                    print(f"  [DUPLICIDADE] CPF '{cpf}' já consta cadastrado no Portal Fake.")
                    self.logger.duplicado(f"CPF {cpf} ({nome_completo}) já existe no portal.")

                    self.gerenciador_planilha.atualizar_status_registro(
                        cpf=cpf,
                        linha=linha,
                        novo_status="DUPLICADO_P3",
                        observacao="CPF já cadastrado previamente no Portal Fake"
                    )

                    res_item = {
                        "cpf": cpf,
                        "nome_completo": nome_completo,
                        "email": email,
                        "telefone": cliente.get("telefone", ""),
                        "status_cadastro": "DUPLICADO",
                        "sucesso": True,
                        "motivo": "CPF já cadastrado no portal",
                        "observacoes": cliente.get("observacoes", "")
                    }
                    duplicados.append(res_item)
                    resultados.append(res_item)
                    continue

                # c) Execução do cadastro no formulário do portal
                print(f"  [CADASTRO] Preenchendo ficha e submetendo cadastro no portal...")
                res_cadastro = self.portal.cadastrar_cliente(page, cliente)

                if res_cadastro.get("sucesso"):
                    print(f"  [SUCESSO] Cliente {nome_completo} cadastrado com sucesso no portal.")
                    self.logger.sucesso(f"Cadastro concluído no portal para {nome_completo} (CPF: {cpf}).")

                    self.gerenciador_planilha.atualizar_status_registro(
                        cpf=cpf,
                        linha=linha,
                        novo_status="CONCLUIDO_P3",
                        observacao="Cadastrado com sucesso no Portal Fake via RPA"
                    )

                    res_item = {
                        "cpf": cpf,
                        "nome_completo": nome_completo,
                        "email": email,
                        "telefone": cliente.get("telefone", ""),
                        "status_cadastro": "CADASTRADO",
                        "sucesso": True,
                        "motivo": "Cadastro realizado com sucesso",
                        "observacoes": cliente.get("observacoes", "")
                    }
                    cadastrados.append(res_item)
                    resultados.append(res_item)
                else:
                    # d) Fallback em caso de rejeição no portal
                    motivo_falha = res_cadastro.get("mensagem", "Erro desconhecido ao salvar")
                    print(f"  [FALLBACK] Falha no cadastro de {nome_completo}: {motivo_falha}")
                    self.logger.fallback(f"Falha ao cadastrar {nome_completo}", motivo=motivo_falha)

                    novo_st = "DUPLICADO_P3" if res_cadastro.get("status") == "DUPLICADO" else "ERRO_CADASTRO_P3"
                    self.gerenciador_planilha.atualizar_status_registro(
                        cpf=cpf,
                        linha=linha,
                        novo_status=novo_st,
                        observacao=f"Falha no portal: {motivo_falha}"
                    )

                    res_item = {
                        "cpf": cpf,
                        "nome_completo": nome_completo,
                        "email": email,
                        "telefone": cliente.get("telefone", ""),
                        "status_cadastro": res_cadastro.get("status", "ERRO"),
                        "sucesso": False,
                        "motivo": motivo_falha,
                        "observacoes": cliente.get("observacoes", "")
                    }
                    if res_cadastro.get("status") == "DUPLICADO":
                        duplicados.append(res_item)
                    else:
                        erros.append(res_item)
                    resultados.append(res_item)

            # 4. Finalização e Evidências
            self.portal.limpar_filtros(page)
            print("\n[Etapa 4] Capturando screenshot de evidência do Portal Fake...")
            print_p3 = self.portal.capturar_screenshot(page, "03_processo3_cadastros_concluidos.png")

            if maestro and maestro.is_online and task_id and print_p3:
                try:
                    maestro.post_artifact(task_id=task_id, artifact_name=print_p3.name, filepath=str(print_p3))
                except Exception:
                    pass

        except Exception as e:
            self.logger.erro("Falha crítica durante a execução do Processo 3", erro=str(e))
            print(f"[ERRO CRÍTICO PROCESSO 3] {e}")
            raise e

        finally:
            if fechar_navegador_ao_final:
                try:
                    context.close()
                    if playwright_instance:
                        playwright_instance.stop()
                except Exception:
                    pass

        print("\n" + "=" * 75)
        print("ORQUESTRAÇÃO DO PROCESSO 3 FINALIZADA COM SUCESSO!")
        print(f"Total Processados: {len(resultados)} | Novos Cadastrados: {len(cadastrados)} | Duplicados: {len(duplicados)} | Erros: {len(erros)}")
        print("=" * 75)

        self.logger.sucesso(
            f"Processo 3 concluído. Total: {len(resultados)} (Cadastrados: {len(cadastrados)}, Duplicados: {len(duplicados)}, Erros: {len(erros)})"
        )

        return {
            "sucesso": True,
            "total_processados": len(resultados),
            "cadastrados": cadastrados,
            "duplicados": duplicados,
            "erros": erros,
            "resultados": resultados  # Payload estruturado para o Processo 4 (SAC)
        }


def executar_processo3(caminho_planilha: Path = None, headless: bool = False, page = None, context = None, maestro = None, task_id = None, cpf: str = None, linha: int = None, zerar_base: bool = False) -> dict:
    """Função utilitária para disparo direto do Processo 3."""
    orquestrador = OrquestradorCadastro(caminho_planilha)
    return orquestrador.executar(headless=headless, page=page, context=context, maestro=maestro, task_id=task_id, cpf=cpf, linha=linha, zerar_base=zerar_base)
