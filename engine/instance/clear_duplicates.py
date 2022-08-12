import psycopg2
from config import config


def clear_duplicates():
    command = """DELETE FROM vaga_geral
        WHERE ctid NOT IN (
        SELECT min(ctid) FROM vaga_geral
        GROUP  BY titulo, descr, empresa
        ORDER BY empresa) RETURNING titulo, empresa;"""

    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        print(f'##################\n>Executing Command:\n{command.strip()}:')
        cur.execute(command)
        output = cur.fetchall()
        for row in output:
            print(row)
        print(f'-> Result description: {cur.description}')
        print(f'-> Affected rows: {cur.rowcount}')
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    clear_duplicates()
