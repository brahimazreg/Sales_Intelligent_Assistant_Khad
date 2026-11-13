
import json
import re
import urllib.request
import urllib.error

from rag.retriever import retrieve_documents


OLLAMA_URL = "http://localhost:11434/api/chat"
LLM_MODEL = "qwen3:8b"


def generate_answer(question, top_k=3):
    """
    Récupère les documents pertinents dans ChromaDB
    puis génère une réponse avec Ollama.
    """

    # 1. Recherche des documents pertinents
    documents = retrieve_documents(question, top_k=top_k)

    if not documents:
        return "Je n'ai trouvé aucune information pertinente dans la base documentaire."

    # 2. Construction du contexte
    context_parts = []

    for index, document in enumerate(documents, start=1):
        metadata = document.get("metadata", {})
        table = metadata.get("table", "inconnue")
        text = document.get("text", "")

        context_parts.append(
            f"Document {index} - Table : {table}\n{text}"
        )

    context = "\n\n".join(context_parts)

    # 3. Préparation du prompt
    system_prompt = """
Tu es un assistant intelligent spécialisé dans les bases de données commerciales.

Tu dois répondre en français, de manière claire, précise et professionnelle.

Règles :
- Utilise uniquement les informations fournies dans le contexte.
- N'invente jamais de tables, colonnes ou informations.
- Si le contexte ne permet pas de répondre, indique-le clairement.
- Cite les noms des tables et des colonnes lorsque c'est pertinent.
- Ne montre jamais ton raisonnement interne.
- Donne uniquement la réponse finale.
"""

    user_prompt = f"""
Question :
{question}

Contexte documentaire :
{context}

Réponds à la question en utilisant uniquement ce contexte.
"""

    # 4. Appel du modèle Ollama
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
            result = json.loads(response.read().decode("utf-8"))

        answer = result.get("message", {}).get("content", "").strip()

        # Suppression éventuelle des blocs de raisonnement
        answer = re.sub(
            r"<think>.*?</think>",
            "",
            answer,
            flags=re.DOTALL
        ).strip()

        if not answer:
            return "Le modèle n'a pas généré de réponse."

        return answer

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Impossible de contacter Ollama : {error}"
        ) from error

    except (json.JSONDecodeError, KeyError) as error:
        raise RuntimeError(
            f"Réponse Ollama invalide : {error}"
        ) from error


if __name__ == "__main__":
    question = input("\nPose ta question : ")

    try:
        answer = generate_answer(question)

        print("\nRéponse de l'assistant :")
        print("-" * 50)
        print(answer)

    except Exception as error:
        print(f"\nErreur : {error}")
