FROM mcr.microsoft.com/playwright/python:v1.62.0-jammy

WORKDIR /app

RUN apt-get update && apt-get install -y xvfb

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN rm -rf /app/resources/browser_data && mkdir -p /app/resources/browser_data

CMD ["xvfb-run", "-a", "python", "bot.py"]