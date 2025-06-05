#from fu_eval import gen_answer
from functions import gen_answer
from embeddings import gerar_embedding as embedding_function, complete_quey as complete_query
from db_conn import get_db_connection
from telemetry import initialize_telemetry
from dotenv import load_dotenv
import re


def questions(file):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.readlines()
        list_pre = [con.strip() for con in content if con not in ['\n', '\r\n']]
        list_q = [q for q in list_pre if q.startswith('Q:')]
        list_q = [q[2:].strip() for q in list_q]  # Remove 'Q:' e espaços em branco
        for i, q in enumerate(list_q):
            quest = re.sub(r'\?\s*\[.*?\]', '?', q)
            list_q[i] = quest
    return list_q

def main():
    load_dotenv()
    initialize_telemetry()
    q = questions("C:\\Users\\ASUS\\Desktop\\utilizador\\Desktop\\Universidade\\5º ano\\2ºSemestre\\Eval_Questions.txt")
    q.append("sair")
    conn, cursor = get_db_connection()
    print("Assistente Técnico de Máquinas-Ferramenta (modo terminal). Escreve 'sair' para terminar.\n")

    for question in q:
        print(question)
        if question.lower() in ["sair", "exit", "quit"]:
            break

        if not question.strip():
            continue
        """if question == q[-1]:
            break
        if question == q[-10] or question == q[-2]:
            print(question)
            resposta = gen_answer(
                question=question,
                results=[],
                cursor=cursor,
                embedding_function=embedding_function,
                complete_query=complete_query
            )

            print("\nResposta gerada:\n")
            print(resposta)
            print("\n" + "="*80 + "\n")"""
        resposta = gen_answer(
                question=question,
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