
import json
import os
import requests

from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

from services.schema_database import extract_schema


# ============================================================
# 2. NOMS DES ENTITES METIER
# ============================================================

ENTITY_NAMES = {
    "categories": "Categorie",
    "customers": "Client",
    "order_items": "Ligne de commande",
    "orders": "Commande",
    "products": "Produit",
    "sales_reps": "Commercial",
    "suppliers": "Fournisseur"
}


# ============================================================
# 3. FONCTION DE GENERATION DES DESCRIPTIONS
# ============================================================

def generate_table_description(table_name, table_schema, base_url, model):

    columns = table_schema.get("columns", [])

    # Informations techniques transmises au modele
    table_info = {
        "table": table_name,
        "columns": columns,
        "primary_key": table_schema.get("primary_key", []),
        "foreign_keys": table_schema.get("foreign_keys", [])
    }

    prompt = f"""
Tu es un expert en bases de donnees et en analyse metier.

Analyse cette table SQL et explique son role dans une
application commerciale.

Schema de la table :

{json.dumps(table_info, ensure_ascii=False)}

Retourne uniquement un JSON valide avec cette structure :

{{
    "description": "Description metier de la table",
    "attributes": [
        {{
            "column": "nom_exact_de_la_colonne",
            "meaning": "Explication metier de la colonne"
        }}
    ]
}}

Regles :
- Conserve exactement les noms des colonnes.
- Fournis une explication pour chaque colonne.
- N'invente aucune information.
- Si une signification est incertaine, reste descriptif.
- Reponds uniquement avec le JSON.
"""

    response = requests.post(
        f"{base_url.rstrip('/')}/api/chat",
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Tu es un expert en bases de donnees. "
                        "Tu reponds uniquement avec du JSON valide."
                    )
                },
                {
                    "role": "user",
                    "content": prompt + "\n/no_think"
                }
            ],
            "stream": False,
            "think": False,
            "format": "json",
            "options": {
                "temperature": 0,
                "num_predict": 1500
            }
        },
        timeout=300
    )

    response.raise_for_status()

    ollama_data = response.json()

    result = ollama_data.get("message", {}).get("content", "")

    if not result.strip():
        raise ValueError(
            f"Qwen3 a retourne une reponse vide pour la table {table_name}."
        )

    generated_data = json.loads(result)

    if not isinstance(generated_data, dict):
        raise ValueError(
            f"Reponse JSON invalide pour la table {table_name}."
        )

    return generated_data


# ============================================================
# 4. CONSTRUCTION DES RELATIONS
# ============================================================

def build_relations(schema):

    relations_by_table = {
        table_name: []
        for table_name in schema
    }

    for table_name, table_schema in schema.items():

        foreign_keys = table_schema.get("foreign_keys", [])

        for fk in foreign_keys:

            referenced_table = fk.get("references_table")

            if referenced_table not in schema:
                continue

            local_columns = fk.get("columns", [])
            referenced_columns = fk.get("references_columns", [])

            # Relation depuis la table qui porte la cle etrangere
            relations_by_table[table_name].append({
                "entity": ENTITY_NAMES.get(
                    referenced_table,
                    referenced_table
                ),
                "type": "many-to-one",
                "description": (
                    f"La table {table_name} reference "
                    f"{referenced_table} via "
                    f"{local_columns} vers {referenced_columns}."
                )
            })

            # Relation inverse
            relations_by_table[referenced_table].append({
                "entity": ENTITY_NAMES.get(
                    table_name,
                    table_name
                ),
                "type": "one-to-many",
                "description": (
                    f"La table {referenced_table} peut etre "
                    f'associee a plusieurs enregistrements de '
                    f"{table_name}."
                )
            })

    return relations_by_table


# ============================================================
# 5. GENERATION DU SCHEMA METIER COMPLET
# ============================================================

