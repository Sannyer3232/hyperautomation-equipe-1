"""
Testes Automatizados - Processo 3 (Cadastro)
Validação de regras de negócio, sanitização, leitor da Planilha Mestra, logs e orquestração.
"""
import sys
import pytest
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

# Adiciona diretórios do projeto ao path
BASE_DIR = Path(__file__).resolve().parent.parent / "HyperAutomation" / "source"
sys.path.append(str(BASE_DIR))

from processo_cadastro.validador_cadastro import ValidadorCadastro
from processo_cadastro.leitor_planilha import LeitorPlanilhaCadastro
from processo_cadastro.logger_cadastro import LoggerCadastro
from processo_cadastro.orquestrador_cadastro import OrquestradorCadastro, executar_processo3
from processo_cadastro.integrador_portal import CadastradorPortalFake
from processo_organizacao.planilha_mestra import GerenciadorPlanilha


class TestValidadorCadastro:
    """Testes unitários do Validador de Regras de Negócio e Dados."""

    def test_sanitizacao_cpf(self):
        assert ValidadorCadastro.sanitizar_cpf("123.456.789-00") == "12345678900"
        assert ValidadorCadastro.sanitizar_cpf("12345678900") == "12345678900"
        assert ValidadorCadastro.sanitizar_cpf("3536054250") == "03536054250"
        assert ValidadorCadastro.sanitizar_cpf("") == ""

    def test_validacao_cpf_valido(self):
        valido, msg = ValidadorCadastro.validar_cpf("035.360.542-50")
        assert valido is True
        assert "válido" in msg.lower()

    def test_validacao_cpf_invalido(self):
        # Menos de 11 dígitos
        valido, msg = ValidadorCadastro.validar_cpf("12345")
        assert valido is False

        # Dígitos todos iguais
        valido_iguais, _ = ValidadorCadastro.validar_cpf("11111111111")
        assert valido_iguais is False

        # Vazio
        valido_vazio, _ = ValidadorCadastro.validar_cpf("")
        assert valido_vazio is False

    def test_validacao_email(self):
        assert ValidadorCadastro.validar_email("cliente@exemplo.com") is True
        assert ValidadorCadastro.validar_email("invalido@") is False
        assert ValidadorCadastro.validar_email("sem_arroba.com") is False
        assert ValidadorCadastro.validar_email("") is False

    def test_validacao_cliente_completo(self):
        cliente_valido = {
            "nome": "Sannyer",
            "sobrenome": "Nery",
            "cpf": "03536054250",
            "email": "sannyer.nery@email.com",
        }
        valido, erros = ValidadorCadastro.validar_dados_cliente(cliente_valido)
        assert valido is True
        assert len(erros) == 0

    def test_validacao_cliente_invalido(self):
        cliente_sem_nome = {
            "nome": "",
            "sobrenome": "",
            "cpf": "123",
            "email": "invalido",
        }
        valido, erros = ValidadorCadastro.validar_dados_cliente(cliente_sem_nome)
        assert valido is False
        assert len(erros) >= 2


