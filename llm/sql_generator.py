
import json
import re
import urllib.request
import urllib.error

from rag.retriever import retrieve_documents


OLLAMA_URL = "http://localhost:11434/api/chat"
LLM_MODEL = "qwen3:8b"


def generate_sql(question, top_k=4):
    """
    Génère une requête SQL Server à partir
    d'une question en langage naturel et du contexte RAG.
    """

    # 1. Récupération du schéma pertinent
    documents = retrieve_documents(question, top_k=top_k)

    if not documents:
        raise ValueError(
            "Aucune information pertinente trouvée dans le schéma."
        )

    # 2. Construction du contexte
    context_parts = []

    for document in documents:
        metadata = document.get("metadata", {})
        table = metadata.get("table", "inconnue")
        text = document.get("text", "")

        context_parts.append(
            f"Table : {table}\n{text}"
        )

    context = "\n\n".join(context_parts)

    # 3. Instructions données au modèle
    system_prompt = """
Tu es un expert en SQL Server et en bases de données commerciales.

Ta mission est de transformer une question en langage naturel
en une requête SQL Server correcte.

Règles obligatoires :
- Utilise uniquement les tables et colonnes présentes dans le contexte.
- Génère uniquement des requêtes SELECT.
- N'utilise jamais INSERT, UPDATE, DELETE, DROP, ALTER ou TRUNCATE.
- Utilise TOP pour limiter les résultats si nécessaire.
- Respecte les relations entre les tables.
- N'invente aucune colonne ni aucune table.
- Ne donne aucune explication.
- Ne montre jamais ton raisonnement.
- Retourne uniquement le SQL, sans bloc Markdown.
"""

    user_prompt = f"""
Schéma de la base de données :

{context}

Question de l'utilisateur :

{question}

Génère la requête SQL Server correspondante.
"""

    # 4. Préparation de l'appel Ollama
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
            "temperature": 0
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

        sql = result.get("message", {}).get("content", "").strip()

        # Suppression des éventuels blocs de raisonnement
        sql = re.sub(
            r"<think>.*?</think>",
            "",
            sql,
            flags=re.DOTALL
        ).strip()

        # Suppression des balises Markdown éventuelles
        sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\s*```$", "", sql)

        if not sql:
            raise ValueError("Le modèle n'a généré aucune requête SQL.")

        return sql.strip()

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Impossible de contacter Ollama : {error}"
        ) from error


if __name__ == "__main__":
    question = input("\nPose ta question SQL : ")

    try:
        sql = generate_sql(question)

        print("\nRequête SQL générée :")
        print("-" * 50)
        print(sql)

    except Exception as error:
        print(f"\nErreur : {error}")
