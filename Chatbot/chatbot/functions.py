import json
from openai import OpenAI
#import openai
from tools import tools
from tools_logic import call_function
from query_logic import build_similarity_query
from typing import List, Any
from avaliacao import registar_interacao
from dotenv import load_dotenv
import os 

#load_dotenv()
#api_key = os.getenv("OPENAI_API_KEY")
  

client_ollama = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


"""FUNÇÃO PARA A GERAÇÃO DA RESPOSTA FINAL"""

def gen_answer(question: str, results: List[Any], cursor, embedding_function, complete_query ) -> str:
    llama_model = "llama3.2"
    #llama_model = "qwen3:4b"
   # llama_model = "gpt-4"

    system_prompt = """
    Tu és um assistente técnico especializado em manuais de máquinas-ferramenta.
    Baseia-te apenas no contexto fornecido pelas funções  para responder de forma objetiva, técnica e em português de Portugal.

    Dica sobre as siglas utilizadas:
    - OT: Ordem de Trabalho
    - FOS: Folha de Operação Standard

    Tens acesso a ferramentas (funções) que te permitem obter informações adicionais:
    - Usa `get_table_info` para descrever a estrutura da base de dados documental.
    - Usa `get_machine_manual` se o utilizador pedir apenas o nome ou título do(s) manual(is) de uma máquina.
    - Usa `get_machine_n_model_manual` se o utilizador indicar nome e modelo da máquina, e desejar listar os manuais associados.
    - Usa `get_similarity_context` quando a pergunta for técnica ou detalhada, e precisares de procurar o conteúdo dentro dos manuais (ex: procedimentos, segurança, manutenção, tempos, riscos).
    - Usa `handle_inappropriate_question` se a pergunta não for técnica ou não estiver relacionada com manuais de máquinas-ferramenta, ou ots.
    - Usa `who_am_i` se o utilizador perguntar sobre a tua identidade ou função.
    - Usa `get_ots_info` se o utilizador perguntar sobre o conteudo das **OT's** de uma máquina específica, indicando nome, modelo, bd e op.
    - Usa `get_ots_info_by_intervencao` se o utilizador perguntar sobre o conteudo das **OT's** de uma dada intervenção.
    - Usa `get_fos_info` se o utilizador perguntar sobre o conteudo de uma **FOS** (Folha de Operação Standard) de uma máquina específica, indicando nome, modelo e tipo.


    Segue esta lógica de decisão:
    Exemplos:
    1. Pergunta: "Que manuais existem para a máquina EMAG?"
    ⇒ Usa: `get_machine_manual`

    2. Pergunta: "Que manuais estão disponíveis para a EMAG VL4?"
    ⇒ Usa: `get_machine_n_model_manual`

    3. Pergunta: "Qual o intervalo de substituição do vidro de segurança da EMAG VL4?"
    ⇒ Usa: `get_similarity_context`

    4. Pergunta: "Quantas tabelas tem a base de dados?"
    ⇒ Usa: `get_table_info`

    5. Pergunta: "Qual é a tua opinião sobre política?"
    ⇒ Usa: `handle_inappropriate_question` com motivo "Pergunta fora do âmbito técnico do assistente."

    6. Pergunta: "Quem és tu?"
    ⇒ Usa: `who_am_i`

    7. Pergunta: "Qual a última ot da máquina EMAG VL4 da BD100 OP110?"
    ⇒ Usa: `get_ots_info` com os parâmetros: maquina_nome="EMAG", modelo="VL4", bd="BD100", op="OP110", mais_recente=True

    8. Pergunta: "Ot's relativas à colisão do trackmotion?"
    ⇒ Usa: `get_ots_info_by_intervencao` com os parâmetros: temas="colisão do trackmotion" 

    9. Pergunta: "Como se faz o bloqueio da máquina EMAG VL8-Y?"
    ⇒ Usa: `get_fos_info` com os parâmetros: maquina_nome="EMAG", modelo="VL8-Y", tipo = "Bloqueio"

    Lembra-te: quando chamares uma função, deves usar o conteúdo retornado como **base principal da resposta final**.
    Não uses o conteúdo da pergunta do utilizador como base para a resposta. E através do conteudo da função, elabora uma resposta clara e objetiva, sem repetir o conteúdo da função e sem divergir do tema.
    """


    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"Pergunta: {question}"
        }
    ]

    # 1ª chamada para verificar se é necessária função
    response = client_ollama.chat.completions.create(
        model=llama_model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message
    

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        function_result = call_function(function_name, arguments, cursor, embedding_function, complete_query, question)

        messages.extend([
            {
                "role": "assistant",
                "content": None,
                "tool_calls": message.tool_calls
            },
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": function_result["content"]
            }
            ])
        
        # Definir a estrutura da resposta com base na função
        if function_name == "get_ots_info":
            response_structure = f"""
            Elabora a resposta com base na informação da função seguinte:

            {function_result['content']}

            Segue rigorosamente esta estrutura de resposta para OT:

            OT [número]  
            📅 Datas: [data de início] a [data de fim], no formato dd/mm/aaaa  
            🔧 Intervenção: [descrição]  
            🛠️ Atividade: [descrição]  
            💬 Comentário: [ou "Sem comentário."]
            🔗 Link: [link]
            """

        elif function_name == "get_machine_n_model_manual" or function_name == "get_machine_manual":
            response_structure = f"""
            Elabora a resposta com base na informação da função seguinte:

            {function_result['content']}

            Segue rigorosamente esta estrutura de resposta para Manuais:

            - Título do manual: [nome]  
            - Resumo técnico: [se aplicável]
            - Link de acesso ao manual: [link]
            """

        elif function_name == "get_ots_info_by_intervencao":
            response_structure = f"""
            Elabora a resposta com base na informação da função seguinte:

            {function_result['content']}

            Estrutura da resposta para Intervenções:
            """

        elif function_name == "get_similarity_context":
            response_structure = f"""
            Elabora a resposta com base na informação da função seguinte:

            {function_result['content']}

            Estrutura da resposta:

            - Conteúdo devolvido pela função: [conteúdo], deves usar este conteúdo como base para a resposta, deves incluir um resumo das 3 declarações fornecidas pela função get_similarity_context, porém detalhado.
            - No final deves incluir o link para o manual: [link]
            - Se não houver link, deves indicar que não existe link disponível.
            """

        elif function_name == "get_fos_info":
            response_structure = f"""
            Elabora a resposta com base na informação da função seguinte:

            {function_result['content']}

            Estrutura da resposta para FOS:
            - Ficha de Operação Standard: [nome]
            - Conteúdo: [conteúdo], deves usar a mesmo tipo de estrutura devolvida pela função, mas deves incluir um resumo desse conteúdo, porém detalhado.
            - No final deves incluir o link para a FOS: [link]
            """

        elif function_name == "handle_inappropriate_question":
            response_structure = f"""
            Elabora uma resposta na qual avisas o utilizador que a pergunta não é apropriada, relevante ou profissional no contexto de manuais de máquinas-ferramenta:

            {function_result['content']}
            """

        else:
            response_structure = f"""
            Elabora a resposta com base na informação da função seguinte:

            {function_result['content']}

            Mantém a estrutura profissional, clara e objetiva.
            """

        # Adiciona a instrução final ao fluxo de mensagens
        messages.append({
            "role": "user",
            "content": response_structure
        })

        follow_up = client_ollama.chat.completions.create(
            model=llama_model,
            messages=messages
        )

        # avaliação
        registar_interacao(
            pergunta=question,
            conteudo=function_result["content"],
            resposta=follow_up.choices[0].message.content,
            funcao=function_name
        )

        # Retorna a resposta final
        return follow_up.choices[0].message.content
    else:
        return message.content