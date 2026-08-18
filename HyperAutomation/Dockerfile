# Usa a imagem oficial que já tem Python, Playwright e os Browsers instalados
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Define o diretório de trabalho
WORKDIR /app

# Copia os requisitos e instala as libs Python (o Playwright já está instalado na imagem)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do seu projeto
COPY . .

# Comando de execução
CMD ["python", "bot.py"]