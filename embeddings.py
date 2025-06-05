import re
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
"""GERAÇÃO DE EMBEDDINGS PARA A PESQUISA DE SEMELHANÇA"""

def gerar_embedding(texto):
    emb = model.encode([texto])
    emb = np.array(emb)
    #print("Dimensão do embedding:",emb.shape )
    
    emb = np.mean(emb, axis=0)

    return np.array(emb).tolist()


"""FUNÇÃO PARA COMPLETAR A QUERY FINAL"""

def complete_quey(query: str, embedding: list[float]) -> str:

    
    """ Substitui o placeholder de embedding na query pelo vetor real.
    Args:
        query (str): A query SQL gerada pelo modelo com placeholder.
        embedding (list[float]): O vetor de embedding a ser inserido.
    Returns:
        str: A query com o vetor de embedding substituído."""

    # Formatar o embedding para string SQL entre parênteses
    embedding_str = "ARRAY[" + ", ".join(f"{v:.6f}" for v in embedding) + "]::vector"

    # Substituir qualquer um dos dois placeholders possíveis
    query_modificada = re.sub(r"<(ARRAY_EMBEDDING_HERE|embedding_string)>", embedding_str, query)
    

    return query_modificada