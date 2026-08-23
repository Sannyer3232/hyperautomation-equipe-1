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

    @patch("orquestrador.carregar_usuarios")
    @patch("orquestrador.executar_processo3")
    def test_modo_cadastro_nao_le_csv(self, mock_exec_p3, mock_carregar_csv):
        """Valida que o modo cadastro NÃO lê o CSV e chama diretamente o Processo 3."""
        mock_exec_p3.return_value = {
            "sucesso": True,
            "total_processados": 1,
            "cadastrados": [],
            "duplicados": [],
            "erros": []
        }

        executar_orquestracao(modo="cadastro", headless=True)

        mock_carregar_csv.assert_not_called()
        mock_exec_p3.assert_called_once()

    @patch("processo_organizacao.extrator_dados.PdfReader")
    def test_extracao_data_nascimento_formatos(self, mock_pdf_reader, tmp_path):
        """Valida que o ExtratorPDF extrai e normaliza corretamente diferentes formatos de data de nascimento."""
        fake_pdf = tmp_path / "fake.pdf"
        fake_pdf.write_text("dummy")

        mock_page = MagicMock()
        mock_page.extract_text.return_value = (
            "PORTAL FAKE SOLUCOES DIGITAIS\n"
            "FICHA DE CADASTRO\n"
            "1. Nome: Sannyer\n"
            "2. Sobrenome: Nery\n"
            "3. CPF: 03536054250\n"
            "4. E-mail: sannyer@teste.com\n"
            "5. Telefone: (92) 99982-7524\n"
            "6. Data de Nascimento: 1999-11-15\n"
            "7. Endereço: Rua Rio Purus, 915 - Manaus/AM\n"
        )
        mock_reader_inst = MagicMock()
        mock_reader_inst.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader_inst

        from processo_organizacao.extrator_dados import ExtratorPDF
        extrator = ExtratorPDF(fake_pdf)
        dados = extrator.extrair_dados()

        assert dados["nascimento"] == "1999-11-15"
        assert dados["cpf"] == "03536054250"
        assert dados["nome_completo"] == "Sannyer Nery"
        assert dados["email"] == "sannyer@teste.com"

    @patch("orquestrador.executar_processo_sac")
    def test_modo_sac_executa_processo_sac(self, mock_exec_sac):
        """Valida que o modo sac chama diretamente o Processo 4 (SAC)."""
        mock_exec_sac.return_value = {
            "sucesso": True,
            "total_processados": 3,
            "total_registros": 3
        }

        executar_orquestracao(modo="sac", headless=True)

        mock_exec_sac.assert_called_once()
        kwargs_sac = mock_exec_sac.call_args[1]
        assert "Planilha_Mestra.xlsx" in str(kwargs_sac["caminho_planilha_mestra"])
        assert "atendimentos_sac.xlsx" in str(kwargs_sac["caminho_planilha_sac"])

    @patch("orquestrador.executar_processo5")
    def test_modo_relatorios_executa_processo5(self, mock_exec_p5):
        """Valida que o modo relatorios chama diretamente o Processo 5."""
        mock_exec_p5.return_value = {
            "sucesso": True,
            "total_clientes": 5,
            "metricas": {},
            "relatorios": {}
        }

        executar_orquestracao(modo="relatorios", headless=True)

        mock_exec_p5.assert_called_once()
        kwargs_p5 = mock_exec_p5.call_args[1]
        assert "Planilha_Mestra.xlsx" in str(kwargs_p5["caminho_planilha_mestra"])
        assert "atendimentos_sac.xlsx" in str(kwargs_p5["caminho_planilha_sac"])

    @patch("orquestrador.executar_processo5")
    @patch("orquestrador.executar_processo_sac")
    @patch("orquestrador.executar_processo3")
    @patch("orquestrador.LeitorEmail")
    @patch("orquestrador.ValidadorDocumentos")
    @patch("orquestrador.NotificadorCliente")
    @patch("orquestrador.criar_documento")
    @patch("orquestrador.carregar_usuarios")
    def test_modo_demo_completo_executa_todas_as_fases(
        self, mock_carregar_csv, mock_criar_doc, mock_notificador_cls,
        mock_validador_cls, mock_leitor_cls, mock_exec_p3, mock_exec_sac, mock_exec_p5
    ):
        """Valida a execução integrada das 5 fases no modo demo_completo."""
        mock_carregar_csv.return_value = [{
            "id_solicitacao": "1",
            "nome": "Ana",
            "sobrenome": "Silva",
            "cpf": "10000012482",
            "email": "ana@email.com",
            "telefone": "(92) 99888-1122",
            "nascimento": "1995-01-01",
            "endereco": "Manaus/AM"
        }]
        mock_criar_doc.return_value = "/tmp/fake_ficha.docx"
        mock_notificador = MagicMock()
        mock_notificador_cls.return_value = mock_notificador

        mock_leitor = MagicMock()
        mock_leitor.ler_emails_pendentes.return_value = []
        mock_leitor_cls.return_value = mock_leitor

        mock_exec_p3.return_value = {
            "sucesso": True,
            "total_processados": 1,
            "cadastrados": [],
            "duplicados": [],
            "erros": []
        }
        mock_exec_sac.return_value = {
            "sucesso": True,
            "total_processados": 1,
            "total_registros": 1
        }
        mock_exec_p5.return_value = {
            "sucesso": True,
            "total_clientes": 1,
            "metricas": {},
            "relatorios": {}
        }

        executar_orquestracao(modo="demo_completo", row_index=0, headless=True)

        mock_criar_doc.assert_called_once()
        mock_notificador.enviar_solicitacao_assinatura.assert_called_once()
        mock_leitor.ler_emails_pendentes.assert_called_once()
        mock_exec_p3.assert_called_once()
        mock_exec_sac.assert_called_once()
        mock_exec_p5.assert_called_once()



