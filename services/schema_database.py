
import os
import json
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "database"


def extract_schema():

    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    driver = os.getenv("DB_DRIVER")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    # Vérification des variables de connexion
    required_variables = {
        "DB_SERVER": server,
        "DB_NAME": database,
        "DB_DRIVER": driver,
        "DB_USER": username,
        "DB_PASSWORD": password,
    }

    missing = [
        key for key, value in required_variables.items()
        if not value
    ]

    if missing:
        raise ValueError(
            f"Variables manquantes dans .env : {missing}"
        )

    # Construction de la chaîne ODBC
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "TrustServerCertificate=yes;"
    )

    connection_url = (
        "mssql+pyodbc:///?odbc_connect="
        + quote_plus(connection_string)
    )

    engine = create_engine(connection_url)

    try:
        inspector = inspect(engine)
        schema = {}

        tables = inspector.get_table_names()

        for table in tables:

            columns = inspector.get_columns(table)
            primary_key = inspector.get_pk_constraint(table)
            foreign_keys = inspector.get_foreign_keys(table)

            schema[table] = {
                "columns": [
                    {
                        "name": column["name"],
                        "type": str(column["type"]),
                        "nullable": column["nullable"],
                    }
                    for column in columns
                ],

                "primary_key": (
                    primary_key.get("constrained_columns") or []
                ),

                "foreign_keys": [
                    {
                        "columns": fk["constrained_columns"],
                        "references_table": fk["referred_table"],
                        "references_columns": fk["referred_columns"],
                    }
                    for fk in foreign_keys
                ],
            }

        # Sauvegarde du schéma technique
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)

        schema_path = DATABASE_DIR / "schema.json"

        with open(schema_path, "w", encoding="utf-8") as file:
            json.dump(
                schema,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(f"Extraction terminée : {len(schema)} tables.")
        print(f"Fichier généré : {schema_path}")

        return schema

    finally:
        engine.dispose()


if __name__ == "__main__":
    extract_schema()
