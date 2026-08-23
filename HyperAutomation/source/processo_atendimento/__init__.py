"""
Módulo do Processo de Atendimento ao Cliente.
"""
from .gestor_arquivos import GestorArquivos
from .resposta_cliente import NotificadorCliente
from .leitor_email import LeitorEmail
from .validador_docs import ValidadorDocumentos
from .portal_integracao import PortalIntegracao
from .processo_sac import (
    ProcessoSAC,
    RegistroAtendimento,
    ErroPlanilhaMestra,
    executar_processo_sac,
    enviar_comunicacao,
    criar_mensagem
)

__all__ = [
    "GestorArquivos",
    "NotificadorCliente",
    "LeitorEmail",
    "ValidadorDocumentos",
    "PortalIntegracao",
    "ProcessoSAC",
    "RegistroAtendimento",
    "ErroPlanilhaMestra",
    "executar_processo_sac",
    "enviar_comunicacao",
    "criar_mensagem"
]
