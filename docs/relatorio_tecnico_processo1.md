# 📜 Relatório Técnico - Automação do Processo 1 (Setor de Atendimento)
**Empresa Portal Fake | Roteiro 10 - Disciplina de Técnicas de Hyperautomation**
**Professor:** Prof. Moisés Levy

---

## 👥 1. Identificação da Equipe e Responsabilidades

* **Integrante 1:** Responsável pela Modelagem BPMN (`Processo01_Atendimento.drawio`), Módulo de Leitura/Monitoramento de E-mails (`leitor_email.py`), Validador Documental de Retorno (`validador_docs.py`) e Automação Playwright no Portal Fake (`portal_integracao.py`).
* **Integrante 2 (Sannyer Carvalho):** Responsável pela Gestão de Versões (GitFlow), Estruturação das Pastas ERP (`ERP_Portal_Fake`), Gestor de Arquivos (`gestor_arquivos.py`), Notificador Transacional HTML de Envio de Ficha e Confirmação (`resposta_cliente.py`), Orquestração Integrada (`orquestrador.py`) e Redação do Relatório Técnico.

---

## 🗺️ 2. Modelagem do Processo em BPMN 2.0 (Ciclo de Atendimento & Assinatura)

O **Processo 1 (Setor de Atendimento)** foi modelado visualmente no Draw.io (`docs/Processo01_Atendimento.drawio`) e contempla o ciclo completo de envio da ficha para assinatura e monitoramento do e-mail de retorno do cliente.

### Diagrama do Fluxo de Atendimento:
```mermaid
flowchart TD
    A([Início: Solicitação de Cadastro/Atendimento]) --> B[Gerar Ficha Cadastral Word '.docx'\n'criar_documento']
    B --> C[Enviar E-mail com Ficha para Assinatura\n'resposta_cliente.py']
    
    C --> D[Monitorar E-mail de Retorno do Cliente\n'leitor_email.py' -> Salva em 'ERP_Portal_Fake/Downloads']
    D --> E[Validação do PDF Único (Ficha Assinada + Documentos)\n'validador_docs.py']
    
    E -->|Documentação Incompleta / Não Assinada| F[Mover PDF para 'Documentos_Pendentes'\n'gestor_arquivos.py']
    F --> G[Enviar E-mail HTML de Pendência\n'resposta_cliente.py']
    G --> H([Fim: Aguardando Reenvio do Cliente])

    E -->|Ficha Assinada & PDF Válidos| I[Mover PDF para 'Documentos_OK'\n'gestor_arquivos.py']
    I --> J[Cadastrar/Atualizar Cliente no Portal Fake ERP\n'portal_integracao.py' via Playwright]
    J --> K[Mover PDF para 'Encaminhados'\n'gestor_arquivos.py']
    K --> L[Enviar E-mail HTML de Confirmação e Aprovação\n'resposta_cliente.py']
    L --> M([Fim: Cadastro Concluído e Encaminhado])
```

---

## 🛠️ 3. Arquitetura da Solução e Estrutura de Pastas

A arquitetura adota o padrão **Modular por Processo**, separando as responsabilidades em submódulos reutilizáveis:

```text
hyperautomation-equipe-1/
├── ERP_Portal_Fake/                  # Estrutura do ERP Simulado (Pastas Físicas)
│   ├── Downloads/                    # Entrada de anexos retornado pelos clientes (PDF Único)
│   ├── Documentos_OK/                # Documentos e fichas assinadas validadas
│   ├── Documentos_Pendentes/         # Documentos com inconsistências ou sem assinatura
│   └── Encaminhados/                 # Documentos processados e cadastrados no portal
├── docs/                             # Documentação do Projeto
│   ├── Processo01_Atendimento.drawio # Diagrama BPMN 2.0 no Draw.io
│   └── relatorio_tecnico_processo1.md# Este relatório técnico
└── HyperAutomation/                  # Módulos Python e Orquestração
    ├── source/
    │   ├── .env                      # Variáveis de ambiente (Credenciais SMTP/IMAP e ERP)
    │   ├── orquestrador.py           # Orquestrador do fluxo completo (Processo 1)
    │   ├── common/                   # Módulos reutilizáveis (extração e geração docx)
    │   │   ├── documento_email.py
    │   │   └── extracao.py
    │   └── processo_atendimento/     # Módulos do Processo 1
    │       ├── __init__.py
    │       ├── gestor_arquivos.py    # Movimentação física no ERP
    │       ├── resposta_cliente.py   # Notificações de e-mail (Solicitação de Assinatura e Retorno)
    │       ├── leitor_email.py       # Monitoramento IMAP e extração dos PDFs de retorno
    │       ├── validador_docs.py     # Validador de integridade da Ficha Assinada + PDF Único
    │       └── portal_integracao.py  # Automação Web via Playwright
    ├── requirements.txt              # Lista de dependências Python
    ├── bot.yaml                      # Manifesto BotCity Maestro
    └── pack_bot.py                   # Script de empacotamento para publicação
```

