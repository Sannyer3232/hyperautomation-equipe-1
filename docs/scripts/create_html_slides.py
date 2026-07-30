import os
from pathlib import Path

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Defesa da Solução de Hyperautomation - Processo 1</title>
    <style>
        :root {
            --lg-red: #A50034;
            --lg-dark: #333333;
            --lg-light: #F8F9FA;
            --card-bg: #FFFFFF;
            --card-border: #E2E8F0;
            --accent-blue: #0F4C81;
            --text-grey: #4A5568;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--lg-light); color: var(--lg-dark); overflow: hidden; height: 100vh; }

        .slide-container { width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; }
        .slide { display: none; width: 92vw; height: 88vh; background: var(--card-bg); border-radius: 12px; border: 1px solid var(--card-border); box-shadow: 0 10px 30px rgba(0,0,0,0.08); padding: 30px 40px; flex-direction: column; justify-content: space-between; position: relative; animation: fadeIn 0.3s ease-in-out; }
        .slide.active { display: flex; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* Header */
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--lg-light); padding-bottom: 12px; margin-bottom: 15px; }
        .header-title-box { display: flex; align-items: center; gap: 12px; }
        .red-bar { width: 6px; height: 36px; background-color: var(--lg-red); border-radius: 3px; }
        .category { font-size: 11px; font-weight: 700; color: var(--lg-red); text-transform: uppercase; letter-spacing: 1px; }
        .title { font-size: 22px; font-weight: 700; color: var(--lg-dark); }
        .member-badge { background-color: var(--lg-red); color: white; padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 600; }

        /* Content Layouts */
        .content-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; flex-grow: 1; align-items: stretch; }
        .content-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; flex-grow: 1; align-items: stretch; }
        .content-full { flex-grow: 1; display: flex; flex-direction: column; gap: 12px; }

        .card { background-color: var(--lg-light); border: 1px solid var(--card-border); border-radius: 8px; padding: 18px 22px; display: flex; flex-direction: column; gap: 8px; }
        .card-title { font-size: 16px; font-weight: 700; color: var(--lg-red); border-bottom: 1px solid rgba(165,0,52,0.15); padding-bottom: 6px; margin-bottom: 4px; }
        .card-item { font-size: 13px; line-height: 1.5; color: var(--lg-dark); }
        .card-item strong { color: var(--lg-dark); font-weight: 600; }

        /* Code Block Style */
        .code-box { background-color: var(--lg-dark); color: #F8F9FA; font-family: 'Courier New', Courier, monospace; font-size: 11px; padding: 16px; border-radius: 8px; border-left: 4px solid var(--lg-red); white-space: pre-wrap; line-height: 1.4; flex-grow: 1; overflow-y: auto; }

        /* Table Style */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
        th { background-color: var(--lg-red); color: white; padding: 10px 14px; text-align: left; font-weight: 600; }
        td { padding: 10px 14px; border-bottom: 1px solid var(--card-border); color: var(--lg-dark); }
        tr:nth-child(even) { background-color: var(--lg-light); }

        /* Footer & Controls */
        .footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--card-border); pt: 10px; margin-top: 15px; font-size: 11px; color: var(--text-grey); }
        .controls { position: fixed; bottom: 15px; right: 20px; display: flex; gap: 8px; z-index: 100; }
        .btn { background: var(--lg-red); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 600; }
        .btn:hover { background: #800028; }
        .btn-sec { background: var(--lg-dark); }
    </style>
</head>
<body>
    <div class="slide-container">

        <!-- SLIDE 1: CAPA -->
        <div class="slide active">
            <div style="text-align: center; margin-top: 40px;">
                <div style="color: var(--lg-red); font-weight: 800; font-size: 14px; letter-spacing: 2px;">DISCIPLINA DE TÉCNICAS DE HYPERAUTOMATION | SEMANA 07</div>
                <h1 style="font-size: 34px; color: var(--lg-red); margin: 15px 0 10px 0;">DEFESA DA SOLUÇÃO DE HYPERAUTOMATION</h1>
                <h3 style="font-size: 18px; color: var(--lg-dark); font-weight: 600;">Processo 1: Automação do Setor de Atendimento & Cadastro (Empresa Portal Fake)</h3>
                <p style="color: var(--text-grey); margin-top: 10px; font-size: 14px;">Professor: Prof. Moisés Levy | Apresentação Técnica de 20 Minutos | IFAM / FAEPI / LG</p>
            </div>
            
            <div style="background: var(--lg-light); border: 1px solid var(--card-border); border-radius: 10px; padding: 20px; margin: 20px 0;">
                <div style="font-weight: 700; color: var(--lg-red); font-size: 14px; margin-bottom: 10px;">EQUIPE 1 (INTEGRANTES & INTEGRALIZAÇÃO):</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">
                    <div>• <strong>Eric Luna Costa</strong> — Analista de Processos BPMN & Regras de Negócio</div>
                    <div>• <strong>Daniele Greice A. e Silva</strong> — Desenvolvedora de Automação Core</div>
                    <div>• <strong>Kauã Sales Viana</strong> — Desenvolvedor de Automação Core</div>
                    <div>• <strong>Sannyer Cardoso C. Nery</strong> — DevOps, Versionamento, Arquitetura & Orquestração</div>
                </div>
            </div>

            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 1 de 20</span>
            </div>
        </div>

        <!-- SLIDE 2: AGENDA -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Estrutura da Defesa</div>
                        <div class="title">Agenda da Apresentação Técnica (20 Minutos)</div>
                    </div>
                </div>
                <div class="member-badge">Visão Geral</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">BLOCO 1: Contexto & BPMN (0 a 5 min)</div>
                    <div class="card-item"><strong>Apresentador:</strong> Eric Luna Costa</div>
                    <div class="card-item"><strong>• Contexto do Problema:</strong> Gargalos do atendimento manual no Portal Fake.</div>
                    <div class="card-item"><strong>• Processo AS-IS:</strong> Fluxo operacional antes da automação.</div>
                    <div class="card-item"><strong>• Processo TO-BE:</strong> Modelagem BPMN 2.0 no Draw.io e regras de negócio.</div>
                </div>
                <div class="card">
                    <div class="card-title">BLOCO 2: Arquitetura & Core (5 a 10 min)</div>
                    <div class="card-item"><strong>Apresentadores:</strong> Daniele Greice & Kauã Sales</div>
                    <div class="card-item"><strong>• Stack Tecnológico:</strong> Python 3.10, Playwright, pypdf, BotCity Maestro.</div>
                    <div class="card-item"><strong>• Fases 1 & 2:</strong> Geração de Ficha Word, Envio SMTP e Leitor IMAP.</div>
                    <div class="card-item"><strong>• Fase 3:</strong> Validador documental inteligente de PDFs únicos.</div>
                </div>
                <div class="card">
                    <div class="card-title">BLOCO 3: ERP, Drive & DevOps (10 a 15 min)</div>
                    <div class="card-item"><strong>Apresentador:</strong> Sannyer Cardoso C. Nery</div>
                    <div class="card-item"><strong>• Gestão de Arquivos:</strong> Pastas ERP local e Google Drive API v3.</div>
                    <div class="card-item"><strong>• Solução de Cota:</strong> Suporte OAuth 2.0 / Service Account e DRIVE_FOLDER_ID.</div>
                    <div class="card-item"><strong>• Governança & GitFlow:</strong> Orquestrador central e controle de versão.</div>
                </div>
                <div class="card">
                    <div class="card-title">BLOCO 4: Evidências & Resultados (15 a 20 min)</div>
                    <div class="card-item"><strong>Apresentadores:</strong> Equipe Integrada</div>
                    <div class="card-item"><strong>• Evidências Práticas:</strong> Execution logs do terminal e screenshots do portal.</div>
                    <div class="card-item"><strong>• Tabela de Ganhos:</strong> Comparativo de métricas (Antes vs Depois).</div>
                    <div class="card-item"><strong>• Conclusão & Q&A:</strong> Defesa técnica e resposta a perguntas da banca.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 2 de 20</span>
            </div>
        </div>

        <!-- SLIDE 3: CONTEXTO ORGANIZACIONAL -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 1 — Contexto & BPMN</div>
                        <div class="title">Contexto Organizacional: Empresa Portal Fake</div>
                    </div>
                </div>
                <div class="member-badge">Eric Luna Costa</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">O ERP Simulado da Empresa Portal Fake</div>
                    <div class="card-item"><strong>• Operação Comercial:</strong> A Empresa Portal Fake atua no fornecimento de soluções digitais e cadastramento de novos clientes.</div>
                    <div class="card-item"><strong>• Volume Operacional:</strong> Recebe diariamente solicitações cadastrais que exigem validação de documentos com foto, comprovante de residência e ficha assinada.</div>
                    <div class="card-item"><strong>• Ecossistema Híbrido:</strong> Necessidade de integração entre interface Web (Portal ERP), e-mails corporativos e nuvem.</div>
                </div>
                <div class="card">
                    <div class="card-title">Desafios do Setor de Atendimento</div>
                    <div class="card-item"><strong>• Alta Dependência Manual:</strong> Triagem manual repetitiva e verificação visual de anexos por operadores humanos.</div>
                    <div class="card-item"><strong>• Complexidade de Integração:</strong> Ler e-mails de retorno, extrair anexos, validar PDFs, atualizar dados Web e mover arquivos.</div>
                    <div class="card-item"><strong>• Requisito da Semana 07:</strong> Evoluir a automação existente sem recriar o robô, adicionando o módulo de Atendimento com padrão limpo.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 3 de 20</span>
            </div>
        </div>

        <!-- SLIDE 4: O PROBLEMA DE NEGÓCIO -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 1 — Contexto & BPMN</div>
                        <div class="title">O Problema de Negócio & Gargalos Operacionais</div>
                    </div>
                </div>
                <div class="member-badge">Eric Luna Costa</div>
            </div>
            <div class="content-grid-3">
                <div class="card">
                    <div class="card-title">🔴 Tempo Elevado</div>
                    <div class="card-item"><strong>• Gargalo 1:</strong> Cada atendimento manual consumia entre 15 a 20 minutos por cliente.</div>
                    <div class="card-item"><strong>• Impacto:</strong> Filas na caixa de e-mail e demora no retorno ao cliente.</div>
                </div>
                <div class="card">
                    <div class="card-title">🔴 Falha Humana na Triagem</div>
                    <div class="card-item"><strong>• Gargalo 2:</strong> Erro no aceite de fichas não assinadas ou documentos faltantes.</div>
                    <div class="card-item"><strong>• Impacto:</strong> Cadastros inconsistentes e alto retrabalho.</div>
                </div>
                <div class="card">
                    <div class="card-title">🔴 Descentralização</div>
                    <div class="card-item"><strong>• Gargalo 3:</strong> Arquivos salvos em pastas dispersas sem espelhamento na nuvem.</div>
                    <div class="card-item"><strong>• Impacto:</strong> Falta de auditoria e perda de histórico.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 4 de 20</span>
            </div>
        </div>

        <!-- SLIDE 5: PROCESSO AS-IS -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 1 — Contexto & BPMN</div>
                        <div class="title">Mapeamento do Processo AS-IS (Manual)</div>
                    </div>
                </div>
                <div class="member-badge">Eric Luna Costa</div>
            </div>
            <div class="content-full">
                <div class="card">
                    <div class="card-title">Fluxo Operacional Manual Antes da Automação</div>
                    <div class="card-item"><strong>Etapa 1 — Recebimento Manual:</strong> Operador abre caixa de e-mail e busca mensagens de clientes.</div>
                    <div class="card-item"><strong>Etapa 2 — Download & Abertura:</strong> Baixa o anexo PDF para a máquina e abre o arquivo no leitor local.</div>
                    <div class="card-item"><strong>Etapa 3 — Validação Visual:</strong> Conferência visual das páginas (Ficha assinada, documento com foto e comprovante).</div>
                    <div class="card-item"><strong>Etapa 4 — Digitação no ERP:</strong> Acessa o Portal Fake ERP e digita manualmente os dados do cliente.</div>
                    <div class="card-item"><strong>Etapa 5 — Organização de Arquivos:</strong> Move o arquivo manualmente para pastas locais.</div>
                    <div class="card-item"><strong>Etapa 6 — Resposta ao Cliente:</strong> Envia e-mail manual de confirmação ou pendência.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 5 de 20</span>
            </div>
        </div>

        <!-- SLIDE 6: PROCESSO TO-BE BPMN -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 1 — Contexto & BPMN</div>
                        <div class="title">Modelagem do Processo TO-BE em BPMN 2.0</div>
                    </div>
                </div>
                <div class="member-badge">Eric Luna Costa</div>
            </div>
            <div class="content-grid-2" style="grid-template-columns: 2fr 1fr;">
                <div class="card" style="text-align: center; justify-content: center; background: #FFF;">
                    <img src="../img/bpmn_atendimento_portal_fake.jpeg" style="max-width: 100%; max-height: 480px; border-radius: 8px; border: 1px solid var(--card-border);" alt="Diagrama BPMN 2.0">
                </div>
                <div class="card">
                    <div class="card-title">📐 Diagrama BPMN 2.0 (Draw.io)</div>
                    <div class="card-item"><strong>• Evento Inicial:</strong> Recebimento de e-mail de solicitação ou retorno de cliente.</div>
                    <div class="card-item"><strong>• Raias (Pools/Lanes):</strong> Setor de Atendimento, Robô de Hyperautomation e Portal ERP.</div>
                    <div class="card-item"><strong>• Fluxo Automatizado:</strong> Geração DOCX -> SMTP -> IMAP -> pypdf -> Playwright -> Google Drive.</div>
                    <div class="card-item"><strong>• Gateways de Decisão:</strong> Validação Documental Aprovada? (Sim -> Documentos_OK / Não -> Documentos_Pendentes).</div>
                    <div class="card-item"><strong>• Eventos Finais:</strong> Notificação ao cliente com protocolo único e arquivamento em Encaminhados.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 6 de 24</span>
            </div>
        </div>

        <!-- SLIDE 7: ARQUITETURA MODULAR -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 2 — Arquitetura & Core</div>
                        <div class="title">Arquitetura Modular da Solução de Hyperautomation</div>
                    </div>
                </div>
                <div class="member-badge">Daniele & Kauã</div>
            </div>
            <div class="content-full">
                <div class="card">
                    <div class="card-title">Módulos Python e Separação de Responsabilidades</div>
                    <div class="card-item"><strong>• orquestrador.py:</strong> Orquestrador principal que controla as 3 fases da solução.</div>
                    <div class="card-item"><strong>• processo_atendimento/leitor_email.py:</strong> Conecta a IMAP4_SSL, busca e-mails não lidos (UNSEEN) e baixa PDFs.</div>
                    <div class="card-item"><strong>• processo_atendimento/validador_docs.py:</strong> Executa validação de conteúdo via pypdf nos PDFs.</div>
                    <div class="card-item"><strong>• processo_atendimento/gestor_arquivos.py:</strong> Gerencia pastas no ERP local e aciona sincronização remota.</div>
                    <div class="card-item"><strong>• processo_atendimento/gestor_drive.py:</strong> Autentica via Google Drive API v3 e realiza criação/movimentação no Drive.</div>
                    <div class="card-item"><strong>• processo_atendimento/resposta_cliente.py:</strong> Envia e-mails HTML responsivos via SMTP.</div>
                    <div class="card-item"><strong>• processo_atendimento/portal_integracao.py:</strong> Automação Web via Playwright no Portal Fake ERP.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 7 de 20</span>
            </div>
        </div>

        <!-- SLIDE 8: STACK TECNOLÓGICO -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 2 — Arquitetura & Core</div>
                        <div class="title">Stack Tecnológico Escolhido & Justificativas</div>
                    </div>
                </div>
                <div class="member-badge">Daniele & Kauã</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Tecnologias de Automação & RPA</div>
                    <div class="card-item"><strong>• Python 3.10:</strong> Linguagem base de alta produtividade e vasto suporte.</div>
                    <div class="card-item"><strong>• Playwright:</strong> RPA Web ultra-rápido em Chromium headless com captura de screenshots.</div>
                    <div class="card-item"><strong>• BotCity Maestro SDK:</strong> Orquestração na nuvem, logs centralizados e controle.</div>
                </div>
                <div class="card">
                    <div class="card-title">Tecnologias de Integração & Documentos</div>
                    <div class="card-item"><strong>• Google Drive API v3:</strong> Conexão oficial via google-api-python-client.</div>
                    <div class="card-item"><strong>• pypdf & python-docx:</strong> Inspeção inteligente de PDFs e montagem de Fichas Word.</div>
                    <div class="card-item"><strong>• imaplib & smtplib:</strong> Conexões seguras SSL para e-mails transacionais.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 8 de 20</span>
            </div>
        </div>

        <!-- SLIDE 9: FASE 1 -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 2 — Arquitetura & Core</div>
                        <div class="title">FASE 1: Geração da Ficha (.docx) & Solicitação SMTP</div>
                    </div>
                </div>
                <div class="member-badge">Daniele & Kauã</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Geração Dinâmica da Ficha em Word</div>
                    <div class="card-item"><strong>• Módulo:</strong> common/documento_email.py (função criar_documento).</div>
                    <div class="card-item"><strong>• Extração Dinâmica:</strong> Robô lê os dados no portal ou base de entrada.</div>
                    <div class="card-item"><strong>• Template Automático:</strong> Preenche a Ficha Cadastral .docx com dados do cliente.</div>
                    <div class="card-item"><strong>• Status Inicial:</strong> Registrado como 'AGUARDANDO ASSINATURA E DOCUMENTOS'.</div>
                </div>
                <div class="card">
                    <div class="card-title">Disparo de E-mail de Solicitação</div>
                    <div class="card-item"><strong>• Módulo:</strong> processo_atendimento/resposta_cliente.py.</div>
                    <div class="card-item"><strong>• Protocolo Único:</strong> Gera protocolo de atendimento #YYYY-XXXX.</div>
                    <div class="card-item"><strong>• E-mail HTML:</strong> Envia ficha DOCX e instruções para o retorno em PDF Único.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 9 de 20</span>
            </div>
        </div>

        <!-- SLIDE 10: FASE 2 -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 2 — Arquitetura & Core</div>
                        <div class="title">FASE 2: Leitor IMAP & Extração de Anexos</div>
                    </div>
                </div>
                <div class="member-badge">Daniele & Kauã</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Monitoramento Inteligente via IMAP</div>
                    <div class="card-item"><strong>• Conexão SSL:</strong> imaplib.IMAP4_SSL em imap.gmail.com.</div>
                    <div class="card-item"><strong>• Busca Seletiva:</strong> Filtro estrito por e-mails NÃO LIDOS (UNSEEN) com "Assinatura" no assunto.</div>
                    <div class="card-item"><strong>• Prevenção de Duplicidade:</strong> Aplica a flag \Seen no servidor imediatamente.</div>
                </div>
                <div class="card">
                    <div class="card-title">Extração e Salvamento de Anexos</div>
                    <div class="card-item"><strong>• Módulo:</strong> processo_atendimento/leitor_email.py.</div>
                    <div class="card-item"><strong>• Extração PDF:</strong> Decodifica anexos e salva em ERP_Portal_Fake/Downloads/.</div>
                    <div class="card-item"><strong>• Trigger no Drive:</strong> Dispara o upload automático para a pasta 'Downloads' no Google Drive.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 10 de 20</span>
            </div>
        </div>

        <!-- SLIDE 11: FASE 3 -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 2 — Arquitetura & Core</div>
                        <div class="title">FASE 3: Validador Documental Inteligente (pypdf)</div>
                    </div>
                </div>
                <div class="member-badge">Daniele & Kauã</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Inspeção de Conteúdo em PDFs com pypdf</div>
                    <div class="card-item"><strong>• Módulo:</strong> processo_atendimento/validador_docs.py.</div>
                    <div class="card-item"><strong>• Checagem de Integridade:</strong> Rejeita arquivos vazios ou corrompidos.</div>
                    <div class="card-item"><strong>• Inspeção de Conteúdo:</strong> Busca termos obrigatórios: Ficha Cadastral Assinada, Documento com Foto e Comprovante de Residência.</div>
                </div>
                <div class="card">
                    <div class="card-title">Decisão de Aprovação vs Pendência</div>
                    <div class="card-item"><strong>• APROVADO:</strong> Move para 'Documentos_OK', cadastra via Playwright, move para 'Encaminhados' e envia e-mail HTML de sucesso.</div>
                    <div class="card-item"><strong>• REPROVADO:</strong> Move para 'Documentos_Pendentes' e envia e-mail HTML notificando pendências.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 11 de 20</span>
            </div>
        </div>

        <!-- SLIDE 12: ESTRUTURA ERP -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 3 — ERP, Drive & DevOps</div>
                        <div class="title">Estrutura de Pastas do ERP Simulado</div>
                    </div>
                </div>
                <div class="member-badge">Sannyer C. Nery</div>
            </div>
            <div class="content-full">
                <div class="card">
                    <div class="card-title">Gerenciador de Arquivos ERP (gestor_arquivos.py)</div>
                    <div class="card-item"><strong>1. Downloads/:</strong> Pasta de entrada onde todos os novos PDFs baixados da caixa de e-mail são depositados.</div>
                    <div class="card-item"><strong>2. Documentos_OK/:</strong> Pasta intermediária para arquivos cujos PDFs foram validados e aprovados pelas regras de negócio.</div>
                    <div class="card-item"><strong>3. Documentos_Pendentes/:</strong> Pasta de retenção para documentos reprovados ou com inconsistências.</div>
                    <div class="card-item"><strong>4. Encaminhados/:</strong> Pasta final onde ficam armazenados os cadastros ativos concluídos e encaminhados ao próximo setor.</div>
                    <div class="card-item"><strong>• Sincronismo Físico/Nuvem:</strong> Cada operação shutil.move() executada localmente invoca automaticamente o gestor_drive.mover_arquivo().</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 12 de 20</span>
            </div>
        </div>

        <!-- SLIDE 13: GOOGLE DRIVE API V3 -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 3 — ERP, Drive & DevOps</div>
                        <div class="title">Integração Avançada com Google Drive API v3</div>
                    </div>
                </div>
                <div class="member-badge">Sannyer C. Nery</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Módulo GestorDrive (gestor_drive.py)</div>
                    <div class="card-item"><strong>• Mapeamento Automático:</strong> Mapeia a pasta raiz ERP_Portal_Fake e garante as 4 subpastas no Drive.</div>
                    <div class="card-item"><strong>• Variável de ID:</strong> Suporte a GOOGLE_DRIVE_FOLDER_ID no .env para vincular à pasta compartilhada.</div>
                    <div class="card-item"><strong>• Drives Compartilhados:</strong> Inclusão de supportsAllDrives=True e includeItemsFromAllDrives=True em todas as chamadas.</div>
                </div>
                <div class="card">
                    <div class="card-title">Movimentação Remota Inteligente</div>
                    <div class="card-item"><strong>• Atualização de Parents:</strong> Altera os pais dos arquivos via API (addParents/removeParents) sem duplicá-los.</div>
                    <div class="card-item"><strong>• Rastreamento por Nome:</strong> Localização de arquivos por query no Drive com fallback.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 13 de 20</span>
            </div>
        </div>

        <!-- SLIDE 14: COTA DRIVE -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 3 — ERP, Drive & DevOps</div>
                        <div class="title">Resolução do Desafio Técnico: Cota 0MB no Drive</div>
                    </div>
                </div>
                <div class="member-badge">Sannyer C. Nery</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Diagnóstico do Erro HTTP 403 Google API</div>
                    <div class="card-item"><strong>• Causa Raiz:</strong> Service Accounts possuem COTA ZERO (0 MB) em drives pessoais @gmail.com.</div>
                    <div class="card-item"><strong>• Comportamento:</strong> Ao criar arquivos em pasta compartilhada, a API atribuía posse à Service Account, gerando o erro storageQuotaExceeded.</div>
                    <div class="card-item"><strong>• Solução:</strong> Implementada arquitetura híbrida de autenticação.</div>
                </div>
                <div class="card">
                    <div class="card-title">Solução Híbrida & Fallback de Upload</div>
                    <div class="card-item"><strong>• Suporte Duplo:</strong> O GestorDrive suporta Service Account e OAuth 2.0 Client ID (gerando token.json automático).</div>
                    <div class="card-item"><strong>• Fallback de Upload:</strong> Se o arquivo não existir no Drive ao mover, dispara upload_arquivo() de fallback automaticamente.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 14 de 20</span>
            </div>
        </div>

        <!-- SLIDE 15: PLAYWRIGHT WEB -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 3 — ERP, Drive & DevOps</div>
                        <div class="title">Automação Web no Portal Fake (Playwright)</div>
                    </div>
                </div>
                <div class="member-badge">Sannyer C. Nery</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Integração RPA no Portal ERP</div>
                    <div class="card-item"><strong>• Execução de Alta Velocidade:</strong> Playwright Chromium em modo Headless.</div>
                    <div class="card-item"><strong>• Preenchimento Cadastral:</strong> Insere Nome, CPF, E-mail, Telefone, Endereço e Observações.</div>
                    <div class="card-item"><strong>• Status no ERP:</strong> Atualiza o cadastro do cliente para 'ATIVO' no Portal Fake.</div>
                </div>
                <div class="card">
                    <div class="card-title">Auditoria Visual por Screenshots</div>
                    <div class="card-item"><strong>• Captura Automática:</strong> Gera imagens 01_portal_preenchido.png e 02_extracao_dados.png.</div>
                    <div class="card-item"><strong>• BotCity Maestro:</strong> Posta screenshots no painel Maestro como artefatos de auditoria.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 15 de 20</span>
            </div>
        </div>

        <!-- SLIDE 16: ORQUESTRADOR & GITFLOW -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 3 — ERP, Drive & DevOps</div>
                        <div class="title">Orquestrador Principal & Governança GitFlow</div>
                    </div>
                </div>
                <div class="member-badge">Sannyer C. Nery</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Orquestrador Geral (orquestrador.py)</div>
                    <div class="card-item"><strong>• Modos CLI:</strong> enviar_solicitacoes (Fase 1), processar_retornos (Fases 2 e 3) e demo_completo.</div>
                    <div class="card-item"><strong>• Maestro SDK:</strong> Execuções agendadas na nuvem, captura de parâmetros e controle de tarefas.</div>
                </div>
                <div class="card">
                    <div class="card-title">Governança DevOps & GitFlow</div>
                    <div class="card-item"><strong>• Branches:</strong> main (produção), develop (integração contínua), feature/* e release/2.0.</div>
                    <div class="card-item"><strong>• Proteção de Segredos:</strong> Isolamento estrito de credenciais (.env, credentials.json, token.json) no .gitignore.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 16 de 20</span>
            </div>
        </div>

        <!-- SLIDE 17: LOGS DE EXECUÇÃO -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 4 — Demonstração & Resultados</div>
                        <div class="title">Evidências Práticas: Logs Reais de Execução</div>
                    </div>
                </div>
                <div class="member-badge">Equipe Integrada</div>
            </div>
            <div class="content-full">
                <div class="code-box">===========================================================================
INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION - PROCESSO 1 (MODO: DEMO_COMPLETO)
===========================================================================
[Etapa 0] Inicializando Módulos do Processo 1...
[GESTOR ARQUIVOS] Estrutura de pastas local garantida em: .../ERP_Portal_Fake
[GESTOR DRIVE] Autenticado com sucesso via Service Account!
[GESTOR DRIVE] Usando ID configurado para a pasta raiz 'ERP_Portal_Fake': 1_AMktNc_sXyN9GWkjVVV1a2fuYPtKQ7w
[GESTOR DRIVE] Estrutura de pastas no Google Drive pronta: ['ERP_Portal_Fake', 'Downloads', 'Documentos_OK', 'Documentos_Pendentes', 'Encaminhados']

[FASE 1] GERAÇÃO E ENVIO DE FICHA PARA ASSINATURA (Ana Silva) | Protocolo: #2026-0001
  [FASE 1] Ficha DOCX gerada: Ficha_Cadastro_11122233344.docx
  [FASE 1] E-mail de solicitação enviado com sucesso.

[FASE 2 & 3] MONITORAMENTO DO RETORNO, VALIDAÇÃO E CADASTRO (Ana Silva)
  [LEITOR EMAIL] Encontrados 1 novos e-mails não lidos de retorno.
  [VALIDAÇÃO] Documentação e Ficha Assinada APROVADAS para Ana Silva.
[GESTOR ARQUIVOS] Arquivo 'Ficha_Assinada_Ana_Silva.pdf' movido para 'Documentos_OK'.
[GESTOR DRIVE] Arquivo movido de 'Downloads' para 'Documentos_OK' no Google Drive!
[PORTAL INTEGRAÇÃO] Cadastrando cliente Ana Silva (CPF: 11122233344) no Portal Fake...
[PORTAL INTEGRAÇÃO] Cadastro de 'Ana' concluído com sucesso (Status: ATIVO).
[GESTOR ARQUIVOS] Arquivo movido para 'Encaminhados'.
[GESTOR DRIVE] Arquivo movido de 'Documentos_OK' para 'Encaminhados' no Google Drive!
===========================================================================
ORQUESTRAÇÃO DO PROCESSO 1 FINALIZADA COM SUCESSO!</div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 17 de 20</span>
            </div>
        </div>

        <!-- SLIDE 18: EVIDÊNCIA 1 - PORTAL FAKE PREENCHIDO -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 4 — Demonstração & Resultados</div>
                        <div class="title">Evidência 1: Interface Web do Portal Fake ERP (Preenchimento RPA)</div>
                    </div>
                </div>
                <div class="member-badge">Equipe Integrada</div>
            </div>
            <div class="content-grid-2" style="grid-template-columns: 2fr 1fr;">
                <div class="card" style="text-align: center; justify-content: center; background: #FFF;">
                    <img src="../../HyperAutomation/resources/screenshots/01_portal_preenchido.png" style="max-width: 100%; max-height: 480px; border-radius: 8px; border: 1px solid var(--card-border);" alt="Portal Preenchido">
                </div>
                <div class="card">
                    <div class="card-title">🤖 Automação Web Playwright</div>
                    <div class="card-item"><strong>• Interface do Portal ERP:</strong> Visão geral da tabela de cadastros mantida no Portal Fake Soluções Digitais.</div>
                    <div class="card-item"><strong>• Execução de Alta Velocidade:</strong> Preenchimento e sincronização dinâmica em massa executados via Chromium Headless.</div>
                    <div class="card-item"><strong>• Validação em Tela:</strong> Verificação de campos obrigatórios e integridade das linhas de cadastro.</div>
                    <div class="card-item"><strong>• Rastreabilidade:</strong> Captura de tela automatizada no encerramento da carga inicial do sistema.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 18 de 24</span>
            </div>
        </div>

        <!-- SLIDE 19: EVIDÊNCIA 2 - FORMULÁRIO E ATIVAÇÃO DE CADASTRO -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 4 — Demonstração & Resultados</div>
                        <div class="title">Evidência 2: Formulário e Ativação de Cadastro no ERP</div>
                    </div>
                </div>
                <div class="member-badge">Equipe Integrada</div>
            </div>
            <div class="content-grid-2" style="grid-template-columns: 2fr 1fr;">
                <div class="card" style="text-align: center; justify-content: center; background: #FFF;">
                    <img src="../../HyperAutomation/resources/screenshots/02_extracao_dados.png" style="max-width: 100%; max-height: 480px; border-radius: 8px; border: 1px solid var(--card-border);" alt="Ativação de Cadastro">
                </div>
                <div class="card">
                    <div class="card-title">✅ Ativação de Cadastro</div>
                    <div class="card-item"><strong>• Modal de Novo Cadastro:</strong> Formulário cadastral preenchido automaticamente com os dados extraídos do cliente.</div>
                    <div class="card-item"><strong>• Transição de Status:</strong> Cliente ativado no ERP com a transição automática do estado para 'ATIVO' após validação documental.</div>
                    <div class="card-item"><strong>• Registro de Atendimento:</strong> Inclusão de observações auditáveis informando o atendimento automatizado.</div>
                    <div class="card-item"><strong>• Screenshot de Evidência:</strong> Registro armazenado e enviado como artefato ao BotCity Maestro.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 19 de 24</span>
            </div>
        </div>

        <!-- SLIDE 20: EVIDÊNCIA 3 - CONFIRMAÇÃO DE SUCESSO DE E-MAIL -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 4 — Demonstração & Resultados</div>
                        <div class="title">Evidência 3: Confirmação de Cadastro Aprovado (E-mail HTML)</div>
                    </div>
                </div>
                <div class="member-badge">Equipe Integrada</div>
            </div>
            <div class="content-grid-2" style="grid-template-columns: 2fr 1fr;">
                <div class="card" style="text-align: center; justify-content: center; background: #FFF;">
                    <img src="../img/sucesso.png" style="max-width: 100%; max-height: 480px; border-radius: 8px; border: 1px solid var(--card-border);" alt="Sucesso">
                </div>
                <div class="card">
                    <div class="card-title">✅ Cenário de Sucesso</div>
                    <div class="card-item"><strong>• Validação Documental:</strong> 100% Aprovado.</div>
                    <div class="card-item"><strong>• Análise do PDF:</strong> Ficha Cadastral Assinada, Documento com Foto e Comprovante de Residência validados via pypdf.</div>
                    <div class="card-item"><strong>• Automação Web:</strong> Cadastro ativado no Portal Fake ERP como 'ATIVO' via Playwright.</div>
                    <div class="card-item"><strong>• Gestão de Arquivos:</strong> Arquivo transferido para 'Documentos_OK' e depois 'Encaminhados' (local e Google Drive).</div>
                    <div class="card-item"><strong>• Notificação:</strong> Disparo instantâneo do e-mail em HTML responsivo com protocolo único de aprovação.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 20 de 24</span>
            </div>
        </div>

        <!-- SLIDE 21: EVIDÊNCIA 4 - PENDÊNCIA: FALTA DOC COM FOTO -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 4 — Demonstração & Resultados</div>
                        <div class="title">Evidência 4: Pendência — Falta Documento Oficial com Foto</div>
                    </div>
                </div>
                <div class="member-badge">Equipe Integrada</div>
            </div>
            <div class="content-grid-2" style="grid-template-columns: 2fr 1fr;">
                <div class="card" style="text-align: center; justify-content: center; background: #FFF;">
                    <img src="../img/falha_faltou_documento_foto.png" style="max-width: 100%; max-height: 480px; border-radius: 8px; border: 1px solid var(--card-border);" alt="Faltou Foto">
                </div>
                <div class="card">
                    <div class="card-title">⚠️ Cenário de Inconsistência</div>
                    <div class="card-item"><strong>• Validação Documental:</strong> Reprovado por Pendência.</div>
                    <div class="card-item"><strong>• Inconsistência Detectada:</strong> Ausência do Documento Oficial de Identificação com Foto (RG / CPF) no PDF enviado.</div>
                    <div class="card-item"><strong>• Gestão de Arquivos:</strong> PDF retido e movido para a pasta 'Documentos_Pendentes' no ERP local e no Google Drive.</div>
                    <div class="card-item"><strong>• Notificação Automática:</strong> Disparo imediato de e-mail em HTML orientando o cliente sobre o reenvio exato da identidade com foto.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 21 de 24</span>
            </div>
        </div>

        <!-- SLIDE 22: EVIDÊNCIA 5 - PENDÊNCIA: FALTA COMPROVANTE -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 4 — Demonstração & Resultados</div>
                        <div class="title">Evidência 5: Pendência — Falta Comprovante de Residência</div>
                    </div>
                </div>
                <div class="member-badge">Equipe Integrada</div>
            </div>
            <div class="content-grid-2" style="grid-template-columns: 2fr 1fr;">
                <div class="card" style="text-align: center; justify-content: center; background: #FFF;">
                    <img src="../img/falha_falta-comprovante-residencia.png" style="max-width: 100%; max-height: 480px; border-radius: 8px; border: 1px solid var(--card-border);" alt="Falta Comprovante">
                </div>
                <div class="card">
                    <div class="card-title">⚠️ Cenário de Inconsistência</div>
                    <div class="card-item"><strong>• Validação Documental:</strong> Reprovado por Pendência.</div>
                    <div class="card-item"><strong>• Inconsistência Detectada:</strong> Ausência do Comprovante de Residência (fatura de água/luz/endereço) no PDF retornado.</div>
                    <div class="card-item"><strong>• Gestão de Arquivos:</strong> PDF movido para 'Documentos_Pendentes' no ERP e espelhado no Google Drive.</div>
                    <div class="card-item"><strong>• Notificação Automática:</strong> Envio de e-mail em HTML responsivo solicitando a regularização do comprovante residencial.</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 22 de 24</span>
            </div>
        </div>

        <!-- SLIDE 22: TABELA COMPARATIVA -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 4 — Demonstração & Resultados</div>
                        <div class="title">Métricas de Sucesso & Tabela Comparativa de Ganhos</div>
                    </div>
                </div>
                <div class="member-badge">Equipe Integrada</div>
            </div>
            <div class="content-full">
                <table>
                    <thead>
                        <tr>
                            <th>Métrica de Desempenho</th>
                            <th>Processo Manual (AS-IS)</th>
                            <th>Processo Automatizado (TO-BE)</th>
                            <th>Ganho / Melhoria Obtida</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Tempo por Atendimento</strong></td>
                            <td>15 a 20 minutos por cliente</td>
                            <td>Aproximadamente 5 segundos</td>
                            <td>⚡ <strong>Redução de 99.5%</strong> no tempo de processamento</td>
                        </tr>
                        <tr>
                            <td><strong>Taxa de Erro na Triagem</strong></td>
                            <td>12% a 15% (falha humana)</td>
                            <td>0% (regras de negócio estritas)</td>
                            <td>🎯 <strong>Eliminação total</strong> de cadastros com docs incompletos</td>
                        </tr>
                        <tr>
                            <td><strong>Organização de Arquivos</strong></td>
                            <td>Dispersos localmente sem padrão</td>
                            <td>Sincronizados local e no Drive</td>
                            <td>☁️ <strong>100% dos arquivos</strong> padronizados na nuvem</td>
                        </tr>
                        <tr>
                            <td><strong>Comunicação com Cliente</strong></td>
                            <td>E-mails manuais sem padronização</td>
                            <td>Templates HTML automatizados</td>
                            <td>✉️ <strong>Notificação instantânea</strong> com protocolo único</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 22 de 23</span>
            </div>
        </div>

        <!-- SLIDE 23: CONCLUSÃO -->
        <div class="slide">
            <div class="header">
                <div class="header-title-box">
                    <div class="red-bar"></div>
                    <div>
                        <div class="category">Bloco 4 — Demonstração & Resultados</div>
                        <div class="title">Conclusão & Defesa do Projeto</div>
                    </div>
                </div>
                <div class="member-badge">Equipe Integrada</div>
            </div>
            <div class="content-grid-2">
                <div class="card">
                    <div class="card-title">Atendimento a 100% dos Requisitos do Roteiro 10</div>
                    <div class="card-item">✅ <strong>Modelagem BPMN 2.0:</strong> Processo 1 totalmente mapeado no Draw.io.</div>
                    <div class="card-item">✅ <strong>Automação Integrada:</strong> Solução acoplada ao projeto preexistente.</div>
                    <div class="card-item">✅ <strong>Validação Inteligente:</strong> Inspeção de conteúdo em PDFs via pypdf.</div>
                    <div class="card-item">✅ <strong>Sincronização em Nuvem:</strong> Integração nativa com Google Drive API v3.</div>
                    <div class="card-item">✅ <strong>Governança de Código:</strong> Repositório GitHub com metodologia GitFlow.</div>
                </div>
                <div class="card">
                    <div class="card-title">Muito Obrigado! Pergunta & Resposta (Q&A)</div>
                    <div class="card-item"><strong>• Equipe 1:</strong> Eric Luna, Daniele Greice, Kauã Sales e Sannyer Cardoso.</div>
                    <div class="card-item"><strong>• Professor:</strong> Prof. Moisés Levy | Disciplina: Técnicas de Hyperautomation.</div>
                    <div class="card-item"><strong>• Instituição:</strong> PÓLO DE INOVAÇÃO IFAM / FAEPI / LG.</div>
                    <div class="card-item"><strong>• Espaço Aberto:</strong> Estamos à disposição da banca para dúvidas e demonstração ao vivo!</div>
                </div>
            </div>
            <div class="footer">
                <span>Empresa Portal Fake — Processo 1</span>
                <span>Slide 23 de 23</span>
            </div>
        </div>

    </div>

    <!-- Navigation Controls -->
    <div class="controls">
        <button class="btn btn-sec" onclick="prevSlide()">❮ Anterior</button>
        <button class="btn" onclick="nextSlide()">Próximo ❯</button>
    </div>

    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
            });
        }

        function nextSlide() {
            if (currentSlide < slides.length - 1) {
                currentSlide++;
                showSlide(currentSlide);
            }
        }

        function prevSlide() {
            if (currentSlide > 0) {
                currentSlide--;
                showSlide(currentSlide);
            }
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === 'Space') nextSlide();
            if (e.key === 'ArrowLeft') prevSlide();
        });
    </script>
</body>
</html>
"""

output_path = Path(__file__).resolve().parent / "Apresentacao_Hyperautomation_Processo1_LG.html"
output_path.write_text(html_content, encoding='utf-8')
print(f"Apresentação HTML gerada com sucesso: {output_path}")
