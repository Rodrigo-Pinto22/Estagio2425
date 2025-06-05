"""CONSTRUÇÃO DA QUERY FINAL PARA A PESQUISA DE SEMELHANÇA"""


def build_similarity_query(limit: int = 3) -> str:
    """
    Constrói uma query segura com placeholders para uso com psycopg2.

    Parâmetros:
        limit (int): número de resultados a retornar

    Retorna:
        str: query SQL com <ARRAY_EMBEDDING_HERE> como placeholder
    """
    query = f"""
        SELECT c.id, c.manuais_id, c.conteudo, c.pag, c.vetor <=> <ARRAY_EMBEDDING_HERE> AS similarity
        FROM conteudo c
        JOIN manuais m ON c.manuais_id = m.id
        JOIN maquina_manuais mm ON m.id = mm.manuais_id
        JOIN maquina ma ON mm.maquina_id = ma.id
        WHERE ma.nome = %s AND ma.modelo = %s
        GROUP BY c.id, c.conteudo
        ORDER BY similarity
        LIMIT {limit};
    """
    return query.strip()
