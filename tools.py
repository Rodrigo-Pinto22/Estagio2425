# tools.py
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_table_info",
            "description": "Descreve a estrutura das tabelas da base de dados documental.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_machine_manual",
            "description": "Obtém os manuais técnicos associados a uma máquina específica, com base no nome da marca.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_maquina": {
                        "type": "string",
                        "description": "Marca ou nome da máquina (ex: EMAG)"
                    }
                },
                "required": ["nome_maquina"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_machine_n_model_manual",
            "description": "Obtém os manuais técnicos associados a uma máquina específica, com base no nome da marca e modelo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_maquina": {
                        "type": "string",
                        "description": "Marca ou nome da máquina (ex: EMAG)"
                    },
                    "modelo": {
                        "type": "string",
                        "description": "Modelo da máquina (ex: VL4)"
                    }
                },
                "required": ["nome_maquina", "modelo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_similarity_context",
            "description": "Obtém os conteúdos mais relevantes com base em similaridade semântica para uma máquina específica (marca e modelo).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_maquina": {
                        "type": "string",
                        "description": "Marca da máquina (ex: EMAG)"
                    },
                    "modelo": {
                        "type": "string",
                        "description": "Modelo da máquina (ex: VL4)"
                    }
                },
                "required": ["nome_maquina", "modelo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "handle_inappropriate_question",
            "description": "Utiliza esta função quando a pergunta não for apropriada, relevante ou profissional no contexto de manuais de máquinas-ferramenta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "motivo": {
                        "type": "string",
                        "description": "Breve descrição do motivo pelo qual a pergunta é considerada inadequada"
                    }
                },
                "required": ["motivo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "who_am_i",
            "description": "Identifica quem é o assistente virtual e qual o seu papel.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ots_info",
            "description": "Consulta informações sobre ordens de trabalho (OTs) com base no nome da máquina, linha e operação, retornando a descrição da intervenção mais recente ou todas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "maquina_nome": {
                        "type": "string",
                        "description": "Nome da máquina, ex: 'EMAG'"
                    },
                    "modelo": {
                        "type": "string",
                        "description": "Modelo da máquina (ex: 'VL4')"
                    },
                    "bd": {
                        "type": "string",
                        "description": "Linha de produção da qual a máquina opera (ex: 'BD100')"
                    },
                    "op": {
                        "type": "string",
                        "description": "Operação de fabrico, específico dessa máquina (ex: 'OP110')"
                    },
                    "mais_recente": {
                        "type": "boolean",
                        "description": "Se verdadeiro, retorna apenas a OT mais recente",
                        "default": True
                    }
                },
                "required": ["maquina_nome", "modelo", "bd", "op", "mais_recente"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ots_info_by_intervencao",
            "description": "Pesquisa OTs com base em palavras-chave descritas na coluna 'intervencao', como avarias específicas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "termo_pesquisa": {
                        "type": "string",
                        "description": "Termo ou palavras-chave para procurar na coluna 'intervencao' (ex: 'colisão', 'trackmotion')"
                    },
                    "limite": {
                        "type": "integer",
                        "description": "Número máximo de OTs a retornar (ex: 5)",
                        "default": 5
                    }
                },
                "required": ["termo_pesquisa"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_fos_info",
            "description": "Consulta uma Folha de Operações Standard (FOS) associada a uma máquina, podendo filtrar por tipo (PMA, Bloqueio, Desbloqueio).",
            "parameters": {
                "type": "object",
                "properties": {
                    "maquina_nome": {
                        "type": "string",
                        "description": "Nome da máquina, ex: 'EMAG'"
                    },
                    "modelo": {
                        "type": "string",
                        "description": "Modelo da máquina (ex: 'VL4')"
                    },
                    "tipo": {
                        "type": "string",
                        "description": "Filtro opcional para o tipo de FOS, como 'PMA', 'Bloqueio' ou 'Desbloqueio'.",
                        "enum": ["PMA", "Bloqueio", "Desbloqueio"]
                    }
                },
                "required": ["maquina_nome", "maquina_modelo", "tipo"]
            }
        }
    }
]
