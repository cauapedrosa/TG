import time
import psycopg2
from config import config


def clear_duplicates():
    command = """DELETE FROM vaga_formatada
        WHERE ctid NOT IN (
        SELECT min(ctid) FROM vaga_formatada
        GROUP  BY titulo, descr
        ORDER BY titulo) RETURNING curso_id, titulo;"""

    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        print(f'##################\n>Executing Command:\n{command.strip()}\n')
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
    start = time.perf_counter()
    clear_duplicates()
    print(f'\n🔥 Total time elapsed: {round(time.perf_counter() - start, 2)} seconds\n')
