
import re
import sqlglot

from sqlglot import exp


FORBIDDEN_NODES = {
    "Insert", "Update", "Delete", "Drop", "Alter",
    "Create", "TruncateTable", "Merge", "Command",
    "Copy", "Transaction", "Into", "Grant", "Revoke"
}

FORBIDDEN_FUNCTIONS = {
    "OPENROWSET",
    "OPENDATASOURCE",
    "OPENQUERY",
    "XP_CMDSHELL"
}


def validate_sql(sql, schema):

    if not sql or not sql.strip():
        return False, "Requête vide."

    # Une seule instruction SQL
    try:
        statements = sqlglot.parse(sql, read="tsql")
    except Exception as error:
        return False, f"Erreur de syntaxe SQL : {error}"

    if len(statements) != 1 or statements[0] is None:
        return False, "Une seule instruction SQL est autorisée."

    tree = statements[0]

    # Seules les requêtes SELECT sont acceptées
    if not isinstance(tree, exp.Select):
        return False, "Seules les requêtes SELECT sont autorisées."

    # Tables autorisées
    allowed_tables = {
        name.lower()
        for name in schema.get("tables", {})
    }

    # Alias des CTE autorisés
    cte_names = {
        cte.alias.lower()
        for cte in tree.find_all(exp.CTE)
    }

    for node in tree.walk():

        node_name = type(node).__name__

        if node_name in FORBIDDEN_NODES:
            return False, f"Opération interdite : {node_name}"

        if isinstance(node, exp.Table):

            table_name = node.name.lower()

            if table_name not in allowed_tables and table_name not in cte_names:
                return False, f"Table non autorisée : {table_name}"

            # Interdiction des références inter-bases
            if node.catalog:
                return False, "Référence à une autre base interdite."

            if node.db and node.db.lower() != "dbo":
                return False, "Schéma SQL non autorisé."

        if isinstance(node, exp.Anonymous):

            if node.name.upper() in FORBIDDEN_FUNCTIONS:
                return False, "Fonction SQL interdite."

    # Refuser les constructions potentiellement dangereuses
    if re.search(
        r"\b(OPENROWSET|OPENDATASOURCE|OPENQUERY|XP_CMDSHELL)\b",
        sql,
        re.IGNORECASE
    ):
        return False, "Fonction SQL dangereuse détectée."

    return True, "Requête SQL validée."
