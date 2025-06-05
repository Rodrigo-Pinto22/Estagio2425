from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from functions import gen_answer
from embeddings import gerar_embedding as embedding_function, complete_quey as complete_query
from db_conn import get_db_connection
import re

app = FastAPI()

# Configurar CORS para permitir pedidos do Angular (localhost:4200)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir o modelo de dados esperado (JSON)
class QuestionRequest(BaseModel):
    question: str

def limpar_think_tags(texto):
    return re.sub(r"<think>.*?</think>", "", texto, flags=re.DOTALL).strip()

# Rota para receber perguntas
@app.post("/ask")
async def ask_question(data: QuestionRequest):
    conn, cursor = get_db_connection()

    resposta = gen_answer(
        question=data.question,
        results=[],
        cursor=cursor,
        embedding_function=embedding_function,
        complete_query=complete_query
    )

    cursor.close()
    conn.close()
    resposta = limpar_think_tags(resposta)
    return {"response": resposta}
