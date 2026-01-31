import os
import pika
import psycopg2


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "password")
QUEUE_NAME = "poc_queue"


PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_USER = os.getenv("POSTGRES_USER", "user")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "password")
PG_DB = os.getenv("POSTGRES_DB", "pocdb")
TABLE_NAME = "messages"


def get_pg_conn():
    return psycopg2.connect(
        host=PG_HOST,
        user=PG_USER,
        password=PG_PASS,
        dbname=PG_DB
    )


def ensure_table():
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} ("
        "id SERIAL PRIMARY KEY, "
        "message_id VARCHAR(36) UNIQUE NOT NULL, "
        "content TEXT NOT NULL);"
    )
    conn.commit()
    cur.close()
    conn.close()


def callback(ch, method, properties, body):
    import random
    import time
    payload = body.decode()
    print(f"Recebido: {payload}", flush=True)
    delay = random.uniform(1, 3)
    print(f"Processando por {delay:.2f} segundos...", flush=True)
    time.sleep(delay)
    # Espera que payload seja "message_id|conteudo"
    if '|' in payload:
        message_id, content = payload.split('|', 1)
    else:
        message_id, content = None, payload
    conn = get_pg_conn()
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO {TABLE_NAME} (message_id, content) "
        "VALUES (%s, %s)",
        (message_id, content)
    )
    conn.commit()
    cur.close()
    conn.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    ensure_table()
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)
    print("Aguardando mensagens...", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
