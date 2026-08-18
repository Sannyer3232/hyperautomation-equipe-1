FROM python:3.10-slim

# Instalação de dependências do sistema necessárias para o Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalação correta do Playwright e seus navegadores
RUN playwright install chromium
RUN playwright install-deps

COPY . .

# Garante que não haja problemas com o usuário root
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

CMD ["python", "bot.py"]