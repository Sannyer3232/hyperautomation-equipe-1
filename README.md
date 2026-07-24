# HyperAutomation - Portal Fake Soluções Digitais

## 📝 Descrição

Projeto desenvolvido para demonstrar técnicas de **Hyperautomation** por meio da automação do processo de cadastro de clientes da empresa fictícia **Portal Fake Soluções Digitais**. 

A solução integra automação Web, preenchimento e extração de dados, geração automática de documentos, envio automatizado de e-mails e controle de versão utilizando Git, GitHub e GitFlow.

---

## ⚡ Funcionalidades

- **Carga e Criptografia/Preenchimento Web**: População ultra-rápida do formulário no Portal Fake a partir de base CSV utilizando **Playwright**;
- **Extração Automática**: Leitura dos dados cadastrados no formulário de cadastro utilizando **Playwright**;
- **Geração de Documentos**: Criação automática da ficha de cadastro em formato Word (`.docx`) preenchida com os dados do cliente;
- **Disparo de E-mails**: Envio automático da ficha de cadastro por e-mail utilizando protocolo **SMTP Gmail** com anexo;
- **Exclusão Automática**: Remoção automática do arquivo temporário `.docx` após o envio com sucesso do e-mail;
- **Segurança de Credenciais**: Proteção das credenciais de e-mail por meio de variáveis de ambiente no arquivo `.env`;
- **Versionamento Estruturado**: Controle de versão utilizando **Git**, **GitHub** e o fluxo **GitFlow**.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **Playwright** (Automação Web)
- **python-docx** (Geração de Documentos Word)
- **python-dotenv** (Gerenciamento de Variáveis de Ambiente)
- **smtplib & email** (Envio de E-mails via SMTP)
- **Git & GitHub** (Controle de Versão)
- **GitFlow** (Metodologia de Ramificação de Código)

---

## 📁 Estrutura do Projeto

```text
HyperAutomation/
│
├── source/
│   ├── extracao.py         # Módulo de extração de dados com Playwright
│   ├── documento_email.py  # Geração da ficha em Word (.docx) e envio de e-mail
│   └── orquestrador.py     # Orquestrador principal do ciclo completo de RPA
│
├── resources/
│   ├── bot.py                     # Módulo de preenchimento rápido do portal
│   ├── cadastros_portal_fake_20.csv # Base de dados de exemplo em CSV
│   └── portal_fake/               # Aplicação Web estática (Portal Fake)
│
├── .env                    # Variáveis de ambiente com credenciais (Não versionado)
├── .env.example            # Modelo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── requirements.txt        # Dependências do projeto Python
└── README.md               # Documentação do projeto
```

---

## 🔒 Segurança

As credenciais utilizadas para a autenticação e envio de e-mails são armazenadas com segurança no arquivo `.env`, utilizando as seguintes variáveis:

- `EMAIL_REMETENTE`
- `EMAIL_SENHA`

> [!IMPORTANT]
> O arquivo `.env` está listado no `.gitignore`, garantindo que informações sensíveis não sejam enviadas ao repositório remoto no GitHub.

---

## 🌿 Controle de Versão (GitFlow)

O projeto foi desenvolvido utilizando a metodologia **GitFlow**, contando com as seguintes branches:

- `main` – Versão oficial e estável em produção;
- `develop` – Integração contínua das novas funcionalidades;
- `feature/extracao` – Desenvolvimento do módulo de extração de dados;
- `feature/documento-email` – Desenvolvimento da geração de documentos e envio de e-mails;
- `release/1.0` – Preparação, validação e testes finais para lançamento da versão 1.0.

### 🔄 Fluxo GitFlow Executado:
1. Criação do repositório Git;
2. Desenvolvimento das funcionalidades em branches `feature/*`;
3. Merge das funcionalidades finalizadas para a branch `develop`;
4. Criação da branch `release/1.0`;
5. Realização dos testes finais de integração do RPA;
6. Merge da branch `release` para a `main`;
7. Criação da tag `v1.0`;
8. Publicação oficial do projeto no GitHub.

---

## 📌 Versão

**Versão Atual:** `v1.0`  
Primeira versão funcional da automação desenvolvida para o processo de cadastro da empresa fictícia Portal Fake Soluções Digitais.

---

## 👤 Autor

- **Nome do Aluno:** Sannyer Cardoso Carvalho Nery
- **Turma:** Tarde  
- **Disciplina:** Hyperautomation  
- **Professor:** Moisés Levy  
