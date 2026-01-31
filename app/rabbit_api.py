import pika
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uuid
import psycopg2

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "password")
QUEUE_NAME = "poc_queue"

app = FastAPI()

class Message(BaseModel):
    content: str

def get_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))

def get_pg_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        dbname=os.getenv("POSTGRES_DB", "pocdb")
    )

@app.post("/enqueue")
def enqueue_message(msg: Message):
    try:
        message_id = str(uuid.uuid4())
        payload = f"{message_id}|{msg.content}"
        conn = get_connection()
        channel = conn.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=payload.encode(),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        conn.close()
        return {"status": "queued", "message_id": message_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{message_id}")
def get_status(message_id: str):
    try:
        conn = get_pg_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, content FROM messages WHERE message_id = %s", (message_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return {"status": "processed", "content": result[1]}
        else:
            return {"status": "pending", "content": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