class TestLeitorPlanilhaCadastro:
    """Testes de preparação e normalização de registros da Planilha Mestra."""

    @pytest.fixture
    def planilha_temp(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
            temp_path = Path(tf.name)
        temp_path.unlink(missing_ok=True)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_preparacao_dados_completos(self):
        leitor = LeitorPlanilhaCadastro()
        registro_bruto = {
            "linha": 2,
            "nome_completo": "Ana Paula Silva",
            "cpf": "12345678901",
            "email": "ana.silva@teste.com",
            "telefone": "(92) 99111-2233",
            "nascimento": "1990-08-20",
            "endereco": "Rua Principal, 100",
            "status": "CONCLUIDO_P2",
            "observacoes": "Processado no P2",
        }
        preparado = leitor._preparar_dados_cliente(registro_bruto)

        assert preparado["nome"] == "Ana"
        assert preparado["sobrenome"] == "Paula Silva"
        assert preparado["cpf"] == "12345678901"
        assert preparado["email"] == "ana.silva@teste.com"
        assert preparado["status_portal"] == "ATIVO"

    def test_preparacao_dados_com_fallbacks(self):
        leitor = LeitorPlanilhaCadastro()
        registro_incompleto = {
            "linha": 5,
            "nome_completo": "Carlos",
            "cpf": "99887766554",
            "email": "",  # Sem email -> deve gerar fallback
            "telefone": "",
            "nascimento": "",
            "endereco": "",
            "status": "CONCLUIDO_P2",
            "observacoes": "",
        }
        preparado = leitor._preparar_dados_cliente(registro_incompleto)

        assert preparado["nome"] == "Carlos"
        assert "@email.com" in preparado["email"]
        assert preparado["nascimento"] == "1995-01-01"
        assert preparado["telefone"] != ""

    def test_obter_pendentes_e_todos(self, planilha_temp):
        gerenciador = GerenciadorPlanilha(planilha_temp)
        gerenciador.inicializar_planilha()
        gerenciador.adicionar_registro({
            "nome_completo": "Cliente P2",
            "cpf": "12345678900",
            "email": "p2@teste.com",
            "status": "CONCLUIDO_P2"
        })
        gerenciador.adicionar_registro({
            "nome_completo": "Cliente P3",
            "cpf": "98765432100",
            "email": "p3@teste.com",
            "status": "CONCLUIDO_P3"
        })

        leitor = LeitorPlanilhaCadastro(planilha_temp)
        pendentes = leitor.obter_clientes_pendentes(status_filtro=["CONCLUIDO_P2"])
        assert len(pendentes) == 1
        assert pendentes[0]["cpf"] == "12345678900"

        todos = leitor.obter_todos_clientes()
        assert len(todos) == 2


class TestGerenciadorPlanilhaMestra:
    """Testes com arquivo temporário da Planilha Mestra."""

    @pytest.fixture
    def planilha_temp(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
            temp_path = Path(tf.name)
        temp_path.unlink(missing_ok=True)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_ciclo_leitura_e_atualizacao(self, planilha_temp):
        gerenciador = GerenciadorPlanilha(planilha_temp)
        gerenciador.inicializar_planilha()

        # Insere registro simulado do P2
        sucesso = gerenciador.adicionar_registro({
            "nome_completo": "Testador Automatizado",
            "cpf": "11122233344",
            "email": "testador@rpa.com",
            "telefone": "(92) 99999-8888",
            "endereco": "Rua dos Testes, 1",
            "status": "CONCLUIDO_P2",
            "observacoes": "Inserido para teste",
        })
        assert sucesso is True

        # Lê registros com filtro de status
        registros_p2 = gerenciador.ler_registros(status_filtro="CONCLUIDO_P2")
        assert len(registros_p2) == 1
        assert registros_p2[0]["cpf"] == "11122233344"
        assert registros_p2[0]["status"] == "CONCLUIDO_P2"

        # Atualiza status para CONCLUIDO_P3
        atualizou = gerenciador.atualizar_status_registro(
            cpf="11122233344",
            novo_status="CONCLUIDO_P3",
            observacao="Cadastro realizado com sucesso via Processo 3"
        )
        assert atualizou is True

        # Confirma que não está mais como P2 e sim como P3
        registros_p2_pos = gerenciador.ler_registros(status_filtro="CONCLUIDO_P2")
        assert len(registros_p2_pos) == 0

        registros_p3 = gerenciador.ler_registros(status_filtro="CONCLUIDO_P3")
        assert len(registros_p3) == 1
        assert "Processo 3" in registros_p3[0]["observacoes"]


class TestLoggerCadastro:
    """Testes do sistema de logs estruturado."""

    def test_registro_logs(self, tmp_path):
        logger = LoggerCadastro(log_dir=tmp_path)
        logger.info("Teste de info")
        logger.sucesso("Teste de sucesso")
        logger.duplicado("Teste duplicado")
        logger.aviso("Teste de aviso")
        logger.erro("Teste de erro", erro="Erro simulado")
        logger.fallback("Teste de fallback")

        assert logger.log_file.exists()
        conteudo = logger.log_file.read_text(encoding="utf-8")
        assert "PROCESSO 3 - CADASTRO" in conteudo
        assert "Teste de sucesso" in conteudo
        assert "Erro simulado" in conteudo


class TestOrquestradorCadastro:
    """Testes de fluxo da orquestração do Processo 3 com mocks e validações."""

    @pytest.fixture
    def planilha_vazia(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tf:
            temp_path = Path(tf.name)
        temp_path.unlink(missing_ok=True)
        gp = GerenciadorPlanilha(temp_path)
        gp.inicializar_planilha()
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_orquestrador_sem_clientes_pendentes(self, planilha_vazia):
        orquestrador = OrquestradorCadastro(caminho_planilha=planilha_vazia)
        resultado = orquestrador.executar(headless=True)
        assert resultado["sucesso"] is True
        assert resultado["total_processados"] == 0
        assert len(resultado["resultados"]) == 0

    def test_orquestrador_fluxo_com_mock(self, planilha_vazia):
        # Adiciona registros: 1 novo, 1 duplicado, 1 com dados inválidos
        gp = GerenciadorPlanilha(planilha_vazia)
        gp.adicionar_registro({
            "nome_completo": "Novo Cliente",
            "cpf": "11122233300",
            "email": "novo@teste.com",
            "status": "CONCLUIDO_P2"
        })
        gp.adicionar_registro({
            "nome_completo": "Cliente Duplicado",
            "cpf": "22233344400",
            "email": "dup@teste.com",
            "status": "CONCLUIDO_P2"
        })

        orquestrador = OrquestradorCadastro(caminho_planilha=planilha_vazia)

        # Mock dos métodos de Playwright no portal
        mock_page = MagicMock()
        with patch.object(orquestrador.portal, "navegar_ao_portal"), \
             patch.object(orquestrador.portal, "capturar_screenshot", return_value=None), \
             patch.object(orquestrador.portal, "limpar_filtros"), \
             patch.object(orquestrador.portal, "consultar_cpf") as mock_consultar, \
             patch.object(orquestrador.portal, "cadastrar_cliente") as mock_cadastrar:

            # Define retornos simulados
            def side_effect_consultar(page, cpf):
                if cpf == "11122233300":
                    return {"existe": False, "total": 0}
                else:
                    return {"existe": True, "total": 1}

            mock_consultar.side_effect = side_effect_consultar
            mock_cadastrar.return_value = {
                "sucesso": True,
                "status": "CADASTRADO",
                "mensagem": "Cadastrado com sucesso"
            }

            resultado = orquestrador.executar(headless=True, page=mock_page)

            assert resultado["sucesso"] is True
            assert resultado["total_processados"] == 2
            assert len(resultado["cadastrados"]) == 1
            assert len(resultado["duplicados"]) == 1
            assert resultado["cadastrados"][0]["cpf"] == "11122233300"
            assert resultado["duplicados"][0]["cpf"] == "22233344400"

            # Confirma que a planilha foi atualizada
            regs_p3 = gp.ler_registros(status_filtro="CONCLUIDO_P3")
            regs_dup = gp.ler_registros(status_filtro="DUPLICADO_P3")
            assert len(regs_p3) == 1
            assert len(regs_dup) == 1
