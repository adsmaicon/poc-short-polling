import requests
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

API_URL = "http://127.0.0.1:8000"

app = FastAPI()

class Message(BaseModel):
    content: str

@app.post("/process-and-wait")
def process_and_wait(msg: Message, timeout: int = 10, interval: float = 1.0):
    try:
        # Envia para a API que coloca na fila
        resp = requests.post(f"{API_URL}/enqueue", json={"content": msg.content})
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Erro ao enfileirar mensagem")
        message_id = resp.json()["message_id"]
        waited = 0
        # Short polling
        while waited < timeout:
            status_resp = requests.get(f"{API_URL}/status/{message_id}")
            if status_resp.status_code == 200 and status_resp.json().get("status") == "processed":
                return {"status": "done", "message_id": message_id, "content": status_resp.json().get("content")}
            time.sleep(interval)
            waited += interval
        return {"status": "processing", "message_id": message_id, "detail": "Timeout reached, message still processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
