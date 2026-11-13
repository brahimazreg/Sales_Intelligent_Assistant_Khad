
import json
from pathlib import Path


# Chemin du projet
BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "database" / "business_schema.json"


def build_documents():

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {SCHEMA_PATH}"
        )

    # Charger le schéma métier
    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        schema = json.load(file)

    documents = []

    # Parcourir les entités
    for entity in schema.get("entities", []):

        entity_name = entity.get("name", "Entité inconnue")
        table_name = entity.get("table", "")
        description = entity.get("description", "")

        content = f"""
Entité : {entity_name}
Table SQL : {table_name}

Description :
{description}
"""

        # Ajouter la clé primaire
        primary_keys = entity.get("primary_key", [])

        if primary_keys:
            content += "\nClé primaire :\n"
            for key in primary_keys:
                content += f"- {key}\n"

        # Ajouter les attributs / colonnes
        attributes = entity.get("attributes", [])

        content += "\nColonnes :\n"

        for attribute in attributes:

            column = attribute.get("column", "")
            column_type = attribute.get("type", "")
            meaning = attribute.get("meaning", "")
            nullable = attribute.get("nullable", False)

            content += (
                f"- {column} ({column_type})\n"
                f"  Signification : {meaning}\n"
                f"  Nullable : {nullable}\n"
            )

        # Ajouter les relations
        relations = entity.get("relations", [])

        if relations:
            content += "\nRelations :\n"

            for relation in relations:

                related_entity = relation.get("entity", "")
                relation_type = relation.get("type", "")
                relation_description = relation.get("description", "")

                content += (
                    f"- Avec {related_entity}\n"
                    f"  Type : {relation_type}\n"
                    f"  Description : {relation_description}\n"
                )

        # Créer le document
        documents.append({
            "id": table_name,
            "text": content.strip(),
            "metadata": {
                "entity": entity_name,
                "table": table_name,
                "source": "business_schema.json"
            }
        })

    return documents


if __name__ == "__main__":

    docs = build_documents()

    print("DOCUMENTS CREES AVEC SUCCES !")
    print("Nombre de documents :", len(docs))

    for doc in docs:
        print("\n" + "=" * 60)
        print("ID :", doc["id"])
        print(doc["text"])
