
import chromadb
from pathlib import Path

from rag.document_builder import build_documents
from rag.embedding_manager import generate_embeddings


# Configuration ChromaDB
BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_PATH = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "sales_business_schema"


def save_to_chroma(embedded_documents):
    """
    Enregistre les documents et leurs embeddings
    dans une base ChromaDB persistante.
    """

    # Créer le dossier si nécessaire
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    # Connexion à ChromaDB
    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    # Créer ou récupérer la collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # Préparer les données
    ids = [doc["id"] for doc in embedded_documents]

    texts = [
        doc["text"] for doc in embedded_documents
    ]

    metadatas = [
        doc["metadata"] for doc in embedded_documents
    ]

    embeddings = [
        doc["embedding"] for doc in embedded_documents
    ]

    # Enregistrer ou mettre à jour les documents
    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return collection


if __name__ == "__main__":

    print("Chargement des documents...")

    documents = build_documents()

    print("Nombre de documents :", len(documents))

    print("\nGénération des embeddings...")

    embedded_documents = generate_embeddings(documents)

    print("\nEnregistrement dans ChromaDB...")

    collection = save_to_chroma(embedded_documents)

    print("\nSTOCKAGE CHROMADB TERMINE !")
    print("Collection :", COLLECTION_NAME)
    print("Nombre de documents enregistrés :", collection.count())
    print("Emplacement :", CHROMA_PATH)
