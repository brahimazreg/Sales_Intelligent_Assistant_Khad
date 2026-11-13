
import json
import urllib.request
import urllib.error
from pathlib import Path

import chromadb


# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_PATH = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "sales_business_schema"

OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text:latest"

DEFAULT_TOP_K = 6


def generate_query_embedding(question):
    """
    Transforme une question en embedding avec Ollama.
    """

    payload = {
        "model": EMBED_MODEL,
        "input": question
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Impossible de contacter Ollama : {error}"
        )

    embeddings = result.get("embeddings", [])

    if not embeddings:
        raise ValueError("Aucun embedding généré pour la question.")

    return embeddings[0]


def retrieve_documents(question, top_k=DEFAULT_TOP_K):
    """
    Recherche les documents les plus pertinents dans ChromaDB.
    """

    if not question or not question.strip():
        raise ValueError("La question ne peut pas être vide.")

    # Connexion à ChromaDB
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    # Récupérer la collection existante
    try:
        collection = client.get_collection(
            name=COLLECTION_NAME
        )
    except Exception as error:
        raise RuntimeError(
            f"Collection ChromaDB introuvable : {error}"
        )

    # Vérifier le nombre de documents
    total_documents = collection.count()

    if total_documents == 0:
        return []

    # Limiter top_k au nombre de documents disponibles
    top_k = min(top_k, total_documents)

    # Transformer la question en embedding
    query_embedding = generate_query_embedding(question)

    # Recherche sémantique
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Organiser les résultats
    documents = []

    for i in range(len(results["ids"][0])):

        documents.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return documents


if __name__ == "__main__":

    print("ASSISTANT RAG - RECHERCHE SEMANTIQUE")

    question = input("\nPose ta question : ")

    print("\nRecherche dans ChromaDB...\n")

    results = retrieve_documents(question)

    if not results:
        print("Aucun document trouvé.")

    else:
        print("DOCUMENTS PERTINENTS TROUVES :")

        for i, doc in enumerate(results, start=1):

            print("\n" + "=" * 60)
            print(f"Résultat {i}")
            print("ID :", doc["id"])
            print("Table :", doc["metadata"].get("table"))
            print("Distance :", round(doc["distance"], 4))
            print("\nContenu :")
            print(doc["text"])
