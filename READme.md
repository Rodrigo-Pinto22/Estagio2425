# 🛠️ Assistente Técnico de Máquinas-Ferramenta

Este projeto fornece um assistente baseado em linguagem natural para consulta de manuais técnicos de máquinas-ferramenta. O sistema está preparado para operar tanto em linha de comandos (terminal) como através de uma interface gráfica via Streamlit.

---

## 📦 Estrutura do Projeto

```
├── main.py                     # Interface terminal
├── charts_api.py               # Endpoint FastAPI responsável pelo envio dos dados estatísticos para o dashboard
├── chatcom.py                  # Endpoint FastAPI que interage com o frontend, processando perguntas e devolvendo respostas do modelo
├── functions.py                # Função principal `gen_answer`
├── tools.py                    # Definição JSON das ferramentas disponíveis
├── tools_logic.py              # Lógica que liga as tools às funções reais
├── function.py                 # Implementações das funções
├── db_con.py                   # Conexão à base de dados PostgreSQL
├── query_logic.py              # Query base para pesquisa por similaridade
├── eval.py                     # Script para avaliação do sistema através de perguntas predefinidas em ficheiro local (modo terminal)
├── README.md                   # Este ficheiro :)
```

---

## ⚙️ Requisitos

- Python 3.9+
- PostgreSQL com a base de dados `ChatbotDB`
- Ollama com o modelo `llama3.2` ativo localmente

### Instalar dependências:
```bash
pip install streamlit psycopg2 openai
```

---

## 🧠 Execução via terminal

```bash
python main.py
```


## 💬 Execução via interface gráfica (Angular)

```bash
uvicorn charts_api:app --reload --host 0.0.0.0 --port 8000
uvicorn chatcom:app --reload --host 0.0.0.0 --port 5000
ng serve
```

---

## 🗂️ Base de Dados
Certifica-te de que tens as seguintes tabelas na base de dados `ChatbotDB`, incluindo:
- `manuais`
- `maquina`
- `maquina_manuais`
- `conteudo` com vetores (`vector(384)`) para pesquisa semântica

---

## 🔐 Perguntas inapropriadas
O sistema deteta e responde educadamente a perguntas fora de contexto técnico com a função:
```python
handle_inappropriate_question()
```

---

## ✍️ Contribuição
Sugestões, melhorias e extensões são bem-vindas!

---

## 📜 Licença
Projeto académico e experimental – uso interno e educacional.
