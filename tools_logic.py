# tools_logic.py
from function import (
    get_table_info,
    get_machine_manual,
    get_machine_n_model_manual,
    get_similarity_context,
    handle_inappropriate_question,
    who_am_i,
    get_ots_info,
    get_ots_info_by_intervencao,
    get_fos_info
)

from embeddings import (
    gerar_embedding as embedding_function,
    complete_quey as complete_query
)

# Função que encaminha para a função certa com base no nome

def call_function(name, arguments, cursor, embedding_function, complete_query, question=""):
    if name == "get_table_info":
        result = get_table_info(cursor)
        return {"content": result}

    elif name == "get_machine_manual":
        nome_maquina = arguments.get("nome_maquina", "")
        result = get_machine_manual(cursor, nome_maquina)
        return {"content": result}

    elif name == "get_machine_n_model_manual":
        nome_maquina = arguments.get("nome_maquina", "")
        modelo = arguments.get("modelo", "")
        result = get_machine_n_model_manual(cursor, nome_maquina, modelo)
        return {"content": result}

    elif name == "get_similarity_context":
        nome_maquina = arguments.get("nome_maquina", "")
        modelo = arguments.get("modelo", "")
        if not embedding_function or not complete_query:
            return {"content": "Erro: função de embedding ou montagem de query não fornecida."}
        result = get_similarity_context(cursor, nome_maquina, modelo, embedding_function, complete_query, question)
        return {"content": result}

    elif name == "handle_inappropriate_question":
        motivo = arguments.get("motivo", "Motivo não especificado.")
        result = handle_inappropriate_question(motivo)
        return {"content": result}
    
    elif name == "who_am_i":
        result = who_am_i()
        return {"content": result}
    
    elif name == "get_ots_info":
        maquina_nome = arguments.get("maquina_nome", "")
        modelo = arguments.get("modelo", "")
        bd = arguments.get("bd", "")
        op = arguments.get("op", "")
        mais_recente = bool(arguments.get("mais_recente", True))
        if isinstance(mais_recente, str):
            mais_recente = mais_recente.lower() == "true"
        result = get_ots_info(cursor, maquina_nome, modelo, bd, op, mais_recente)
        return {"content": result}
    
    elif name == "get_ots_info_by_intervencao":
        termo = arguments.get("termo_pesquisa", "")
        limite = arguments.get("limite", 5)
        if isinstance(limite, str) and limite.isdigit():
            limite = int(limite)
        result = get_ots_info_by_intervencao(cursor, termo, limite)
        return {"content": result}
    
    elif name == "get_fos_info":
        maquina_nome = arguments.get("maquina_nome", "")
        maquina_modelo = arguments.get("maquina_modelo", "")
        tipo = arguments.get("tipo", "")
        result = get_fos_info(cursor, maquina_nome, maquina_modelo, tipo)
        return {"content": result}



    return {"content": "Função desconhecida."}
