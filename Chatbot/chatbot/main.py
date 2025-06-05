from functions import gen_answer
from embeddings import gerar_embedding as embedding_function, complete_quey as complete_query
from db_conn import get_db_connection
from telemetry import initialize_telemetry
from dotenv import load_dotenv


def main():
    load_dotenv()
    initialize_telemetry()

    conn, cursor = get_db_connection()
    print("Assistente Técnico de Máquinas-Ferramenta (modo terminal). Escreve 'sair' para terminar.\n")

    while True:
        pergunta = input("Pergunta: ")
        if pergunta.lower() in ["sair", "exit", "quit"]:
            break

        if not pergunta.strip():
            continue

        resposta = gen_answer(
            question=pergunta,
            results=[],
            cursor=cursor,
            embedding_function=embedding_function,
            complete_query=complete_query
        )

        print("\nResposta gerada:\n")
        print(resposta)
        print("\n" + "="*80 + "\n")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
