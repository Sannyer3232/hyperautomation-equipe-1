# RELATÓRIO TÉCNICO DE HYPERAUTOMATION
## PROCESSO 1: SETOR DE ATENDIMENTO — EMPRESA PORTAL FAKE

**Disciplina:** Técnicas de Hyperautomation  
**Professor:** Prof. Moisés Levy  
**Empresa Alvo:** Portal Fake Soluções Digitais  
**Versão do Projeto:** 2.0 (`release/2.0` / Tag `v2.0`)  
**Data:** Julho de 2026  

---

### 👥 Integrantes e Divisão de Responsabilidades

| Integrante | Papel no Projeto | Responsabilidades Principais |
| :--- | :--- | :--- |
| **Integrante 1** | Desenvolvimento de Automação & Modelagem BPMN | • Modelagem do processo em BPMN no Draw.io (`Processo01_Atendimento.drawio` / `.png`).<br>• Módulo `leitor_email.py` (Leitura de e-mails e download de anexos).<br>• Módulo `validador_docs.py` (Aplicação das regras de validação documental).<br>• Módulo `portal_integracao.py` (Automação Playwright para preencher/encaminhar no Portal). |
| **Integrante 2 (Sannyer Carvalho)** | DevOps, Gestão de ERP, Notificação & Documentação | • Gestão de versão e repositório via **GitFlow** (`main`, `develop`, `feature/*`, `release/2.0`).<br>• Estruturação e simulação do ERP (`ERP_Portal_Fake/`).<br>• Módulo `gestor_arquivos.py` (Gerenciamento físico e movimentação de arquivos).<br>• Módulo `resposta_cliente.py` (Notificação via e-mail em HTML responsivo).<br>• Integração no `orquestrador.py` e redação do Relatório Técnico. |

---

## 1. 📌 Contexto Geral e Objetivos

O projeto consiste na evolução da solução de Hyperautomation desenvolvida para a **Empresa Portal Fake Soluções Digitais**, expandindo a capacidade operacional por meio da automação do **Processo 1 (Setor de Atendimento)**.

### Objetivos Principais:
1. **Redução de Intervenção Manual**: Automatizar a triagem de e-mails, validação documental, cadastro no ERP e notificação aos clientes.
2. **Rastreabilidade e Organização no ERP**: Garantir que todos os documentos transitem de forma segura entre as pastas do ERP Simulado (`Downloads` ➔ `Documentos_OK` / `Documentos_Pendentes` ➔ `Encaminhados`).
3. **Comunicação Transparente ao Cliente**: Disparar e-mails formatados em HTML com protocolo de atendimento e detalhamento de aprovação ou pendências.
4. **Governança e DevOps**: Manter a estabilidade do código via **GitFlow** e permitir execução via **BotCity Maestro**.

---

## 2. 🗺️ Modelagem do Processo em BPMN

O fluxo do **Processo 1 (Setor de Atendimento)** foi modelado utilizando o padrão **BPMN 2.0** no Draw.io (`docs/Processo01_Atendimento.drawio`).

### Diagrama do Fluxo (Resumo da Sequência):
```mermaid
flowchart TD
    A([Início: Solicitação por E-mail]) --> B[Leitura do E-mail e Download de Anexos\n'leitor_email.py']
    B --> C[Validação Documental\n'validador_docs.py']
    C -->|Documentação Incompleta| D[Move para 'Documentos_Pendentes'\n'gestor_arquivos.py']
    D --> E[Envia E-mail de Pendência\n'resposta_cliente.py']
    E --> F([Fim: Aguardando Cliente])
    
    C -->|Documentação OK| G[Move para 'Documentos_OK'\n'gestor_arquivos.py']
    G --> H[Integração e Cadastro no Portal Fake\n'portal_integracao.py']
    H --> I[Move para 'Encaminhados'\n'gestor_arquivos.py']
    I --> J[Envia E-mail de Confirmação em HTML\n'resposta_cliente.py']
    J --> K([Fim: Solicitação Encaminhada])
```

---

## 3. 🛠️ Arquitetura da Solução e Tecnologias

A estrutura de diretórios adota a **Arquitetura Modular por Processo**:

```text
hyperautomation-equipe-1/
├── ERP_Portal_Fake/                  # ERP Simulado (Pastas Físicas)
│   ├── Downloads/                    # Entrada de anexos baixados
│   ├── Documentos_OK/                # Documentos validados
│   ├── Documentos_Pendentes/         # Documentos com pendências
│   └── Encaminhados/                 # Documentos processados e encaminhados
├── docs/                             # Diagramas BPMN e Relatórios
│   ├── Processo01_Atendimento.drawio
│   └── relatorio_tecnico_processo1.md
└── HyperAutomation/                  # Módulos Python e Orquestrador
    ├── source/
    │   ├── .env                      # Variáveis de ambiente (SMTP e ERP)
    │   ├── orquestrador.py           # Orquestrador do fluxo completo
    │   ├── common/                   # Módulos reutilizáveis
    │   └── processo_atendimento/     # Módulos do Processo 1
    │       ├── gestor_arquivos.py    # Movimentação física no ERP
    │       ├── resposta_cliente.py   # Envios de e-mail HTML
    │       ├── leitor_email.py       # Leitura da caixa de entrada
    │       ├── validador_docs.py     # Regras de validação
    │       └── portal_integracao.py  # Automação de cadastro no Portal
    ├── requirements.txt              # Dependências do projeto
    ├── bot.yaml                      # Manifesto BotCity Maestro
    └── pack_bot.py                   # Empacotamento de distribuição
```

### 🧰 Justificativa das Tecnologias Utilizadas:

