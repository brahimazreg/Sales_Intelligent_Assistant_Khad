
import json
import urllib.request
import urllib.error

from llm.sql_generator import generate_sql
from services.sql_executor import execute_sql


OLLAMA_URL = "http://localhost:11434/api/chat"
LLM_MODEL = "qwen3:8b"


def generate_natural_answer(question, sql, result):
    """
    Transforme les résultats SQL en réponse compréhensible.
    """

    if not result["rows"]:
        return "Aucun résultat n'a été trouvé pour cette question."

    data = {
        "columns": result["columns"],
        "rows": result["rows"],
        "row_count": result["row_count"],
        "truncated": result["truncated"]
    }

    system_prompt = """
Tu es Sales Intelligent Assistant Khady,
un assistant spécialisé dans l'analyse commerciale.

Tu dois répondre en français, de manière claire,
professionnelle et concise.

Règles :
- Base-toi exclusivement sur les résultats SQL fournis.
- N'invente aucun chiffre ni aucune information.
- Présente les résultats de façon lisible.
- Explique brièvement ce que montrent les résultats.
- Si les résultats sont incomplets, précise-le.
- Ne montre pas ton raisonnement interne.
"""

    user_prompt = f"""
Question de l'utilisateur :
{question}

Requête SQL exécutée :
{sql}

Résultats obtenus :
{json.dumps(data, ensure_ascii=False, default=str, indent=2)}

Formule une réponse claire à l'utilisateur.
"""

    payload = {
        "model": LLM_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "options": {
            "temperature": 0.2
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        answer = result.get("message", {}).get(
            "content", ""
        ).strip()

        return answer or "Impossible de générer une réponse."

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Erreur lors de la génération de la réponse : {error}"
        ) from error


def ask_assistant(question):
    """
    Pipeline complet :
    Question -> RAG -> SQL -> Validation -> Exécution -> Réponse.
    """

    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    # 1. Génération SQL à partir du contexte RAG
    sql = generate_sql(question)

    # 2. Validation et exécution SQL
    # execute_sql appelle déjà validate_sql()
    result = execute_sql(sql)

    # 3. Génération de la réponse naturelle
    answer = generate_natural_answer(
        question,
        sql,
        result
    )

    return {
        "question": question,
        "sql": sql,
        "result": result,
        "answer": answer
    }


if __name__ == "__main__":

    print("\n======================================")
    print(" SALES INTELLIGENT ASSISTANT KHADY")
    print("======================================")

    while True:

        question = input("\nVotre question (ou 'exit' pour quitter) : ")

        if question.strip().lower() in ["exit", "quit", "quitter"]:
            print("\nAu revoir !")
            break

        try:
            response = ask_assistant(question)

            print("\nREQUÊTE SQL GÉNÉRÉE :")
            print("-" * 50)
            print(response["sql"])

            print("\nRÉPONSE DE L'ASSISTANT :")
            print("-" * 50)
            print(response["answer"])

        except Exception as error:
            print("\nUne erreur est survenue :")
            print(error)
