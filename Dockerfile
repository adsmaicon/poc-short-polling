# Dockerfile para FastAPI + Worker Python
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# Por padrão, inicia a API. Para rodar o worker, use:
# docker run ... <imagem> python -m worker.rabbit_worker
CMD ["uvicorn", "app.rabbit_api:app", "--host", "0.0.0.0", "--port", "8000"]