---

## 🧰 4. Detalhamento das Fases do Processo

### 4.1. FASE 1: Geração da Ficha e Solicitação de Assinatura
* O robô extrai os dados do cliente e gera a **Ficha Cadastral em `.docx`**.
* O `resposta_cliente.py` envia um e-mail inicial em HTML instruindo o cliente a imprimir/assinar a ficha, anexar seus documentos e retornar tudo em um **ÚNICO arquivo PDF**.

### 4.2. FASE 2: Monitoramento da Caixa de Entrada (`leitor_email.py`)
* O robô monitora a caixa de e-mails via **IMAP4_SSL** buscando mensagens de retorno com assunto de assinatura.
* Extrai o PDF unificado enviado pelo cliente e salva em `ERP_Portal_Fake/Downloads/`.

### 4.3. FASE 3: Validação Documental e Automação Web
* **`validador_docs.py`**: Valida a presença do PDF, checa integridade (> 0 bytes) e confirma a entrega da Ficha Assinada.
* **`gestor_arquivos.py`**: Move o PDF de `Downloads` para `Documentos_OK` (se válido) ou `Documentos_Pendentes` (se reprovado).
* **`portal_integracao.py`**: Interage com o Portal Fake via **Playwright**, realizando o cadastro definitivo do cliente.
* **`gestor_arquivos.py`**: Move o PDF de `Documentos_OK` para `Encaminhados`.
* **`resposta_cliente.py`**: Envia o e-mail final informando a conclusão e aprovação do cadastro.

---

## 🌿 5. Gestão de Versões e DevOps (GitFlow)

O projeto foi organizado sob a metodologia **GitFlow**:

* `main`: Branch de produção com versão estável homologada.
* `develop`: Branch de integração contínua.
* `feature/atendimento-email-validacao`: Funcionalidades de monitoramento e validação documental.
* `feature/atendimento-gestao-orquestrador`: Gestão de arquivos, notificações HTML e orquestração.
* `release/2.0`: Preparação e testes finais da entrega do Roteiro 10.
* **Tag `v2.0`**: Marcação da versão oficial de entrega.

---

## 📊 6. Evidências de Execução Integrada (Orquestrador)

Saída real obtida durante a execução do `orquestrador.py`:

```text
===========================================================================
INICIANDO ORQUESTRAÇÃO HYPERAUTOMATION - PROCESSO 1 (CICLO COMPLETO DE ATENDIMENTO)
===========================================================================

[Etapa 0] Inicializando Módulos do Processo 1...
[GESTOR ARQUIVOS] Estrutura de pastas garantida em: .../ERP_Portal_Fake

[FASE 1] Gerando Ficha de Dados para Assinatura e enviando solicitação ao cliente...
  Ficha DOCX gerada para assinatura: Ficha_Cadastro_11122233344.docx
  E-mail de solicitação de assinatura enviado.

[FASE 2] Monitorando e-mail de retorno do cliente (Ficha Assinada + Documentos em PDF Único)...
  [LEITOR EMAIL] Monitoramento encontrou e-mail de retorno do cliente com PDF Único...
  E-mails de retorno identificados: 1

[FASE 3] Conectando ao Portal Fake ERP: file://.../index.html
  [RPA Preenchimento] Sucesso! 5 cadastros inseridos no portal.
  [SCREENSHOT] Salvo: 01_portal_preenchido.png

[Processando Retorno 1/1] Cliente: Ana Silva | Protocolo: #2026-0001
  Anexos salvos em ERP_Portal_Fake/Downloads: ['Ficha_Assinada_e_Documentos_Ana_Silva.pdf']
[VALIDADOR DOCS] Validação de retorno concluída. Aprovado: True. Pendências: 0
  [VALIDAÇÃO] Documentação e Ficha Assinada APROVADAS para Ana Silva.
[GESTOR ARQUIVOS] Arquivo 'Ficha_Assinada_e_Documentos_Ana_Silva.pdf' movido para 'Documentos_OK'.
[PORTAL INTEGRAÇÃO] Cadastrando cliente: Ana Silva (CPF: 11122233344)
[PORTAL INTEGRAÇÃO] Cadastro de 'Ana' concluído com sucesso.
[GESTOR ARQUIVOS] Arquivo 'Ficha_Assinada_e_Documentos_Ana_Silva.pdf' movido para 'Encaminhados'.
  [SCREENSHOT] Salvo: 02_extracao_dados.png

===========================================================================
ORQUESTRAÇÃO DO PROCESSO 1 FINALIZADA COM SUCESSO!
===========================================================================
```

---

## 🏁 7. Conclusão

A automação do **Processo 1 (Setor de Atendimento)** atende perfeitamente ao ciclo completo de negócio: geração e envio da ficha de dados para assinatura, monitoramento inteligente da caixa de retorno de e-mails, validação documental dos PDFs únicos retornados, movimentação segura nas pastas do ERP e cadastramento automatizado via Playwright.
