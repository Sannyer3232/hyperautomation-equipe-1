"""
Testes Automatizados - Orquestrador Integrado
Valida a leitura direta do CSV para envio de ficha e a execução do cadastro via Planilha Mestra.
"""
import sys
import pytest
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent / "HyperAutomation" / "source"
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR.parent / "resources"))

from orquestrador import executar_orquestracao
from portal_bot import carregar_usuarios, CSV_PATH
from processo_organizacao.planilha_mestra import GerenciadorPlanilha


class TestOrquestradorIntegrado:
    """Testes de ponta a ponta e unitários do novo fluxo do orquestrador."""

    def test_leitura_direta_csv(self):
        """Verifica se o CSV de 20 cadastros é carregado diretamente e com os campos esperados."""
        usuarios = carregar_usuarios(CSV_PATH)
        assert len(usuarios) == 20
        assert usuarios[0]["nome"] == "Ana"
        assert usuarios[0]["cpf"] == "10000012482"
        assert usuarios[1]["nome"] == "Bruno"
        assert usuarios[2]["nome"] == "Carla"

    def test_escolha_cliente_por_row_index(self):
        """Verifica se a seleção do cliente por row_index escolhe o registro correto."""
        usuarios = carregar_usuarios(CSV_PATH)
        # row_index = 2 -> Carla Almeida
        idx = min(max(0, 2), len(usuarios) - 1)
        assert usuarios[idx]["nome"] == "Carla"
        assert usuarios[idx]["sobrenome"] == "Almeida"

        # row_index = 7 -> Sannyer Nery
        idx_7 = min(max(0, 7), len(usuarios) - 1)
        assert usuarios[idx_7]["nome"] == "Sannyer"
        assert usuarios[idx_7]["cpf"] == "03536054250"

    @patch("orquestrador.NotificadorCliente")
    @patch("orquestrador.criar_documento")
    def test_fase1_envio_solicitacao_direto_csv(self, mock_criar_doc, mock_notificador_cls):
        """Valida que a Fase 1 lê do CSV e gera a ficha sem abrir navegador."""
        mock_notificador = MagicMock()
        mock_notificador_cls.return_value = mock_notificador
        mock_criar_doc.return_value = "/tmp/fake_ficha.docx"

        executar_orquestracao(
            modo="enviar_solicitacoes",
            row_index=2,
            email_destino="teste@ifam.edu.br",
            headless=True
        )

        mock_criar_doc.assert_called_once()
        args_doc = mock_criar_doc.call_args[0][0]
        assert args_doc["Nome"] == "Carla"
        assert args_doc["Sobrenome"] == "Almeida"
        assert args_doc["CPF"] == "10000012756"

        mock_notificador.enviar_solicitacao_assinatura.assert_called_once()

    @patch("orquestrador.NotificadorCliente")
    @patch("orquestrador.executar_processo3")
    @patch("orquestrador.LeitorEmail")
    @patch("orquestrador.ValidadorDocumentos")
    def test_fase3_cadastro_via_planilha_mestra(self, mock_validador_cls, mock_leitor_cls, mock_exec_p3, mock_notificador_cls):
        """Valida que a Fase 3 executa o cadastro lendo da Planilha Mestra."""
        mock_notificador = MagicMock()
        mock_notificador_cls.return_value = mock_notificador

        mock_leitor = MagicMock()
        mock_leitor.ler_emails_pendentes.return_value = []
        mock_leitor_cls.return_value = mock_leitor

        mock_exec_p3.return_value = {
            "sucesso": True,
            "total_processados": 1,
            "cadastrados": [{
                "nome_completo": "Carla Almeida",
                "cpf": "10000012756",
                "email": "carla.almeida@email.com",
                "status_cadastro": "CADASTRADO"
            }],
            "duplicados": [],
            "erros": []
        }

        executar_orquestracao(
            modo="processar_retornos",
            row_index=2,
            email_destino="teste@ifam.edu.br",
            headless=True
        )

        mock_exec_p3.assert_called_once()
        # Verifica se o caminho da planilha foi passado para o processo 3
        kwargs_p3 = mock_exec_p3.call_args[1]
        assert "Planilha_Mestra.xlsx" in str(kwargs_p3["caminho_planilha"])
