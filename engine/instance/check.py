import psycopg2
from config import config


def check():
    commands = (
        # """DELETE FROM vaga_formatada WHERE curso_id = 2""",
        """SELECT count(*) FROM curso""",
        """SELECT count(c.curso_id), c.curso_id, c.curso_titulo FROM vaga_formatada v JOIN curso c ON v.curso_id = c.curso_id GROUP BY c.curso_id ORDER BY count(c.curso_id) DESC""",
        """SELECT count(c.curso_id), c.curso_id, c.curso_titulo FROM vaga_geral v JOIN curso c ON v.curso_id = c.curso_id GROUP BY c.curso_id ORDER BY count(c.curso_id) DESC""")
    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        for counter, command in enumerate(commands):
            print(
                f'\n>Executing Command #{counter+1}/{len(commands)}:\n{command.strip()}:')
            cur.execute(command)
            print(f'Status: {cur.statusmessage}')
            # aux = cur.fetchall()
            # for row in aux:
            #     print(row)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    print("\n\n################## RUNNING CHECK.PY:\n")
    check()