def generate_business_schema():

    print("\n========================================")
    print("   GENERATION DU SCHEMA METIER")
    print("========================================\n")

    base_url = os.getenv("OLLAMA_BASE_URL")
    model = os.getenv("OLLAMA_LLM_MODEL")

    if not base_url:
        raise ValueError("OLLAMA_BASE_URL absent du fichier .env")

    if not model:
        raise ValueError("OLLAMA_LLM_MODEL absent du fichier .env")

    print("Modele utilise :", model)

    # --------------------------------------------------------
    # Extraction SQL
    # --------------------------------------------------------

    print("\n[1/4] Extraction du schema SQL...")

    schema = extract_schema()

    if not schema:
        raise ValueError("Aucune table SQL detectee.")

    print("Nombre de tables :", len(schema))

    # --------------------------------------------------------
    # Relations techniques
    # --------------------------------------------------------

    print("\n[2/4] Construction des relations...")

    relations_by_table = build_relations(schema)

    # --------------------------------------------------------
    # Generation table par table
    # --------------------------------------------------------

    print("\n[3/4] Enrichissement avec Qwen3...")

    entities = []

    for index, (table_name, table_schema) in enumerate(
        schema.items(),
        start=1
    ):

        entity_name = ENTITY_NAMES.get(table_name, table_name)

        print(
            f"\nTable {index}/{len(schema)} : "
            f"{table_name}"
        )

        try:

            generated_data = generate_table_description(
                table_name,
                table_schema,
                base_url,
                model
            )

            description = generated_data.get(
                "description",
                f"Entite metier correspondant a la table {table_name}."
            )

            generated_attributes = generated_data.get(
                "attributes",
                []
            )

            # Indexer les significations produites par Qwen3
            meanings = {}

            if isinstance(generated_attributes, list):

                for attribute in generated_attributes:

                    if isinstance(attribute, dict):
                        column = attribute.get("column")
                        meaning = attribute.get("meaning")

                        if column and meaning:
                            meanings[column] = meaning

            # Reconstruire les attributs depuis le vrai schema SQL
            attributes = []

            for column_info in table_schema.get("columns", []):

                column_name = column_info["name"]

                meaning = meanings.get(
                    column_name,
                    f"Colonne {column_name} de la table {table_name}."
                )

                attributes.append({
                    "column": column_name,
                    "type": column_info.get("type"),
                    "nullable": column_info.get("nullable"),
                    "meaning": meaning
                })

            entity = {
                "name": entity_name,
                "table": table_name,
                "description": description,
                "primary_key": table_schema.get("primary_key", []),
                "attributes": attributes,
                "relations": relations_by_table.get(table_name, [])
            }

            entities.append(entity)

            print("Description generee avec succes.")
            print("Nombre de colonnes :", len(attributes))
            print(
                "Nombre de relations :",
                len(entity["relations"])
            )

        except requests.exceptions.Timeout as error:

            raise RuntimeError(
                f"Timeout Ollama sur la table {table_name}. "
                "Le modele met trop de temps a repondre."
            ) from error

        except requests.exceptions.RequestException as error:

            raise RuntimeError(
                f"Erreur de communication avec Ollama "
                f"pour la table {table_name} : {error}"
            ) from error

        except (json.JSONDecodeError, ValueError) as error:

            raise RuntimeError(
                f"Erreur de generation pour la table {table_name} : "
                f"{error}"
            ) from error

    # --------------------------------------------------------
    # Assemblage final
    # --------------------------------------------------------

    business_schema = {
        "project": "Sales Intelligent Assistant Khady",
        "description": (
            "Schema metier genere a partir de la base SQL Server."
        ),
        "entities": entities
    }

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    expected_tables = set(schema.keys())

    generated_tables = {
        entity["table"]
        for entity in entities
    }

    if expected_tables != generated_tables:

        raise ValueError(
            "Les tables generees ne correspondent pas "
            "aux tables SQL extraites."
        )

    # --------------------------------------------------------
    # Sauvegarde
    # --------------------------------------------------------

    print("\n[4/4] Sauvegarde du schema metier...")

    output_file = DATABASE_DIR / "business_schema.json"

    with open(output_file, "w", encoding="utf-8") as file:

        json.dump(
            business_schema,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========================================")
    print("SCHEMA METIER GENERE AVEC SUCCES !")
    print("========================================")

    print("Nombre d'entites :", len(entities))
    print("Fichier :", output_file)

    return business_schema


# ============================================================
# 6. EXECUTION PRINCIPALE
# ============================================================

if __name__ == "__main__":

    generate_business_schema()
