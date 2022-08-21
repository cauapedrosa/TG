import time
import psycopg2
from config import config


def main():
    query = "UPDATE vaga_geral SET curso_id = 1"
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        print(f'\nExecuting Query: "{query}"')
        cur.execute(query)
        print(cur.fetchall())
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    start = time.perf_counter()
    main()
    print(f'\n🔥 Total time elapsed: {round(time.perf_counter() - start, 2)} seconds\n')

