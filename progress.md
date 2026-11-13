# Progression du projet — Sales Intelligent Assistant Khady

## 1. Objectif du projet

Construire un assistant commercial intelligent basé sur SQL Server et un système RAG (Retrieval-Augmented Generation).

L'assistant devra comprendre les questions commerciales et exploiter les données de la base `sales_rag`.

## 2. Technologies utilisées

- Python
- SQL Server
- pyodbc
- SQLAlchemy
- Ollama
- LLM : `qwen3:8b`
- Modèle d'embeddings prévu : `nomic-embed-text:latest`
- FAISS (prévu pour la recherche vectorielle)

## 3. Configuration .env

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=qwen3:8b
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
```

1
Schéma métier

database/business_schema.json

Contient les 7 entités, leurs attributs et leurs relations.


2
Transformation en documents

rag/document_builder.py

Transforme chaque entité en texte compréhensible par le modèle.


3
Génération des embeddings

nomic-embed-text:latest

Convertit chaque document en vecteur numérique.


4
Stockage vectoriel

ChromaDB

Enregistre les documents, vecteurs et métadonnées.


5
Recherche RAG

RAG_TOP_K=6

Retrouve les documents pertinents pour répondre aux questions.