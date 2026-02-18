import psycopg2

def discover_tables(host: str, port: int, database: str, username: str, password: str):
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=username,
        password=password,
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type='BASE TABLE'
          AND table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_schema, table_name;
    """)

    tables = cur.fetchall()

    results = []
    for schema, table in tables:
        results.append(f"{schema}.{table}")

    cur.close()
    conn.close()

    return results


def get_table_schema(host: str, port: int, database: str, username: str, password: str, schema: str, table: str):
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=username,
        password=password,
    )
    cur = conn.cursor()

    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
    """, (schema, table))

    cols = cur.fetchall()

    schema_json = {
        "schema": schema,
        "table": table,
        "columns": [
            {"name": c[0], "type": c[1], "nullable": c[2]}
            for c in cols
        ]
    }

    cur.close()
    conn.close()
    return schema_json
