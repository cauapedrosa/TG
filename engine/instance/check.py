import psycopg2
from config import config


def check():
    commands = ("""
        SELECT count(c.curso_id), c.curso_id, c.curso_titulo FROM vaga_formatada v JOIN curso c ON v.curso_id = c.curso_id GROUP BY c.curso_id ORDER BY count(c.curso_id) DESC
        """, """
        SELECT count(c.curso_id), c.curso_id, c.curso_titulo FROM vaga_geral v JOIN curso c ON v.curso_id = c.curso_id GROUP BY c.curso_id ORDER BY count(c.curso_id) DESC
        """)
    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        for command in commands:
            cur.execute(command)
            print(f'EXECUTING: {command}')
            aux = cur.fetchall()
            print("(COUNT, CURSO_ID, CURSO_TITULO)")
            for row in aux:
                print(row)

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    print("\n\n##################")
    print(" RUNNING CHECK.PY:")
    check()