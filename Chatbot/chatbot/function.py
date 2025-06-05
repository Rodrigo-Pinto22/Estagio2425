from query_logic import build_similarity_query  
from db_conn import get_db_connection


"""FUNÇÃO PARA EXTRAIR A INFORMAÇÃO DO ESQUEMA DA BASE DE DADOS"""

def get_table_info(cursor):
    cursor.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
    """)
    schema_info = {}
    for table, column, dtype in cursor.fetchall():
        if table not in schema_info:
            schema_info[table] = []
        schema_info[table].append((column, dtype))
    
    table_info = ""
    for table, columns in schema_info.items():
        table_info += f"Tabela '{table}':\n"
        for col, dtype in columns:
            table_info += f"  - {col} ({dtype})\n"
        table_info += "\n"
    
    return table_info


"""FUNÇÃO PARA EXTRAIR O NOME DO MANUAL DA MAQUINA COM BASE NO NOME DA MARCA E MODELO"""

def get_machine_n_model_manual(cursor, nome_maquina: str, modelo: str) -> str:
    """
    Obtém os títulos dos manuais associados a uma máquina específica,
    identificada pela marca (nome) e pelo modelo.

    Parâmetros:
        cursor: cursor ativo da base de dados
        nome_maquina (str): nome da marca da máquina (ex: EMAG)
        modelo (str): modelo da máquina (ex: VL4)

    Retorna:
        str: lista de títulos ou mensagem de erro se não encontrado
    """
    query = """
        SELECT m.titulo
        FROM manuais m
        JOIN maquina_manuais mm ON m.id = mm.manuais_id
        JOIN maquina mq ON mm.maquina_id = mq.id
        WHERE LOWER(mq.nome) = LOWER(%s)
          AND LOWER(mq.modelo) = LOWER(%s);
    """
    cursor.execute(query, (nome_maquina, modelo))
    results = cursor.fetchall()

    if results:
        titulos = "\n".join(f"- {row[0]}" for row in results)
        return f"Manuais da máquina '{nome_maquina} {modelo}':\n{titulos}"
    else:
        return f"Não foram encontrados manuais para a máquina '{nome_maquina} {modelo}'."
    


"""FUNÇÃO PARA EXTRAIR O NOME DO MANUAL DA MAQUINA COM BASE NO NOME DA MARCA"""

def get_machine_manual(cursor, nome_maquina: str,) -> str:
    """
    Obtém os títulos dos manuais associados a uma máquina específica,
    identificada pela marca (nome) e pelo modelo.

    Parâmetros:
        cursor: cursor ativo da base de dados
        nome_maquina (str): nome da marca da máquina (ex: EMAG)
        modelo (str): modelo da máquina (ex: VL4)

    Retorna:
        str: lista de títulos ou mensagem de erro se não encontrado
    """
    query = """
        SELECT m.titulo
        FROM manuais m
        JOIN maquina_manuais mm ON m.id = mm.manuais_id
        JOIN maquina mq ON mm.maquina_id = mq.id
        WHERE LOWER(mq.nome) = LOWER(%s);
    """
    cursor.execute(query, (nome_maquina,))
    results = cursor.fetchall()

    if results:
        titulos = "\n".join(f"- {row[0]}" for row in results)
        return f"Manuais da máquina '{nome_maquina}':\n{titulos}"
    else:
        return f"Não foram encontrados manuais para a máquina '{nome_maquina}'."
    


"""SUBMISSÃO DA QUERY PARA O POSTGRESQL"""

def get_similarity_context(cursor, nome_maquina: str, modelo: str, embedding_function, complete_query, question: str) -> str:
    embedding = embedding_function(question)
    sql_template = build_similarity_query()
    final_query = complete_query(sql_template, embedding)  ## Acrescentei na query c.manuais_id
    
    cursor.execute(final_query, (nome_maquina, modelo))
    results = cursor.fetchall()

    if not results:
        return "Não foram encontrados conteúdos relevantes para esta máquina e modelo."

    context = "\n\n".join(f"- {row[2]}" for row in results) # row[2] é o conteúdo caso tenhas que eliminar no query_logi.py o c.manuais_id, troca o row[2] por row[1]
    manuais_id = [row[1] for row in results]                # apagar se não for necessário o c.manuais_id
    page = [row[3] for row in results]                # apagar se não for necessário o c.manuais_id
    url_link = get_manual_url(nome_maquina, modelo, manuais_id, page,  cursor) #apagar se não for necessário o c.manuais_id
    if url_link:
        context += f"\n\nPara mais informações, consulte o manual: {url_link}"
    return f"Contexto relevante encontrado para {nome_maquina} {modelo}:\n{context}"


"""FUNÇÃO PARA LIDAR COM PERGUNTAS INAPROPRIADAS"""

def handle_inappropriate_question(motivo: str) -> str:
    return (
        "A sua pergunta foi considerada inadequada no contexto deste assistente técnico.\n"
        f"Motivo: {motivo}\n"
        "Por favor, reformule a sua questão com foco técnico e relacionado com manuais de máquinas-ferramenta."
    )


def who_am_i() -> str:
    return (
        "Eu sou o assistente virtual HorseTech, técnico especializado em manuais de máquinas-ferramenta relativas às linhas BD100, BD101 e BD102.\n"
        "Estou aqui para o ajudar com informações técnicas e manuais relacionados com máquinas."
    )


def get_ots_info(
    cursor,
    maquina_nome: str = None,
    maquina_modelo: str = None,
    linha: str = None,
    op: str = None,
    mais_recente: bool = True
) -> str:
    """
    Consulta OTs associadas a uma máquina específica identificada pelo nome e linha de produção.
    A função obtém o ID da máquina a partir da tabela `maquina`, e depois consulta a tabela `ots`.

    Parâmetros:
    - cursor: cursor ativo da base de dados (fornecido externamente)
    - maquina_nome: nome exato ou parcial da máquina (ex: "EMAG")
    - linha: linha de produção (ex: "BD100")
    - op: operação (ex: "OP110") — opcional
    - mais_recente: se True, retorna apenas a última OT

    Retorna:
    - Frase descritiva em linguagem natural com a informação da(s) OT(s)
    """

    # 1. Obter o ID da máquina
    query_maquina = """
        SELECT id FROM maquina
        WHERE LOWER(nome) = LOWER(%s)
    """
    params = [maquina_nome]

    if maquina_modelo:
        query_maquina += " AND LOWER(modelo) = LOWER(%s)"
        params.append(maquina_modelo)

    if linha:
        query_maquina += " AND linha = %s"
        params.append(linha)

    if op:
        query_maquina += " AND op = %s"
        params.append(op)

    print(query_maquina, params)
    cursor.execute(query_maquina, tuple(params))
    resultado = cursor.fetchone()

    if not resultado:
        return "❌ Não foi possível encontrar nenhuma máquina com os critérios fornecidos."

    maquina_id = resultado[0]

    # 2. Buscar OTs da máquina encontrada
    query_ots = """
        SELECT id, intervencao, atividade, datain, dataout, comentario, pedidos, num_tot_horas
        FROM ots
        WHERE maquina_id = %s
        ORDER BY dataout DESC
    """
    if mais_recente:
        query_ots += " LIMIT 1"

    cursor.execute(query_ots, (maquina_id,))
    linhas = cursor.fetchall()

    if not linhas:
        return "❌ Não foram encontradas ordens de trabalho para esta máquina."

    descricoes = []
    for linha_ot in linhas:
        id_ot, intervencao, atividade, datain, dataout, comentario, pedido, num_tot_horas = linha_ot
        descricoes.append(
            f"A ordem de trabalho {id_ot} decorreu de {datain.date()} a {dataout.date()}. "
            f"Intervenção: \"{intervencao}\". "
            f"Atividade: \"{atividade}\". "
            f"Comentário: {comentario or 'nenhum'}."
            f" Pedidos: {pedido or 'nenhum'}. "
            f"Número total de horas: {num_tot_horas or 'nenhum'}."
            f"- Link: http://localhost/OTs/Ano_{datain.year}.pdf\n"
        )

    return "\n\n".join(descricoes)

#conn, cursor = get_db_connection()


#print(get_ots_info(cursor, "EMAG", "VL4", "BD100", "OP110", True))


def get_ots_info_by_intervencao(cursor, termo_pesquisa: str, limite: int = 3) -> str:
    """
    Pesquisa as ordens de trabalho (OTs) na tabela `ots` com base no conteúdo da coluna `intervencao`.

    Parâmetros:
    - cursor: cursor da base de dados
    - termo_pesquisa: expressão a procurar (ex: 'colisão trackmotion')
    - limite: número máximo de OTs a retornar

    Retorna:
    - Frase descritiva com as OTs encontradas
    """

    query = """
        SELECT id, intervencao, atividade, datain, dataout, comentario, pedidos, num_tot_horas
        FROM ots
        WHERE LOWER(intervencao) LIKE %s
        ORDER BY dataout DESC
        LIMIT %s
    """
    termo_sql = f"%{termo_pesquisa.lower()}%"
    cursor.execute(query, (termo_sql, limite))
    linhas = cursor.fetchall()
    print(linhas)

    if not linhas:
        return f"❌ Não foram encontradas OTs com '{termo_pesquisa}' na intervenção."

    
    descricoes = []
    for ot_id, intervencao, atividade, datain, dataout, comentario, pedido, num_tot_horas in linhas:
        ano = datain.year
        descricoes.append(
            f"\nOT {ot_id} ({datain.date()} → {dataout.date()}):\n"
            f"- Intervenção: {intervencao}\n"
            f"- Atividade: {atividade}\n"
            f"- Comentário: {comentario or 'nenhum'}"
            f"- Pedidos: {pedido or 'nenhum'}\n"
            f"- Número total de horas: {num_tot_horas or 'nenhum'}\n"
            f"- Link: http://localhost/OTs/Ano_{ano}.pdf\n"
        )

    return "\n\n".join(descricoes)


def get_fos_info(cursor, maquina_nome, maquina_modelo: int, tipo: str = None) -> str:
    """
    Retorna a FOS associada a uma máquina e, opcionalmente, a um tipo específico (PMA, Bloqueio, Desbloqueio).

    Parâmetros:
    - cursor: cursor da base de dados
    - maquina_id: ID da máquina na tabela `maquina`
    - tipo: filtro textual opcional para o título da FOS (ex: 'PMA', 'bloqueio')

    Retorna:
    - Texto formatado com título, número de passos, ferramentas e conteúdo.
    """

    # 1. Obter o ID da máquina
    query_maquina = """
        SELECT id FROM maquina
        WHERE LOWER(nome) = LOWER(%s)
    """
    params = [maquina_nome]

    if maquina_modelo:
        query_maquina += " AND LOWER(modelo) = LOWER(%s)"
        params.append(maquina_modelo)

    print(query_maquina, params)
    cursor.execute(query_maquina, tuple(params))
    resultado = cursor.fetchone()

    if not resultado:
        return "❌ Não foi possível encontrar nenhuma máquina com os critérios fornecidos."

    maquina_id = resultado[0]

    query = """
        SELECT titulo, num_passos, ferramentas, conteudo
        FROM fos
        WHERE maquina_id = %s
    """
    params = [maquina_id]

    if tipo:
        query += " AND LOWER(titulo) ILIKE %s"
        params.append(f"%{tipo.lower()}%") 

    cursor.execute(query, tuple(params))
    row = cursor.fetchone()

    if not row:
        return f"❌ Não foi encontrada nenhuma FOS para a máquina {maquina_id}" + (f" com tipo '{tipo}'." if tipo else ".")

    titulo, num_passos, ferramentas, conteudo = row

    return (
        f"📘 **FOS: {titulo}**\n"
        f"- 🔢 Passos: {num_passos}\n"
        f"- 🧰 Ferramentas: {ferramentas or 'Não especificadas'}\n"
        f"- 📄 Conteúdo:\n{conteudo}"
        f"- 🔗 Link: http://localhost/FOS/CX DIF BD100_{titulo}\n"
    )


def get_manual_url(nome_maquina: str, modelo: str, manuais_id, page, cursor) -> str:
    """
    Obtém a URL do manual associado a uma máquina específica, identificada pela marca (nome) e pelo modelo.

    Parâmetros:
        nome_maquina (str): nome da marca da máquina (ex: EMAG)
        modelo (str): modelo da máquina (ex: VL4)

    Retorna:
        str: URL do manual ou mensagem de erro se não encontrado
    """
    titulo_man = []
    query_manual = """SELECT titulo FROM manuais WHERE id = %s"""
    for id in manuais_id:
        cursor.execute(query_manual, (id,))
        resultado = cursor.fetchone()
        if resultado:
            titulo_man.append(resultado[0])

    dict_urls = {
        "EMAG": {
            "VL4": {
                "Manutenção e conservação": "http://localhost/Manuais_Procedimentos/OP110_EMAG_VL4/Manuten%C3%A7ao%20e%20conserva%C3%A7ao.pdf",
                "Efectuar origem nos transportadores de peças EMAG": "http://localhost/Manuais_Procedimentos/OP110_EMAG_VL4/Efectuar%20origem%20nos%20transportadores%20de%20pe%C3%A7as%20EMAG.pdf",
                "CxDif OP110 Manual operação da máquina VL4": "http://localhost/Manuais_Procedimentos/OP110_EMAG_VL4/CxDif_OP110_Manual%20opera%C3%A7%C3%A3o%20da%20m%C3%A1quina%20VL4.pdf",
            },
            "VL8-Y": {
                "Manual operação da máquina EMAG OP130": "http://localhost/Manuais_Procedimentos/OP130_EMAG_VL8_Y/Manual operação da máquina EMAG OP130",
                "Proced lubrif engregangem ferr rotativa":"http://localhost/Manuais_Procedimentos/OP130_EMAG_VL8_Y/Proced lubrif engregangem ferr rotativa.pdf",
                "Procedimento ajuste corrente carregador":"http://localhost/Manuais_Procedimentos/OP130_EMAG_VL8_Y/Procedimento ajuste corrente carregador.pdf",
                "Procedimento ajuste_Subst correia eixo Y": "http://localhost/Manuais_Procedimentos/OP130_EMAG_VL8_Y/Procedimento ajuste_Subst correia eixo Y.pdf"
            },
            "VT4-4":{
                "CxDif_OP140_Manual operação da máquina EMAG VT 4-4":"http://localhost/Manuais_Procedimentos/OP140_EMAG_VT4_4/CxDif_OP140_Manual operação da máquina EMAG VT 4-4.pdf",
                "Manutençäo e conservação":"http://localhost/Manuais_Procedimentos/OP140_EMAG_VT4_4/Manutençäo e conservação.pdf"
            }
        },
        "Trackmotion": {
            "Controlo": {
                "Manual operação do Trackmotion": "http://localhost/Manuais_Procedimentos/Trackmotion/Manual operação do Trackmotion.pdf"
            },
        },
    }
    i = 0
    # Verifica se a máquina e o modelo estão no dicionário
    if nome_maquina in dict_urls and modelo in dict_urls[nome_maquina]:
        # Se o título do manual estiver no dicionário, retorna a URL correspondente
        for titulo in titulo_man:
            titulo = titulo.split(" - ")[1]
            for keys in dict_urls[nome_maquina][modelo].keys():
                if keys == titulo:
                    link= dict_urls[nome_maquina][modelo][keys]
                    return f"URL do manual: {link+'#'+'page='+str(page[i])}"
                else:
                    pass
                    #print(titulo)
                    #return "Não foi encontrada URL para o manual."
            i+=1


