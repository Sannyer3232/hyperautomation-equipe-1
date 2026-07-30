import os
import sys
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)

    # LG Color Palette
    LG_RED = RGBColor(0xA5, 0x00, 0x34)       # #A50034
    DARK_GREY = RGBColor(0x33, 0x33, 0x33)    # #333333
    LIGHT_BG = RGBColor(0xF8, 0xF9, 0xFA)     # #F8F9FA
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)        # #FFFFFF
    CARD_BG = RGBColor(0xEE, 0xF1, 0xF5)      # #EEF1F5
    CARD_BORDER = RGBColor(0xD0, 0xD7, 0xDE)  # #D0D7DE
    ACCENT_BLUE = RGBColor(0x0F, 0x4C, 0x81)  # #0F4C81
    SUBTITLE_GREY = RGBColor(0x66, 0x66, 0x66)# #666666

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category_text, member_tag):
        # Header bar background
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = WHITE
        top_bar.line.color.rgb = CARD_BORDER
        top_bar.line.width = Pt(1)

        # Red accent line on left
        red_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.2), Inches(0.12), Inches(0.7))
        red_line.fill.solid()
        red_line.fill.fore_color.rgb = LG_RED
        red_line.line.fill.background()

        # Category text
        tx_box = slide.shapes.add_textbox(Inches(0.75), Inches(0.15), Inches(9.0), Inches(0.3))
        tf = tx_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = LG_RED

        # Title text
        tx_box2 = slide.shapes.add_textbox(Inches(0.75), Inches(0.4), Inches(9.0), Inches(0.6))
        tf2 = tx_box2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = title_text
        p2.font.size = Pt(20)
        p2.font.bold = True
        p2.font.color.rgb = DARK_GREY

        # Member Tag Badge (Top Right)
        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.8), Inches(0.3), Inches(3.0), Inches(0.5))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = LG_RED
        tag_box.line.fill.background()
        tf_tag = tag_box.text_frame
        p_tag = tf_tag.paragraphs[0]
        p_tag.alignment = PP_ALIGN.CENTER
        p_tag.text = member_tag
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = WHITE

    def add_footer(slide, current_page, total_pages=20):
        footer_box = slide.shapes.add_textbox(Inches(0.5), Inches(7.0), Inches(12.333), Inches(0.4))
        tf = footer_box.text_frame
        p = tf.paragraphs[0]
        p.text = f"Empresa Portal Fake — Processo 1 (Setor de Atendimento) | Técnicas de Hyperautomation (LG / IFAM / FAEPI) | Slide {current_page} de {total_pages}"
        p.font.size = Pt(9)
        p.font.color.rgb = SUBTITLE_GREY

    def add_card(slide, left, top, width, height, title, content_list, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_right = Inches(0.2)
        tf.margin_top = Inches(0.2)
        tf.margin_bottom = Inches(0.2)

        if title:
            p_title = tf.paragraphs[0]
            p_title.text = title
            p_title.font.size = Pt(14)
            p_title.font.bold = True
            p_title.font.color.rgb = LG_RED
            p_title.space_after = Pt(8)

        for idx, item in enumerate(content_list):
            p = tf.add_paragraph() if (title or idx > 0) else tf.paragraphs[0]
            p.space_after = Pt(6)
            if isinstance(item, tuple):
                bold_txt, norm_txt = item
                r1 = p.add_run()
                r1.text = bold_txt + " "
                r1.font.bold = True
                r1.font.size = Pt(11)
                r1.font.color.rgb = DARK_GREY
                r2 = p.add_run()
                r2.text = norm_txt
                r2.font.size = Pt(11)
                r2.font.color.rgb = DARK_GREY
            else:
                r = p.add_run()
                r.text = item
                r.font.size = Pt(11)
                r.font.color.rgb = DARK_GREY

    # ==========================================
    # SLIDE 1: COVER SLIDE
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1, LIGHT_BG)

    # Top red decorative bar
    bar1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.25))
    bar1.fill.solid()
    bar1.fill.fore_color.rgb = LG_RED
    bar1.line.fill.background()

    # Main Card
    main_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(11.333), Inches(5.2))
    main_card.fill.solid()
    main_card.fill.fore_color.rgb = WHITE
    main_card.line.color.rgb = CARD_BORDER
    main_card.line.width = Pt(1)

    tf1 = main_card.text_frame
    tf1.word_wrap = True
    tf1.margin_left = Inches(0.5)
    tf1.margin_top = Inches(0.5)

    p = tf1.paragraphs[0]
    p.text = "DEFESA DA SOLUÇÃO DE HYPERAUTOMATION"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = LG_RED
    p.space_after = Pt(6)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Processo 1: Automação do Setor de Atendimento & Cadastro da Empresa Portal Fake"
    p_sub.font.size = Pt(16)
    p_sub.font.bold = True
    p_sub.font.color.rgb = DARK_GREY
    p_sub.space_after = Pt(24)

    p_info = tf1.add_paragraph()
    p_info.text = "Disciplina: Técnicas de Hyperautomation (Semana 07 / Atividade 11)\nProfessor: Prof. Moisés Levy | Tempo de Apresentação: 20 Minutos\nInstituição: PÓLO DE INOVAÇÃO IFAM / FAEPI / LG"
    p_info.font.size = Pt(12)
    p_info.font.color.rgb = SUBTITLE_GREY
    p_info.space_after = Pt(24)

    # Team Grid in Cover
    p_team = tf1.add_paragraph()
    p_team.text = "EQUIPE 1 (INTEGRANTES & PAPEIS):"
    p_team.font.size = Pt(12)
    p_team.font.bold = True
    p_team.font.color.rgb = LG_RED
    p_team.space_after = Pt(6)

    members = [
        "• Eric Luna Costa — Analista de Processos BPMN & Regras de Negócio",
        "• Daniele Greice Albuquerque e Silva — Desenvolvedora de Automação Core",
        "• Kauã Sales Viana — Desenvolvedor de Automação Core",
        "• Sannyer Cardoso Carvalho Nery — DevOps, Versionamento, Arquitetura & Orquestração"
    ]
    for m in members:
        pm = tf1.add_paragraph()
        pm.text = m
        pm.font.size = Pt(11)
        pm.font.color.rgb = DARK_GREY

    add_footer(slide1, 1)

    # ==========================================
    # SLIDE 2: AGENDA DA APRESENTAÇÃO
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2, LIGHT_BG)
    add_header(slide2, "Agenda da Apresentação Técnica (20 Minutos)", "ESTRUTURA DA DEFESA", "Visão Geral")

    add_card(slide2, 0.6, 1.4, 5.8, 2.5, "BLOCO 1: Contexto & BPMN (0 a 5 min)", [
        ("Apresentador:", "Eric Luna Costa"),
        ("• Contexto do Problema:", "Gargalos do atendimento manual no Portal Fake."),
        ("• Processo AS-IS:", "Fluxo operacional antes da automação."),
        ("• Processo TO-BE:", "Modelagem BPMN 2.0 no Draw.io e regras de negócio.")
    ])

    add_card(slide2, 6.8, 1.4, 5.8, 2.5, "BLOCO 2: Arquitetura & Core (5 a 10 min)", [
        ("Apresentadores:", "Daniele Greice & Kauã Sales"),
        ("• Stack Tecnológico:", "Python 3.10, Playwright, pypdf, BotCity Maestro."),
        ("• Fases 1 & 2:", "Geração de Ficha Word, Envio SMTP e Leitor IMAP."),
        ("• Fase 3:", "Validador documental inteligente de PDFs únicos.")
    ])

    add_card(slide2, 0.6, 4.2, 5.8, 2.5, "BLOCO 3: ERP, Drive & DevOps (10 a 15 min)", [
        ("Apresentador:", "Sannyer Cardoso Carvalho Nery"),
        ("• Gestão de Arquivos:", "Pastas ERP local e Google Drive API v3."),
        ("• Solução de Cota:", "Suporte OAuth 2.0 / Service Account e GOOGLE_DRIVE_FOLDER_ID."),
        ("• Governança & GitFlow:", "Orquestrador central e controle de versão.")
    ])

    add_card(slide2, 6.8, 4.2, 5.8, 2.5, "BLOCO 4: Evidências & Resultados (15 a 20 min)", [
        ("Apresentadores:", "Equipe Integrada"),
        ("• Evidências Práticas:", "Execution logs do terminal e screenshots do portal."),
        ("• Tabela de Ganhos:", "Comparativo de métricas de eficiência (Antes vs Depois)."),
        ("• Conclusão & Q&A:", "Defesa técnica e resposta a perguntas da banca.")
    ])

    add_footer(slide2, 2)

    # ==========================================
    # SLIDE 3: CONTEXTO ORGANIZACIONAL
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3, LIGHT_BG)
    add_header(slide3, "Contexto Organizacional: Empresa Portal Fake", "BLOCO 1 — CONTEXTO & BPMN", "Eric Luna Costa")

    add_card(slide3, 0.6, 1.4, 5.8, 5.2, "O ERP Simulado da Empresa Portal Fake", [
        ("• Operação Comercial:", "A Empresa Portal Fake atua no fornecimento de soluções digitais e cadastramento de novos clientes."),
        ("• Volume Operacional:", "Recebe diariamente dezenas de solicitações cadastrais que exigem validação de documentos com foto, comprovante de residência e ficha assinada."),
        ("• Ecossistema Híbrido:", "A operação necessita de integração constante entre a interface Web (Portal ERP), a caixa de e-mails corporativa e o repositório de arquivos na nuvem.")
    ])

    add_card(slide3, 6.8, 1.4, 5.8, 5.2, "Desafios do Setor de Atendimento", [
        ("• Alta Dependência Manual:", "Operadores humanos realizam triagem manual repetitiva e verificação visual de anexos."),
        ("• Complexidade de Integração:", "Necessidade de ler e-mails de retorno, extrair anexos, converter/validar PDFs, atualizar dados no Portal Web e organizar arquivos."),
        ("• Requisito da Semana 07:", "Evoluir a automação existente sem recriar o robô, adicionando o módulo de Atendimento com padrão arquitetural limpo e integrado.")
    ])

    add_footer(slide3, 3)

    # ==========================================
    # SLIDE 4: O PROBLEMA DE NEGÓCIO
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4, LIGHT_BG)
    add_header(slide4, "O Problema de Negócio & Gargalos Operacionais", "BLOCO 1 — CONTEXTO & BPMN", "Eric Luna Costa")

    add_card(slide4, 0.6, 1.4, 3.8, 5.2, "🔴 Tempo de Resposta Elevado", [
        ("• Gargalo 1:", "Cada atendimento manual consumia entre 15 a 20 minutos por cliente."),
        ("• Impacto:", "Filas de espera na caixa de e-mail e demora no envio de confirmações aos clientes.")
    ])

    add_card(slide4, 4.7, 1.4, 3.8, 5.2, "🔴 Falha Humana na Triagem", [
        ("• Gargalo 2:", "Erro frequente no aceite de fichas não assinadas ou documentos com foto ausentes."),
        ("• Impacto:", "Cadastros inconsistentes inseridos no sistema e necessidade de retrabalho constante.")
    ])

    add_card(slide4, 8.8, 1.4, 3.8, 5.2, "🔴 Descentralização de Dados", [
        ("• Gargalo 3:", "Arquivos salvos em pastas locais dispersas sem espelhamento na nuvem."),
        ("• Impacto:", "Falta de auditoria, perda de histórico e dificuldade de acesso por outros setores.")
    ])

    add_footer(slide4, 4)

    # ==========================================
    # SLIDE 5: MAPEAMENTO PROCESSO AS-IS
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5, LIGHT_BG)
    add_header(slide5, "Mapeamento do Processo AS-IS (Manual)", "BLOCO 1 — CONTEXTO & BPMN", "Eric Luna Costa")

    add_card(slide5, 0.6, 1.4, 12.0, 5.2, "Fluxo Operacional Manual Antes da Automação", [
        ("Etapa 1 — Recebimento Manual:", "Operador abre a caixa de e-mail individual e verifica se há respostas de clientes."),
        ("Etapa 2 — Download & Abertura:", "Faz o download manual do anexo PDF para a área de trabalho e abre o arquivo no leitor local."),
        ("Etapa 3 — Validação Visual:", "Confera visualmente se o PDF contém 3 páginas (Ficha assinada, documento com foto e comprovante de residência)."),
        ("Etapa 4 — Digitação no ERP:", "Abre o navegador, acessa o Portal Fake ERP e digita manualmente todos os dados do cliente."),
        ("Etapa 5 — Organização de Arquivos:", "Move manualmente o arquivo para pastas locais de aprovados ou rejeitados."),
        ("Etapa 6 — Resposta ao Cliente:", "Escreve um e-mail manual informando o status da aprovação ou pendência.")
    ])

    add_footer(slide5, 5)

    # ==========================================
    # SLIDE 6: MAPEAMENTO PROCESSO TO-BE BPMN 2.0
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6, LIGHT_BG)
    add_header(slide6, "Modelagem do Processo TO-BE em BPMN 2.0", "BLOCO 1 — CONTEXTO & BPMN", "Eric Luna Costa")

    add_card(slide6, 0.6, 1.4, 5.8, 5.2, "Estrutura do Diagrama BPMN 2.0 (Draw.io)", [
        ("• Evento Inicial:", "Chegada de e-mail com solicitação de atendimento ou retorno de assinatura."),
        ("• Atividades Automatizadas:", "Geração de DOCX -> Disparo SMTP -> Monitoramento IMAP -> Extração -> Validação PDF -> Cadastro Playwright -> Sync Drive."),
        ("• Pontos de Decisão (Gateway):", "Documentação Válida? (Sim -> Documentos_OK / Não -> Documentos_Pendentes)."),
        ("• Eventos Finais:", "Confirmação enviada ao cliente & PDF transferido para Encaminhados.")
    ])

    add_card(slide6, 6.8, 1.4, 5.8, 5.2, "Principais Ganhos do Modelo TO-BE", [
        ("• Autonomia Total:", "Eliminação de qualquer intervenção humana na triagem e digitação."),
        ("• Regras de Negócio Estritas:", "Rejeição imediata de arquivos sem assinatura ou fora do padrão."),
        ("• Sincronização em Tempo Real:", "Sincronização instantânea das movimentações com o Google Drive.")
    ])

    add_footer(slide6, 6)

    # ==========================================
    # SLIDE 7: ARQUITETURA DA SOLUÇÃO
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7, LIGHT_BG)
    add_header(slide7, "Arquitetura Modular da Solução de Hyperautomation", "BLOCO 2 — ARQUITETURA & CORE", "Daniele & Kauã")

    add_card(slide7, 0.6, 1.4, 12.0, 5.2, "Módulos Python e Separação de Responsabilidades", [
        ("• orquestrador.py:", "Orquestrador principal que controla a execução das 3 fases do processo."),
        ("• processo_atendimento/leitor_email.py:", "Conecta à caixa IMAP4_SSL, busca e-mails não lidos (UNSEEN) e baixa PDFs."),
        ("• processo_atendimento/validador_docs.py:", "Executa a validação do PDF unificado via pypdf confirmando a integridade dos 3 documentos."),
        ("• processo_atendimento/gestor_arquivos.py:", "Gerencia o sistema de arquivos local do ERP e aciona a sincronização em nuvem."),
        ("• processo_atendimento/gestor_drive.py:", "Autentica via Google Drive API v3 e realiza a criação/movimentação remota de pastas."),
        ("• processo_atendimento/resposta_cliente.py:", "Envia notificações em HTML responsivo via SMTP (Solicitação e Confirmação/Pendência)."),
        ("• processo_atendimento/portal_integracao.py:", "Automação Web via Playwright para cadastro e atualização de status no Portal Fake ERP.")
    ])

    add_footer(slide7, 7)

    # ==========================================
    # SLIDE 8: STACK TECNOLÓGICO SELECIONADO
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8, LIGHT_BG)
    add_header(slide8, "Stack Tecnológico Escolhido & Justificativas", "BLOCO 2 — ARQUITETURA & CORE", "Daniele & Kauã")

    add_card(slide8, 0.6, 1.4, 5.8, 5.2, "Tecnologias de Automação & RPA", [
        ("• Python 3.10:", "Linguagem base de alta produtividade, suporte a bibliotecas maduras e ecossistema robusto."),
        ("• Playwright:", "Automação Web de última geração, execução ultra-rápida em Chromium headless e suporte a screenshots."),
        ("• BotCity Maestro SDK:", "Orquestração na nuvem, controle de execução, postagem de artefatos e logs centralizados.")
    ])

    add_card(slide8, 6.8, 1.4, 5.8, 5.2, "Tecnologias de Integração & Documentos", [
        ("• Google Drive API v3:", "Integração oficial via google-api-python-client e google-auth-oauthlib."),
        ("• pypdf & python-docx:", "Manipulação avançada de PDFs e geração dinâmica de fichas cadastrais em Word."),
        ("• imaplib & smtplib:", "Protocolos padrão para conexão segura SSL a servidores de e-mail corporativos (Gmail).")
    ])

    add_footer(slide8, 8)

    # ==========================================
    # SLIDE 9: FASE 1: GERAÇÃO DE FICHA & DISPARO
    # ==========================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9, LIGHT_BG)
    add_header(slide9, "FASE 1: Geração da Ficha (.docx) & Solicitação SMTP", "BLOCO 2 — ARQUITETURA & CORE", "Daniele & Kauã")

    add_card(slide9, 0.6, 1.4, 5.8, 5.2, "Geração Dinâmica do Documento Word", [
        ("• Módulo de Suporte:", "common/documento_email.py (função criar_documento)."),
        ("• Extração Dinâmica:", "Robô lê os dados cadastrais do cliente no Portal Fake ou base de entrada."),
        ("• Template Automático:", "Preenche a Ficha Cadastral padronizada em formato .docx com Nome, CPF, Telefone, E-mail e Endereço."),
        ("• Status Inicial:", "Marca o status da ficha como 'AGUARDANDO ASSINATURA E DOCUMENTOS'.")
    ])

    add_card(slide9, 6.8, 1.4, 5.8, 5.2, "Disparo de E-mail de Solicitação", [
        ("• Módulo de Envio:", "processo_atendimento/resposta_cliente.py."),
        ("• Protocolo Único:", "Gera protocolo único de atendimento no formato #YYYY-XXXX."),
        ("• E-mail HTML Responsivo:", "Envia o e-mail anexando a Ficha DOCX e instruindo o cliente a retornar o PDF Único com a ficha assinada e documentos com foto.")
    ])

    add_footer(slide9, 9)

    # ==========================================
    # SLIDE 10: FASE 2: LEITOR IMAP & ANEXOS
    # ==========================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10, LIGHT_BG)
    add_header(slide10, "FASE 2: Leitor de E-mails IMAP & Extração de PDFs", "BLOCO 2 — ARQUITETURA & CORE", "Daniele & Kauã")

    add_card(slide10, 0.6, 1.4, 5.8, 5.2, "Monitoramento Inteligente via IMAP", [
        ("• Conexão SSL:", "imaplib.IMAP4_SSL com login seguro em imap.gmail.com."),
        ("• Busca Seletiva:", "Filtro estrito por e-mails NÃO LIDOS (UNSEEN) contendo 'Assinatura' ou 'Ficha' no assunto."),
        ("• Prevenção de Duplicidade:", "Aplica a flag \\Seen no servidor IMAP imediatamente após o download para evitar reprocessamento duplicado.")
    ])

    add_card(slide10, 6.8, 1.4, 5.8, 5.2, "Extração e Salvamento de Anexos", [
        ("• Módulo:", "processo_atendimento/leitor_email.py."),
        ("• Extração de PDF:", "Decodifica headers de e-mail e salva o PDF unificado retornado pelo cliente."),
        ("• Pasta de Entrada:", "Armazena o arquivo diretamente em ERP_Portal_Fake/Downloads/."),
        ("• Trigger no Drive:", "Dispara o upload automático para a pasta 'Downloads' no Google Drive.")
    ])

    add_footer(slide10, 10)

    # ==========================================
    # SLIDE 11: FASE 3: VALIDADOR DOCUMENTAL
    # ==========================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11, LIGHT_BG)
    add_header(slide11, "FASE 3: Validador Documental Inteligente (pypdf)", "BLOCO 2 — ARQUITETURA & CORE", "Daniele & Kauã")

    add_card(slide11, 0.6, 1.4, 5.8, 5.2, "Inspeção Automatizada de PDFs com pypdf", [
        ("• Módulo:", "processo_atendimento/validador_docs.py."),
        ("• Checagem de Tamanho:", "Rejeita arquivos corrompidos ou com 0 bytes."),
        ("• Inspeção de Conteúdo:", "Lê o texto interno das páginas do PDF buscando palavras-chave obrigatórias: 'Ficha Cadastral', 'Assinada', 'Identidade/RG/CPF' e 'Comprovante/Residência'.")
    ])

    add_card(slide11, 6.8, 1.4, 5.8, 5.2, "Decisão de Aprovação vs Pendência", [
        ("• Caso APROVADO:", "Move PDF para 'Documentos_OK', executa cadastro Playwright, move para 'Encaminhados' e envia e-mail de aprovação em HTML."),
        ("• Caso REPROVADO:", "Move PDF para 'Documentos_Pendentes' e envia e-mail em HTML notificando as pendências exatas ao cliente.")
    ])

    add_footer(slide11, 11)

    # ==========================================
    # SLIDE 12: ESTRUTURA DE PASTAS DO ERP
    # ==========================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12, LIGHT_BG)
    add_header(slide12, "Estrutura de Pastas do ERP Simulado", "BLOCO 3 — ERP, DRIVE & DEVOPS", "Sannyer C. Nery")

    add_card(slide12, 0.6, 1.4, 12.0, 5.2, "Gerenciador de Arquivos ERP (gestor_arquivos.py)", [
        ("1. Downloads/:", "Pasta de entrada onde todos os novos PDFs baixados da caixa de e-mail são depositados."),
        ("2. Documentos_OK/:", "Pasta intermediária para arquivos cujos PDFs foram validados e aprovados pelas regras de negócio."),
        ("3. Documentos_Pendentes/:", "Pasta de retenção para documentos reprovados ou com inconsistências (aguardando novo envio)."),
        ("4. Encaminhados/:", "Pasta final do setor onde ficam armazenados os cadastros ativos concluídos e encaminhados ao próximo setor."),
        ("• Sincronismo Físico/Nuvem:", "Cada operação shutil.move() executada localmente invoca automaticamente o gestor_drive.mover_arquivo().")
    ])

    add_footer(slide12, 12)

    # ==========================================
    # SLIDE 13: INTEGRAÇÃO GOOGLE DRIVE API V3
    # ==========================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide13, LIGHT_BG)
    add_header(slide13, "Integração Avançada com Google Drive API v3", "BLOCO 3 — ERP, DRIVE & DEVOPS", "Sannyer C. Nery")

    add_card(slide13, 0.6, 1.4, 5.8, 5.2, "Módulo GestorDrive (gestor_drive.py)", [
        ("• Mapeamento Automático:", "Localiza a pasta raiz ERP_Portal_Fake e garante a criação/mapeamento das 4 subpastas no Drive."),
        ("• Mapeamento por ID:", "Suporte à variável GOOGLE_DRIVE_FOLDER_ID no .env para vincular diretamente à pasta compartilhada pelo usuário."),
        ("• Suporte a Drives Compartilhados:", "Inclusão de supportsAllDrives=True e includeItemsFromAllDrives=True em todas as requisições API.")
    ])

    add_card(slide13, 6.8, 1.4, 5.8, 5.2, "Movimentação Remota Inteligente", [
        ("• Atualização de Parents:", "Utiliza a API files().update(addParents=..., removeParents=...) para mover arquivos entre pastas sem recriá-los."),
        ("• Rastreamento por Nome:", "Localiza arquivos no Drive por query de nome e ID do pai com suporte a buscas globais de fallback.")
    ])

    add_footer(slide13, 13)

    # ==========================================
    # SLIDE 14: RESOLUÇÃO DESAFIO COTA DRIVE
    # ==========================================
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide14, LIGHT_BG)
    add_header(slide14, "Resolução do Desafio Técnico: Cota 0MB no Drive", "BLOCO 3 — ERP, DRIVE & DEVOPS", "Sannyer C. Nery")

    add_card(slide14, 0.6, 1.4, 5.8, 5.2, "Diagnóstico do Erro HTTP 403 Google API", [
        ("• Causa Raiz:", "Service Accounts possuem COTA ZERO (0 MB) em drives pessoais @gmail.com."),
        ("• Comportamento da API:", "Quando a Service Account criava um arquivo novo em pasta compartilhada, o Google atribuía a posse do arquivo à Service Account, gerando o erro storageQuotaExceeded."),
        ("• Solução Arquitetural:", "Projetou-se o robô com arquitetura híbrida de autenticação.")
    ])

    add_card(slide14, 6.8, 1.4, 5.8, 5.2, "Solução Híbrida & Fallback de Upload", [
        ("• Suporte Duplo:", "O GestorDrive suporta nativamente tanto Service Account quanto OAuth 2.0 Client ID (gerando token.json automático com os 15GB da conta do usuário)."),
        ("• Fallback de Upload:", "Se o arquivo a mover não for localizado no Drive, o robô executa upload_arquivo() de fallback automaticamente.")
    ])

    add_footer(slide14, 14)

    # ==========================================
    # SLIDE 15: AUTOMAÇÃO WEB PLAYWRIGHT
    # ==========================================
    slide15 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide15, LIGHT_BG)
    add_header(slide15, "Automação Web no Portal Fake (Playwright)", "BLOCO 3 — ERP, DRIVE & DEVOPS", "Sannyer C. Nery")

    add_card(slide15, 0.6, 1.4, 5.8, 5.2, "Integração RPA no Portal ERP (portal_integracao.py)", [
        ("• Execução de Alta Velocidade:", "Executa via Playwright Chromium em modo Headless (ou gráfico com --no-headless)."),
        ("• Preenchimento Cadastral:", "Preenche campos de Nome, Sobrenome, CPF, E-mail, Telefone, Nascimento, Endereço e Observações."),
        ("• Atualização de Status:", "Muda o status do cadastro do cliente para 'ATIVO' no Portal Fake ERP.")
    ])

    add_card(slide15, 6.8, 1.4, 5.8, 5.2, "Auditoria Visual por Screenshots", [
        ("• Screenshots de Evidência:", "Gera imagens 01_portal_preenchido.png e 02_extracao_dados.png."),
        ("• Integração Maestro:", "Posta automaticamente as screenshots como artefatos no painel do BotCity Maestro.")
    ])

    add_footer(slide15, 15)

    # ==========================================
    # SLIDE 16: ORQUESTRADOR & GITFLOW
    # ==========================================
    slide16 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide16, LIGHT_BG)
    add_header(slide16, "Orquestrador Principal & Governança GitFlow", "BLOCO 3 — ERP, DRIVE & DEVOPS", "Sannyer C. Nery")

    add_card(slide16, 0.6, 1.4, 5.8, 5.2, "Orquestrador Geral (orquestrador.py)", [
        ("• Modos de Execução CLI:", "enviar_solicitacoes (Fase 1), processar_retornos (Fases 2 e 3) e demo_completo (Integração total)."),
        ("• BotCity Maestro SDK:", "Suporte a execuções agendadas na nuvem, captura de parâmetros via Runner e controle de tarefas.")
    ])

    add_card(slide16, 6.8, 1.4, 5.8, 5.2, "Governança DevOps & GitFlow", [
        ("• Estrutura de Branches:", "main (produção), develop (integração contínua), feature/* (funcionalidades) e release/2.0."),
        ("• Proteção de Segredos:", "Isolamento rigoroso de credenciais (.env, credentials.json, token.json) no .gitignore evitou vazamentos no GitHub.")
    ])

    add_footer(slide16, 16)

    # ==========================================
    # SLIDE 17: EVIDÊNCIAS: LOGS DO TERMINAL
    # ==========================================
    slide17 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide17, LIGHT_BG)
    add_header(slide17, "Evidências Práticas: Logs Reais de Execução", "BLOCO 4 — DEMONSTRAÇÃO & RESULTADOS", "Equipe Integrada")

    log_box = slide17.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.4), Inches(12.0), Inches(5.2))
    log_box.fill.solid()
    log_box.fill.fore_color.rgb = DARK_GREY
    log_box.line.color.rgb = LG_RED
    log_box.line.width = Pt(1.5)

    tf_log = log_box.text_frame
    tf_log.word_wrap = True
    tf_log.margin_left = Inches(0.2)
    tf_log.margin_top = Inches(0.2)

    log_txt = (
        "===========================================================================\n"
        "INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION - PROCESSO 1 (MODO: DEMO_COMPLETO)\n"
        "===========================================================================\n"
        "[Etapa 0] Inicializando Módulos do Processo 1...\n"
        "[GESTOR ARQUIVOS] Estrutura de pastas local garantida em: .../ERP_Portal_Fake\n"
        "[GESTOR DRIVE] Autenticado com sucesso via Service Account!\n"
        "[GESTOR DRIVE] Usando ID configurado para a pasta raiz 'ERP_Portal_Fake': 1_AMktNc_sXyN9GWkjVVV1a2fuYPtKQ7w\n"
        "[GESTOR DRIVE] Estrutura de pastas no Google Drive pronta: ['ERP_Portal_Fake', 'Downloads', 'Documentos_OK', 'Documentos_Pendentes', 'Encaminhados']\n\n"
        "[FASE 1] GERAÇÃO E ENVIO DE FICHA PARA ASSINATURA (Ana Silva) | Protocolo: #2026-0001\n"
        "  [FASE 1] Ficha DOCX gerada: Ficha_Cadastro_11122233344.docx\n"
        "  [FASE 1] E-mail de solicitação de assinatura enviado com sucesso.\n\n"
        "[FASE 2 & 3] MONITORAMENTO DO RETORNO, VALIDAÇÃO E CADASTRO (Ana Silva)\n"
        "  [LEITOR EMAIL] Encontrados 1 novos e-mails não lidos de retorno.\n"
        "  [VALIDAÇÃO] Documentação e Ficha Assinada APROVADAS para Ana Silva.\n"
        "[GESTOR ARQUIVOS] Arquivo 'Ficha_Assinada_Ana_Silva.pdf' movido para 'Documentos_OK'.\n"
        "[GESTOR DRIVE] Arquivo movido de 'Downloads' para 'Documentos_OK' no Google Drive!\n"
        "[PORTAL INTEGRAÇÃO] Cadastrando cliente Ana Silva (CPF: 11122233344) no Portal Fake...\n"
        "[PORTAL INTEGRAÇÃO] Cadastro de 'Ana' concluído com sucesso (Status: ATIVO).\n"
        "[GESTOR ARQUIVOS] Arquivo movido para 'Encaminhados'.\n"
        "[GESTOR DRIVE] Arquivo movido de 'Documentos_OK' para 'Encaminhados' no Google Drive!\n"
        "===========================================================================\n"
        "ORQUESTRAÇÃO DO PROCESSO 1 FINALIZADA COM SUCESSO!"
    )
    p_l = tf_log.paragraphs[0]
    p_l.text = log_txt
    p_l.font.name = 'Courier New'
    p_l.font.size = Pt(8.5)
    p_l.font.color.rgb = WHITE

    add_footer(slide17, 17)

    # ==========================================
    # SLIDE 18: EVIDÊNCIA 1 - PORTAL FAKE PREENCHIDO
    # ==========================================
    slide18 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide18, LIGHT_BG)
    add_header(slide18, "Evidência 1: Interface Web do Portal Fake ERP (Preenchimento RPA)", "BLOCO 4 — DEMONSTRAÇÃO & RESULTADOS", "Equipe Integrada")

    img1_path = Path(__file__).resolve().parents[1] / "HyperAutomation" / "resources" / "screenshots" / "01_portal_preenchido.png"
    if img1_path.exists():
        slide18.shapes.add_picture(str(img1_path), Inches(0.6), Inches(1.4), width=Inches(7.8))

    add_card(slide18, 8.6, 1.4, 4.1, 5.2, "🤖 Automação Web Playwright", [
        ("• Interface do Portal ERP:", "Visão geral da tabela de cadastros mantida no Portal Fake Soluções Digitais."),
        ("• Execução de Alta Velocidade:", "Preenchimento e sincronização dinâmica em massa executados via Chromium Headless."),
        ("• Validação em Tela:", "Verificação de campos obrigatórios e integridade das linhas de cadastro."),
        ("• Rastreabilidade:", "Captura de tela automatizada no encerramento da carga inicial do sistema.")
    ])

    add_footer(slide18, 18, total_pages=24)

    # ==========================================
    # SLIDE 19: EVIDÊNCIA 2 - FORMULÁRIO E ATIVAÇÃO DE CADASTRO
    # ==========================================
    slide19 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide19, LIGHT_BG)
    add_header(slide19, "Evidência 2: Formulário e Ativação de Cadastro no ERP", "BLOCO 4 — DEMONSTRAÇÃO & RESULTADOS", "Equipe Integrada")

    img2_path = Path(__file__).resolve().parents[1] / "HyperAutomation" / "resources" / "screenshots" / "02_extracao_dados.png"
    if img2_path.exists():
        slide19.shapes.add_picture(str(img2_path), Inches(0.6), Inches(1.4), width=Inches(7.8))

    add_card(slide19, 8.6, 1.4, 4.1, 5.2, "✅ Ativação de Cadastro", [
        ("• Modal de Novo Cadastro:", "Formulário cadastral preenchido automaticamente com os dados extraídos do cliente."),
        ("• Transição de Status:", "Cliente ativado no ERP com a transição automática do estado para 'ATIVO' após validação documental."),
        ("• Registro de Atendimento:", "Inclusão de observações auditáveis informando o atendimento automatizado."),
        ("• Screenshot de Evidência:", "Registro armazenado e enviado como artefato ao BotCity Maestro.")
    ])

    add_footer(slide19, 19, total_pages=24)

    # ==========================================
    # SLIDE 20: EVIDÊNCIA 3 - CONFIRMAÇÃO DE SUCESSO DE E-MAIL
    # ==========================================
    slide20 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide20, LIGHT_BG)
    add_header(slide20, "Evidência 3: Confirmação de Cadastro Aprovado (E-mail HTML)", "BLOCO 4 — DEMONSTRAÇÃO & RESULTADOS", "Equipe Integrada")

    img_suc = Path(__file__).resolve().parents[1] / "img" / "sucesso.png"
    if img_suc.exists():
        slide20.shapes.add_picture(str(img_suc), Inches(0.6), Inches(1.4), width=Inches(7.8))

    add_card(slide20, 8.6, 1.4, 4.1, 5.2, "✅ E-mail de Aprovação", [
        ("• Validação Documental:", "100% Aprovado."),
        ("• Análise do PDF:", "Ficha Cadastral Assinada, Documento com Foto e Comprovante de Residência validados via pypdf."),
        ("• Automação Web:", "Cadastro ativado no Portal Fake ERP como 'ATIVO' via Playwright."),
        ("• Gestão de Arquivos:", "Arquivo transferido para 'Documentos_OK' e depois 'Encaminhados' (local e Google Drive)."),
        ("• Notificação:", "Disparo instantâneo do e-mail em HTML responsivo com protocolo único de aprovação.")
    ])

    add_footer(slide20, 20, total_pages=24)

    # ==========================================
    # SLIDE 21: EVIDÊNCIA 4 - PENDÊNCIA: FALTA DOC COM FOTO
    # ==========================================
    slide21 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide21, LIGHT_BG)
    add_header(slide21, "Evidência 4: Pendência — Falta Documento Oficial com Foto", "BLOCO 4 — DEMONSTRAÇÃO & RESULTADOS", "Equipe Integrada")

    img_foto = Path(__file__).resolve().parents[1] / "img" / "falha_faltou_documento_foto.png"
    if img_foto.exists():
        slide21.shapes.add_picture(str(img_foto), Inches(0.6), Inches(1.4), width=Inches(7.8))

    add_card(slide21, 8.6, 1.4, 4.1, 5.2, "⚠️ Pendência: Doc. Foto", [
        ("• Validação Documental:", "Reprovado por Pendência."),
        ("• Inconsistência Detectada:", "Ausência de Documento Oficial de Identificação com Foto (RG / CPF) no PDF enviado."),
        ("• Gestão de Arquivos:", "PDF retido e movido para a pasta 'Documentos_Pendentes' no ERP local e no Google Drive."),
        ("• Notificação Automática:", "Disparo imediato de e-mail em HTML orientando o cliente sobre o reenvio exato da identidade com foto.")
    ])

    add_footer(slide21, 21, total_pages=24)

    # ==========================================
    # SLIDE 22: EVIDÊNCIA 5 - PENDÊNCIA: FALTA COMPROVANTE DE RESIDÊNCIA
    # ==========================================
    slide22 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide22, LIGHT_BG)
    add_header(slide22, "Evidência 5: Pendência — Falta Comprovante de Residência", "BLOCO 4 — DEMONSTRAÇÃO & RESULTADOS", "Equipe Integrada")

    img_res = Path(__file__).resolve().parents[1] / "img" / "falha_falta-comprovante-residencia.png"
    if img_res.exists():
        slide22.shapes.add_picture(str(img_res), Inches(0.6), Inches(1.4), width=Inches(7.8))

    add_card(slide22, 8.6, 1.4, 4.1, 5.2, "⚠️ Pendência: Residência", [
        ("• Validação Documental:", "Reprovado por Pendência."),
        ("• Inconsistência Detectada:", "Ausência do Comprovante de Residência (fatura de água/luz/endereço) no PDF retornado."),
        ("• Gestão de Arquivos:", "PDF movido para 'Documentos_Pendentes' no ERP e espelhado no Google Drive."),
        ("• Notificação Automática:", "Envio de e-mail em HTML responsivo solicitando a regularização do comprovante residencial.")
    ])

    add_footer(slide22, 22, total_pages=24)

    # ==========================================
    # SLIDE 22: TABELA COMPARATIVA DE GANHOS
    # ==========================================
    slide22 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide22, LIGHT_BG)
    add_header(slide22, "Métricas de Sucesso & Tabela Comparativa de Ganhos", "BLOCO 4 — DEMONSTRAÇÃO & RESULTADOS", "Equipe Integrada")

    # Table
    tbl = slide22.shapes.add_table(rows=5, cols=4, left=Inches(0.6), top=Inches(1.4), width=Inches(12.0), height=Inches(4.5)).table
    
    headers = ["Métrica de Desempenho", "Processo Manual (AS-IS)", "Processo Automatizado (TO-BE)", "Ganho / Melhoria Obtida"]
    for idx, h in enumerate(headers):
        cell = tbl.cell(0, idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = LG_RED
        for p in cell.text_frame.paragraphs:
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = WHITE
                r.font.size = Pt(12)

    rows_data = [
        ("Tempo Médio por Atendimento", "15 a 20 minutos por cliente", "Aproximadamente 5 segundos", "⚡ Redução de 99.5% no tempo de processamento"),
        ("Taxa de Erro na Triagem", "12% a 15% (falha humana)", "0% (regras de negócio estritas)", "🎯 Eliminação total de cadastros com dados/docs incompletos"),
        ("Organização de Arquivos", "Dispersos localmente sem padrão", "Sincronizados local e no Google Drive", "☁️ 100% dos arquivos padronizados e rastreáveis na nuvem"),
        ("Comunicação com Cliente", "E-mails manuais sem padronização", "Templates HTML automatizados", "✉️ Notificação instantânea com protocolo único em todas as fases")
    ]

    for row_idx, data in enumerate(rows_data, start=1):
        for col_idx, text in enumerate(data):
            cell = tbl.cell(row_idx, col_idx)
            cell.text = text
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if row_idx % 2 == 1 else CARD_BG
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(11)
                    r.font.color.rgb = DARK_GREY
                    if col_idx == 0 or col_idx == 3:
                        r.font.bold = True

    add_footer(slide22, 22, total_pages=23)

    # ==========================================
    # SLIDE 23: CONCLUSÃO E ENCERRAMENTO
    # ==========================================
    slide23 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide23, LIGHT_BG)
    add_header(slide23, "Conclusão & Defesa do Projeto", "BLOCO 4 — DEMONSTRAÇÃO & RESULTADOS", "Equipe Integrada")

    add_card(slide23, 0.6, 1.4, 5.8, 5.2, "Atendimento a 100% dos Requisitos do Roteiro 10", [
        ("✅ Modelagem BPMN 2.0:", "Processo 1 totalmente mapeado no Draw.io."),
        ("✅ Automação Integrada:", "Solução acoplada perfeitamente ao projeto preexistente."),
        ("✅ Validação Inteligente:", "Inspeção de conteúdo em PDFs via pypdf."),
        ("✅ Sincronização em Nuvem:", "Integração nativa com Google Drive API v3."),
        ("✅ Governança de Código:", "Repositório GitHub organizado com metodologia GitFlow.")
    ])

    add_card(slide23, 6.8, 1.4, 5.8, 5.2, "Muito Obrigado! Pergunta & Resposta (Q&A)", [
        ("• Equipe 1:", "Eric Luna Costa, Daniele Greice, Kauã Sales e Sannyer Cardoso."),
        ("• Professor:", "Prof. Moisés Levy | Disciplina: Técnicas de Hyperautomation."),
        ("• Instituição:", "PÓLO DE INOVAÇÃO IFAM / FAEPI / LG."),
        ("• Espaço Aberto:", "Estamos à disposição da banca para dúvidas e demonstração ao vivo!")
    ])

    add_footer(slide23, 23, total_pages=23)

    # Save presentation
    output_pptx = Path(__file__).resolve().parent / "Apresentacao_Hyperautomation_Processo1_LG.pptx"
    prs.save(str(output_pptx))
    print(f"Apresentação PowerPoint gerada com sucesso: {output_pptx}")
    return output_pptx

if __name__ == "__main__":
    create_presentation()
