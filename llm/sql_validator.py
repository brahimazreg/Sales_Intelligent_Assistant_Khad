
import re


FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "EXEC",
    "EXECUTE",
    "MERGE",
    "GRANT",
    "REVOKE",
    "DENY",
    "BACKUP",
    "RESTORE",
    "DBCC",
    "SHUTDOWN",
    "INTO",
    "WAITFOR",
    "OPENROWSET",
    "OPENDATASOURCE",
    "BULK",
]


def validate_sql(sql):
    """
    Validation conservatrice des requêtes SQL Server.
    Accepte uniquement une requête SELECT simple.
    """

    if not isinstance(sql, str) or not sql.strip():
        return False, "La requête SQL est vide."

    sql = sql.strip()

    # 1. Refuser les commentaires SQL
    if "--" in sql or "/*" in sql or "*/" in sql:
        return False, "Les commentaires SQL ne sont pas autorisés."

    # 2. Refuser les instructions multiples
    # Un seul point-virgule final est toléré.
    sql_without_final_semicolon = sql.rstrip()

    if sql_without_final_semicolon.endswith(";"):
        sql_without_final_semicolon = (
            sql_without_final_semicolon[:-1].rstrip()
        )

    if ";" in sql_without_final_semicolon:
        return False, "Plusieurs instructions SQL sont interdites."

    # 3. Vérifier que la requête commence par SELECT
    if not re.match(r"^SELECT\b", sql_without_final_semicolon, re.IGNORECASE):
        return False, "Seules les requêtes SELECT sont autorisées."

    # 4. Refuser les mots-clés dangereux
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = rf"\b{re.escape(keyword)}\b"

        if re.search(pattern, sql_without_final_semicolon, re.IGNORECASE):
            return False, f"Mot-clé SQL interdit : {keyword}"

    # 5. Refuser certaines fonctions système sensibles
    dangerous_functions = [
        "XP_CMDSHELL",
        "SP_CONFIGURE",
        "SP_OACREATE",
        "SP_OAMETHOD",
    ]

    for function in dangerous_functions:
        if re.search(
            rf"\b{re.escape(function)}\b",
            sql_without_final_semicolon,
            re.IGNORECASE
        ):
            return False, f"Fonction SQL interdite : {function}"

    return True, "Requête SQL acceptée."


if __name__ == "__main__":

    test_queries = [
        """
        SELECT TOP 5 c.company_name,
               COUNT(o.order_id) AS order_count
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.company_name
        ORDER BY order_count DESC;
        """,

        "DELETE FROM customers",

        "DROP TABLE customers",

        "SELECT * FROM customers; DELETE FROM customers",

        "EXEC xp_cmdshell 'dir'",
    ]

    for query in test_queries:
        valid, message = validate_sql(query)

        print("\nRequête :")
        print(query.strip())

        print("Résultat :", message)
