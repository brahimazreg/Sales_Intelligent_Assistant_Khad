
import os
import pyodbc

from dotenv import load_dotenv

load_dotenv()


def get_connection():

    connection_string = os.getenv(
        "SQL_SERVER_CONNECTION_STRING"
    )

    if not connection_string:
        raise RuntimeError(
            "Connexion SQL Server non configurée."
        )

    connection = pyodbc.connect(
        connection_string,
        timeout=10,
        autocommit=False
    )

    return connection


def execute_read_query(sql):

    connection = get_connection()

    try:
        cursor = connection.cursor()
        
        cursor.execute(sql)

        if not cursor.description:
            raise RuntimeError(
                "La requête n'a retourné aucun jeu de résultats."
            )

        columns = [
            column[0]
            for column in cursor.description
        ]

        rows = cursor.fetchmany(500)

        return columns, rows

    finally:
        connection.rollback()
        connection.close()
