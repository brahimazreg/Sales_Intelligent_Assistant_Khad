
import json
import urllib.request
import urllib.error

from rag.document_builder import build_documents


# Configuration Ollama
OLLAMA_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text:latest"


def generate_embeddings(documents):
    """
    Génère les embeddings des documents avec Ollama.
    """

    if not documents:
        raise ValueError("Aucun document à traiter.")

    # Récupérer les textes
    texts = [doc["text"] for doc in documents]

    # Préparer la requête Ollama
    payload = {
        "model": EMBED_MODEL,
        "input": texts
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

    if len(embeddings) != len(documents):
        raise ValueError(
            "Le nombre d'embeddings ne correspond pas "
            "au nombre de documents."
        )

    # Associer chaque document à son embedding
    embedded_documents = []

    for doc, embedding in zip(documents, embeddings):

        embedded_documents.append({
            "id": doc["id"],
            "text": doc["text"],
            "metadata": doc["metadata"],
            "embedding": embedding
        })

    return embedded_documents


if __name__ == "__main__":

    print("Chargement des documents...")

    documents = build_documents()

    print("Nombre de documents :", len(documents))
    print("\nGénération des embeddings avec Ollama...")

    results = generate_embeddings(documents)

    print("\nEMBEDDINGS GENERES AVEC SUCCES !")
    print("Nombre de vecteurs :", len(results))

    if results:
        print("Dimension du vecteur :", len(results[0]["embedding"]))

    print("\nDocuments prêts pour ChromaDB !")
