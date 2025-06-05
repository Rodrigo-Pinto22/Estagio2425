from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from datetime import datetime
from typing import List, Dict
from db_conn import get_db_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restringe isto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/api/tempo-intervencao")
def tempo_intervencao():
    conn, cursor = get_db_connection()

    cursor.execute("""
        SELECT maquina_id, datain, num_tot_horas
        FROM ots
        WHERE datain IS NOT NULL AND num_tot_horas IS NOT NULL
    """)

    rows = cursor.fetchall()
    

    resultado = []

    for maquina_id, datain, horas in rows:
        cursor.execute("""
        SELECT nome, modelo, op, linha
        FROM maquina
        WHERE id = %s
        """, (maquina_id,))

        maq_spec = cursor.fetchone()
        if maq_spec:
            nome, modelo, op, bd = maq_spec
            # Adiciona os detalhes da máquina ao resultado
            resultado.append({
                "maquina_id": maquina_id,
                "nome": nome,
                "modelo": modelo,
                "op": op,
                "bd": bd,
                "data": datain.strftime("%Y-%m-%d"),
                "horas": horas
            })
        else:
            # Se não encontrar a máquina, apenas adiciona o ID e os dados de tempo
            resultado.append({
                "maquina_id": maquina_id,
                "data": datain.strftime("%Y-%m-%d"),
                "horas": horas
            })

    conn.close()

    return resultado
