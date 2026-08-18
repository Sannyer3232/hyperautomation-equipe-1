FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Configura o local de instalação dos navegadores
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Instala os navegadores e dependências forçando o local
RUN playwright install chromium && playwright install-deps

# Garante que a pasta tenha permissão de leitura
RUN chmod -R 755 /ms-playwright

COPY . .

CMD ["python", "bot.py"]