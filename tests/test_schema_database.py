from services.schema_database import extract_schema


def main():
    schema = extract_schema()

    for table, details in schema.items():

        print(f"\nTABLE : {table}")

        print("Colonnes :")
        for column in details["columns"]:
            print(
                f"  - {column['name']} "
                f"({column['type']})"
            )

        print("Clé primaire :", details["primary_key"])

        print("Clés étrangères :")
        for fk in details["foreign_keys"]:
            print(f"  - {fk}")

if __name__ =="__main__":
    main()