
import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

from llm.sql_validator import validate_sql


# Chargement du fichier .env situé à la racine du projet
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

CONNECTION_STRING = os.getenv("SQL_SERVER_CONNECTION_STRING")


def execute_sql(sql, max_rows=100):
    """
    Valide et exécute une requête SELECT sur SQL Server.

    Retourne :
        {
            "columns": [...],
            "rows": [...],
            "row_count": int,
            "truncated": bool
        }
    """

    # 1. Vérification de la requête
    is_valid, message = validate_sql(sql)

    if not is_valid:
        raise ValueError(f"Requête SQL refusée : {message}")

    # 2. Vérification de la configuration
    if not CONNECTION_STRING:
        raise RuntimeError(
            "SQL_SERVER_CONNECTION_STRING est absent du fichier .env."
        )

    # 3. Connexion à SQL Server
    connection = None

    try:
        connection = pyodbc.connect(
            CONNECTION_STRING,
            timeout=10
        )

        connection.timeout = 60

        # Limite le temps d'exécution de la requête
        cursor = connection.cursor()

        # 4. Exécution
        cursor.execute(sql)

        # Récupération des noms de colonnes
        columns = [column[0] for column in cursor.description]

        # 5. Récupération limitée des résultats
        results = cursor.fetchmany(max_rows + 1)

        truncated = len(results) > max_rows
        results = results[:max_rows]

        rows = [
            dict(zip(columns, row))
            for row in results
        ]

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": truncated
        }

    except pyodbc.Error as error:
        raise RuntimeError(
            f"Erreur SQL Server : {error}"
        ) from error

    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":

    query = """
    SELECT TOP 5
        c.company_name,
        COUNT(o.order_id) AS order_count
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    GROUP BY c.customer_id, c.company_name
    ORDER BY order_count DESC;
    """

    try:
        result = execute_sql(query)

        print("\nCOLONNES :")
        print(result["columns"])

        print("\nRÉSULTATS :")

        for row in result["rows"]:
            print(row)

        print("\nNombre de lignes :", result["row_count"])

        if result["truncated"]:
            print("Attention : résultats limités.")

    except Exception as error:
        print("\nErreur :", error)
