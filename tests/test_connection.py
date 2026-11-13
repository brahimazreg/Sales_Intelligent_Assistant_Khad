from database.connection import get_connection , execute_read_query


def main():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT @@SERVERNAME, DB_NAME(), SYSTEM_USER")

    print(cursor.fetchone())
    print("*"*50)
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
    """)

    for row in cursor.fetchall():
        print(row[0])

    col , rows= execute_read_query("Select * from customers")
    print(col,'' , rows)
if __name__ =="__main__":
    main()