* **Python 3.x**: Linguagem base escolhida pela robustez no ecossistema de dados, automação e facilidade de integração.
* **Playwright**: Utilizado na automação Web pela execução rápida, suporte a navegadores Chromium modernos e captura automática de screenshots para auditoria.
* **BotCity Maestro SDK**: Utilizado para gerenciamento centralizado do robô na nuvem, postagem de artefatos e controle de logs de execução.
* **`python-docx`**: Biblioteca responsável pela montagem automatizada de fichas cadastrais padronizadas.
* **`python-dotenv`**: Garante a segurança ao isolar credenciais sensíveis (contas SMTP e caminhos de ERP) em variáveis de ambiente fora do versionamento do Git.
* **`smtplib` + `email.mime`**: Responsável pelo envio dos e-mails transacionais com templates de e-mail responsivos em HTML.

---

## 4. 💻 Detalhamento dos Módulos do Integrante 2

### 4.1. Módulo `gestor_arquivos.py` (Classe `GestorArquivos`)
Responsável por garantir a criação das pastas do ERP Simulado e gerenciar o ciclo de vida dos arquivos recebidos:

* **`garantir_estrutura_pastas()`**: Cria automaticamente as pastas `Downloads`, `Documentos_OK`, `Documentos_Pendentes` e `Encaminhados`.
* **`mover_para_status(nome_arquivo, status_ok)`**: Transfere o arquivo recebido da pasta `Downloads` para `Documentos_OK` (se aprovado) ou `Documentos_Pendentes` (se houver irregularidades).
* **`mover_para_encaminhados(nome_arquivo)`**: Transfere o arquivo de `Documentos_OK` para `Encaminhados` após a automação realizar o registro no Portal Fake.

### 4.2. Módulo `resposta_cliente.py` (Classe `NotificadorCliente`)
Responsável por notificar o cliente sobre o andamento de sua solicitação por e-mail em formato HTML:

* **Layout de Aprovação**: Template verde (`#2e7d32`) informando o número do protocolo (`#2026-XXXX`) e confirmando o encaminhamento.
* **Layout de Pendências**: Template vermelho (`#c62828`) listando os documentos pendentes de forma clara em listas com marcadores (`<ul><li>...</li></ul>`).
* **Tratamento de Fallback**: Caso as credenciais SMTP não estejam no `.env`, o módulo registra um log claro no terminal e permite a continuidade da execução sem quebrar a automação.

### 4.3. Integração no `orquestrador.py`
O orquestrador une todas as etapas em um ciclo coeso:
1. Inicializa o `GestorArquivos` e o `NotificadorCliente`.
2. Executa a navegação e o preenchimento ultra-rápido no Portal Fake com Playwright.
3. Extrai os dados dos cadastros efetuados.
4. Gera a ficha `.docx`, movimenta o arquivo através da estrutura física do ERP Simulado e dispara a notificação transacional de status ao cliente.

---

## 5. 🌿 Gestão de Versões e DevOps (GitFlow)

O controle de versão é gerenciado estritamente pela metodologia **GitFlow**:

* **`main`**: Branch de produção contendo apenas versões homologadas e estáveis.
* **`develop`**: Branch de integração para junção dos módulos desenvolvidos pela dupla.
* **`feature/processo-atendimento`** (ou sub-branches `feature/*`): Desenvolvimento isolado das funcionalidades do Processo 1.
* **`release/2.0`**: Branch de preparação, testes integrados e validação da entrega do Roteiro 10.
* **Tag `v2.0`**: Marcador oficial da entrega final da versão 2.0.

---

## 6. 📊 Evidências de Testes e Execução

### 6.1. Validação dos Módulos Locais
O script de validação executou as seguintes verificações:
* Criou arquivos de teste em `Downloads`.
* Movimentou corretamente para `Documentos_OK`, `Documentos_Pendentes` e `Encaminhados`.
* Confirmou a renderização e montagem do e-mail HTML com o protocolo `#2026-0001`.

### 6.2. Execução da Orquestração Integrada
Saída real obtida durante a execução da orquestração:
```text
=================================================================
INICIANDO ORQUESTRAÇÃO RPA COMPLETA (HYPERAUTOMATION - PROCESSO 1)
=================================================================
[GESTOR ARQUIVOS] Estrutura de pastas garantida em: .../ERP_Portal_Fake
[Etapa 1] Abrindo Portal Fake: file://.../index.html
[Etapa 1] Executando preenchimento ultra-rápido dos dados no portal...
  [SCREENSHOT] Salvo: 01_portal_preenchido.png
[Etapa 2] Extraindo dados do cadastro na linha 9...
  [SCREENSHOT] Salvo: 02_extracao_dados.png
[Etapa 3 - Cliente 1/1] Processando: Ana Silva (Protocolo: #2026-0001)
  Documento Word gerado: Ficha_Cadastro_10000012482.docx
[GESTOR ARQUIVOS] Arquivo 'Ficha_Cadastro_10000012482.docx' movido para 'Documentos_OK'.
[GESTOR ARQUIVOS] Arquivo 'Ficha_Cadastro_10000012482.docx' movido para 'Encaminhados'.
  Enviando notificação por e-mail para cliente...
ORQUESTRAÇÃO FINALIZADA COM SUCESSO!
```

---

## 7. 🏁 Conclusão

A automação do **Processo 1 (Setor de Atendimento)** foi desenvolvida com sucesso, atendendo a todos os requisitos arquiteturais e funcionais exigidos na atividade do Roteiro 10. A solução demonstra a eficácia da Hyperautomation ao integrar RPA Web, manipulação de sistema legado/ERP simulado, notificações transacionais em HTML e orquestração em nuvem com o BotCity Maestro.
