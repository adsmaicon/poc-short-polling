#!/bin/bash
set -e

# Carrega variáveis de ambiente do .env, se existir
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "Variáveis de ambiente carregadas do .env"
fi

# Ativa o ambiente virtual
source .venv/bin/activate

# Sobe RabbitMQ e PostgreSQL
if [ ! $(docker ps -q -f name=rabbitmq) ]; then
  echo "Subindo RabbitMQ e PostgreSQL..."
  docker-compose up -d
  sleep 10
fi

# Instala dependências
pip install -r requirements.txt

# Inicia a API FastAPI
nohup uvicorn app.rabbit_api:app --reload > api.log 2>&1 &
echo "API iniciada (FastAPI)"

# Inicia o worker
nohup python worker/rabbit_worker.py > worker.log 2>&1 &
echo "Worker iniciado"

# Inicia a API de short polling
nohup uvicorn app.short_polling_api:app --reload --port 8001 > short_polling_api.log 2>&1 &
echo "API de short polling iniciada (porta 8001)"

echo "Tudo pronto! Use o endpoint POST /enqueue para enviar mensagens ou POST /process-and-wait na porta 8001."
