
# 📨 POC Short Polling com FastAPI, RabbitMQ e PostgreSQL

Projeto de exemplo para processamento assíncrono com fila, banco e short polling.

## 🚀 Tecnologias

- **FastAPI** — APIs REST
- **RabbitMQ** — Fila de mensagens
- **PostgreSQL** — Persistência
- **Python Worker** — Consome fila e grava no banco
- **Short Polling** — Cliente aguarda processamento

---

## ⚙️ Como funciona

1. O cliente faz uma requisição para a API (`/enqueue` ou `/process-and-wait`).
2. A mensagem é enviada para a fila RabbitMQ.
3. O worker consome a fila, processa e grava no PostgreSQL.
4. O cliente pode consultar o status pelo `message_id`.
5. O endpoint `/process-and-wait` faz short polling até o processamento ser concluído.

---

## ▶️ Como executar

```bash
# Suba os serviços
./start.sh

# Para parar tudo
./stop.sh
```

---

## 🧪 Testando

1. Importe a collection `postman_enqueue_and_status.json` no Postman.
2. Teste os endpoints principais:
   - `POST /enqueue` (porta 8000): Enfileira mensagem e retorna `message_id`.
   - `GET /status/{message_id}` (porta 8000): Consulta status da mensagem.
   - `POST /process-and-wait` (porta 8001): Envia mensagem e aguarda processamento (short polling).

### Exemplo de request (short polling)

```bash
curl -X POST "http://127.0.0.1:8001/process-and-wait" \
  -H "Content-Type: application/json" \
  -d '{"content": "mensagem de teste"}'
```

---

## 📦 Requisitos

- Docker e Docker Compose
- Python 3.8+

---

## 📄 Observações

- Os logs dos serviços ficam em `api.log`, `worker.log` e `short_polling_api.log`.
- Variáveis de ambiente estão em `.env`.
