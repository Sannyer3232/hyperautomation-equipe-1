# 🚀 HyperAutomation — Plataforma Integrada de Automação de Processos

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Chromium-green?logo=playwright)
![BotCity Maestro](https://img.shields.io/badge/BotCity-Maestro%20SDK-orange)
![Tests](https://img.shields.io/badge/Tests-70%20Passed%20%7C%20100%25-brightgreen?logo=pytest)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20%26%20GHCR-informational?logo=githubactions)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

---

## 📝 Visão Geral

O projeto **HyperAutomation** é uma solução de automação inteligente de processos de negócios de ponta a ponta desenvolvida para a empresa fictícia **Portal Fake Soluções Digitais**.

A plataforma integra automação Web (RPA), visão computacional, processamento de documentos Word e PDF, integração com caixas postais (IMAP/SMTP), orquestração em nuvem com **BotCity Maestro**, cálculo de indicadores executivos e geração de relatórios gerenciais multiplataforma com gráficos visuais em **PDF, Excel, Markdown e JSON**.

---

## 🔄 Macroprocessos Integrados (Esteira Ponta a Ponta)

A esteira de automação é composta por **5 processos modulares** que operam de forma autônoma ou encadeada:

```text
[ Processo 1: Atendimento ] 
           │ (Ficha .docx gerada e e-mail com protocolo enviado)
           ▼
[ Processo 2: Organização ] 
           │ (Leitura IMAP do retorno assinado, validação e gravação na Planilha Mestra)
           ▼
[ Processo 3: Cadastro RPA ] 
           │ (Validação de CPF/E-mail e submissão automatizada no Portal Fake)
           ▼
[ Processo 4: SAC ] 
           │ (Comunicação de boas-vindas via SMTP e registro em atendimentos_sac.xlsx)
           ▼
[ Processo 5: Relatórios & Gerência ]
           │ (Consolidação 360°, cálculo de KPIs e emissão de Relatórios em PDF, Excel, MD e JSON)
           ▼
   🏁 PROCESSO CONCLUÍDO
```

### 1️⃣ Processo 1 — Atendimento e Solicitação de Cadastro
- **Objetivo:** Iniciar o ciclo de atendimento ao cliente.
- **Entrada:** Base de dados cadastrais em CSV ou parâmetros do sistema.
- **Operação:** Gera dinamicamente a ficha cadastral formatada em Word (`.docx`), cria o protocolo único rastreável (`PROT-YYYYMMDD-XXXX`) e envia por e-mail ao cliente solicitando a assinatura digital.
- **Status Registrado:** `AGUARDANDO RETORNO`.

### 2️⃣ Processo 2 — Recepção e Organização de Documentos
- **Objetivo:** Capturar e validar os documentos assinados retornados pelos clientes.
- **Operação:** Monitora a caixa de entrada via **IMAP**, localiza mensagens contendo o protocolo e anexo em PDF/Word, valida a integridade do arquivo e realiza a extração dos dados cadastrais.
- **Saída:** Persistência dos dados extraídos na [`Planilha_Mestra.xlsx`](ERP_Portal_Fake/Sistema_Integrador_Portal_Fake/Planilha_Mestra.xlsx) com status `CONCLUIDO_P2` e arquivamento dos PDFs validados nas pastas de auditoria (`Documentos_OK` / `Documentos_Pendentes`).

### 3️⃣ Processo 3 — Validação e Cadastro no Portal Fake (RPA)
- **Objetivo:** Inserir os clientes validados no sistema corporativo web da empresa.
- **Operação:** Lê os clientes pendentes da Planilha Mestra, executa sanitização e validação algorítmica de CPF (dígitos verificadores oficiais), formato de e-mail e dados obrigatórios. Utiliza **Playwright** para preencher o formulário web do Portal Fake, capturando logs e tratando duplicidades de cadastro.
- **Status Atualizado:** `CONCLUIDO_P3`, `DUPLICADO_P3` ou `ERRO_VALIDACAO_P3`.

### 4️⃣ Processo 4 — SAC e Comunicação Pós-Cadastro
- **Objetivo:** Notificar o cliente sobre a conclusão do cadastro e registrar o atendimento.
- **Operação:** Identifica os registros aprovados na Planilha Mestra, dispara e-mail formal de confirmação via **SMTP** com idempotência (evitando duplicidade de envios) e registra o histórico na planilha [`atendimentos_sac.xlsx`](ERP_Portal_Fake/Sistema_Integrador_Portal_Fake/atendimentos_sac.xlsx).
- **Status SAC:** `COMUNICADO` ou `PENDENTE_CONTATO`.

### 5️⃣ Processo 5 — Relatórios, Métricas e Governança
- **Objetivo:** Consolidar os dados da esteira, calcular métricas e gerar relatórios executivos.
- **Operação:** Cruza os dados da Planilha Mestra e da Planilha SAC, calcula indicadores analíticos (taxas de conversão, duplicidade, aprovação e eficiência global) e gera relatórios versionados com gráficos:
  - 📄 **PDF Executivo (`.pdf`):** Layout corporativo A4 com gráficos visuais vetoriais, cartões de KPIs e tabela consolidada.
  - 📊 **Excel Analítico (`.xlsx`):** Dashboard gerencial formatado, gráficos de pizza e base consolidada.
  - 📝 **Markdown (`.md`):** Sumário executivo tabular para visualização rápida no repositório.
  - ⚙️ **JSON Estruturado (`.json`):** Payload com metadados para integração com APIs e dashboards.

---

## 🛠️ Tecnologias e Bibliotecas

| Tecnologia / Pacote | Finalidade |
| :--- | :--- |
| **Python 3.10+** | Linguagem principal do projeto |
| **Playwright (Chromium)** | Automação RPA web e renderização de relatórios PDF em alta definição |
| **openpyxl** | Criação, leitura e estilização de planilhas Excel (`.xlsx`) e gráficos |
| **python-docx** | Geração e manipulação de documentos Word (`.docx`) |
| **pypdf** | Validação e extração de dados de arquivos PDF |
| **botcity-maestro-sdk** | Orquestração na nuvem, leitura de parâmetros e envio de status de tarefas |
| **smtplib / email / imaplib** | Protocolos de envio (SMTP) e recepção (IMAP) de e-mails corporativos |
| **python-dotenv** | Gestão de variáveis de ambiente e segurança de credenciais |
| **pytest & pytest-cov** | Suíte de testes unitários, testes de integração e cobertura de código |
| **Docker** | Containerização e padronização do ambiente de execução |
| **GitHub Actions & GHCR** | Pipeline automatizado de CI/CD e publicação de containers |

---

## 📁 Estrutura do Projeto

```text
hyperautomation-equipe-1/
│
├── pai.bot.py                      # Ponto de entrada unificado raiz (todos os 5 processos)
├── requirements.txt                # Dependências Python do projeto
├── Dockerfile                      # Definição do container Docker
├── .dockerignore                   # Arquivos ignorados no build Docker
├── .gitignore                      # Arquivos ignorados no Git
│
├── HyperAutomation/
│   ├── bot.py                      # Ponto de entrada do container e orquestrador principal
│   ├── pai.bot.py                  # Ponto de entrada secundário para compatibilidade
│   ├── Dockerfile                  # Dockerfile do módulo HyperAutomation
│   ├── requirements.txt            # Dependências específicas do módulo
│   ├── bot.yaml                    # Manifesto do BotCity Maestro
│   │
│   ├── source/
│   │   ├── orquestrador.py         # Orquestrador central integrado (Fases 1 a 5)
│   │   ├── orquestrador_processo2.py # Orquestrador isolado do Processo 2 (Organização)
│   │   ├── orquestrador_processo3.py # Orquestrador isolado do Processo 3 (Cadastro RPA)
│   │   ├── orquestrador_processo4.py # Orquestrador isolado do Processo 4 (SAC)
│   │   ├── orquestrador_processo5.py # Orquestrador isolado do Processo 5 (Relatórios)
│   │   │
│   │   ├── common/                 # Módulos compartilhados (protocolo, documentos, extração)
│   │   ├── processo_atendimento/   # Módulos do Processo 1 (Atendimento) e Processo 4 (SAC)
│   │   ├── processo_organizacao/   # Módulos do Processo 2 (Organização e Planilha Mestra)
│   │   ├── processo_cadastro/      # Módulos do Processo 3 (Validador, Leitor, RPA Portal)
│   │   └── processo_relatorios/    # Módulos do Processo 5 (Consolidador, Métricas, Gerador PDF/XLSX)
│   │
│   └── resources/                  # Base de dados CSV, templates e aplicação Portal Fake
│
├── ERP_Portal_Fake/
│   ├── Sistema_Integrador_Portal_Fake/
│   │   ├── Planilha_Mestra.xlsx    # Base mestra de clientes e cadastros
│   │   └── atendimentos_sac.xlsx   # Base histórica de atendimentos SAC
│   └── Relatorios_Gerenciais/      # Diretório de saída dos relatórios gerados (PDF, XLSX, MD, JSON)
│
├── tests/                          # Suíte unificada de testes automatizados (70 testes)
│   ├── conftest.py                 # Configuração de paths do Pytest
│   ├── test_modulo3.py             # Testes do Processo 3 (Cadastro RPA)
│   ├── test_processo_sac.py        # Testes do Processo 4 (SAC e SMTP)
│   ├── test_processo_relatorios.py # Testes do Processo 5 (Relatórios, KPIs e PDFs)
│   └── test_orquestrador_integrado.py # Testes de integração ponta a ponta
│
├── logs/                           # Arquivos de log segregados por processo
│   ├── processo3_cadastro.log
│   ├── processo4_sac.log
│   └── processo5_relatorios.log
│
└── .github/
    └── workflows/
        └── ci-cd.yml               # Pipeline CI/CD (Testes + Build + GHCR)
```

---

## ⚙️ Instalação e Configuração

### 1. Clonar o Repositório
```bash
git clone https://github.com/Sannyer3232/hyperautomation-equipe-1.git
cd hyperautomation-equipe-1
```

### 2. Criar e Ativar o Ambiente Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# ou
.venv\Scripts\activate      # Windows
```

### 3. Instalar as Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

### 4. Configurar as Variáveis de Ambiente (`.env`)
Crie um arquivo `.env` na raiz do projeto (ou dentro de `HyperAutomation/`) contendo as configurações:

```ini
# Configurações de E-mail (Gmail SMTP / IMAP)
EMAIL_REMETENTE=seu_email@gmail.com
EMAIL_SENHA=sua_senha_de_aplicativo_google
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993

# Configurações do Portal Fake
PORTAL_URL=file:///.../ERP_Portal_Fake/Sistema_Integrador_Portal_Fake/index.html
```

---

## 🚀 Instruções de Execução

A automação pode ser executada em **modo integrado (todos os processos encadeados)** ou por **processos individuais**:

### 🎯 1. Execução Completa da Esteira Integrada (Fases 1 a 5)
Executa o fluxo completo ponta a ponta: Geração de Ficha → Leitura/Organização → Cadastro RPA no Portal → Notificação SAC → Relatório Gerencial com Gráficos:

```bash
# Utilizando o ponto de entrada raiz
python pai.bot.py demo_completo

# Ou utilizando o bot principal
python HyperAutomation/bot.py demo_completo
```

---

### 🧩 2. Execução por Processo Individual

#### 🔹 Processo 1 — Enviar Solicitações de Assinatura (Atendimento)
Lê o CSV, gera a ficha em Word e dispara o e-mail de solicitação com protocolo:
```bash
python HyperAutomation/bot.py enviar_solicitacoes --row-index 0
```

#### 🔹 Processo 2 — Processar Retornos e Organizar Documentos
Lê a caixa postal IMAP, valida os PDFs anexados e atualiza a Planilha Mestra:
```bash
python HyperAutomation/bot.py processar_retornos
```

#### 🔹 Processo 3 — Cadastro Automatizado no Portal Fake (RPA)
Lê os clientes aprovados da Planilha Mestra e cadastra no Portal Fake:
```bash
# Execução direta via CLI do Processo 3
python HyperAutomation/source/orquestrador_processo3.py --headless

# Ou cadastrar um CPF específico
python HyperAutomation/source/orquestrador_processo3.py --cpf "10000012482"

# Ou via bot principal
python HyperAutomation/bot.py cadastro
```

#### 🔹 Processo 4 — SAC e Comunicação com Clientes
Dispara as mensagens de confirmação de cadastro e registra em `atendimentos_sac.xlsx`:
```bash
# Execução direta via CLI do Processo 4
python HyperAutomation/source/orquestrador_processo4.py

# Ou via bot principal
python HyperAutomation/bot.py sac
```

#### 🔹 Processo 5 — Relatórios, Indicadores e Gráficos (PDF, Excel, MD, JSON)
Consolida os dados de todos os processos, calcula os KPIs e gera os relatórios executivos:
```bash
# Execução direta via CLI do Processo 5
python HyperAutomation/source/orquestrador_processo5.py

# Ou via bot principal
python HyperAutomation/bot.py relatorios
```

---

### 🎛️ 3. Principais Parâmetros de Linha de Comando

| Argumento | Descrição | Exemplo de Uso |
| :--- | :--- | :--- |
| `-m`, `--modo` | Define o modo de execução | `-m demo_completo`, `-m cadastro`, `-m sac`, `-m relatorios` |
| `--headless` | Executa o navegador em modo invisível (padrão em CI/CD e containers) | `--headless` |
| `--no-headless` | Exibe a interface gráfica do navegador Playwright durante a execução | `--no-headless` |
| `-c`, `--cpf` | Filtra o processamento para um CPF específico | `-c 10000012482` |
| `-r`, `--row-index` | Seleciona o índice do registro na base CSV | `-r 0` |
| `--zerar-base` | Limpa os registros do Portal Fake antes do teste | `--zerar-base` |

---

## 🧪 Testes Automatizados e Cobertura

O projeto possui **70 testes automatizados** com **100% de taxa de aprovação** cobrindo todos os módulos:

```bash
# Executar todos os testes
pytest -v

# Executar testes com relatório detalhado de cobertura de código
pytest -v --cov=HyperAutomation/source tests/
```

---

## 🐳 Execução via Docker (Containerização)

O projeto está totalmente containerizado conforme os padrões do Roteiro 13:

```bash
# Construir a imagem Docker localmente
docker build -t hyperautomation:latest ./HyperAutomation

# Executar a automação dentro do container
docker run --rm -v $(pwd)/ERP_Portal_Fake:/app/ERP_Portal_Fake hyperautomation:latest
```

---

## 🔄 Pipeline de CI/CD (GitHub Actions & GHCR)

O workflow [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml) é disparado a cada `push` e `pull_request` nas branches `main`, `develop` e `test-cicd`:

1. **Job `testes`:**
   - Instalação das dependências Python e Playwright Chromium.
   - Verificação de sintaxe (`python -m compileall .`).
   - Execução da suíte completa de testes (`pytest -v`).
2. **Job `build-and-push`:**
   - Autenticação no **GitHub Container Registry (`ghcr.io`)**.
   - Build da imagem Docker da automação.
   - Publicação automatizada da imagem no pacote do repositório.

---

## 👥 Equipe e Autoria

- **Sannyer Cardoso Carvalho Nery** — Engenharia de Automação / RPA
- **Disciplina:** Hyperautomation  
- **Professor:** Moisés Levy  
