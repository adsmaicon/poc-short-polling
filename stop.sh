#!/bin/bash

# Para API FastAPI, Worker e Short Polling API
pkill -f "uvicorn app.rabbit_api:app"
pkill -f "python worker/rabbit_worker.py"
pkill -f "uvicorn app.short_polling_api:app"

# Para RabbitMQ e PostgreSQL
if [ $(docker ps -q -f name=rabbitmq) ]; then
  echo "Parando RabbitMQ e PostgreSQL..."
  docker-compose down
fi

echo "Aplicação parada."
