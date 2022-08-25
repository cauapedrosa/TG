import psycopg2
from config import config


def create_tables():
    commands = ("""
    DROP TABLE IF EXISTS curso CASCADE;
    """, """
    DROP TABLE IF EXISTS vaga_formatada;
    """, """
    DROP TABLE IF EXISTS vaga_geral;
    """, """
    CREATE TABLE curso(
        curso_id int PRIMARY KEY,
        curso_titulo varchar NOT NULL
    )
    """, """
    CREATE TABLE vaga_formatada (
        URL varchar NOT NULL PRIMARY KEY,
        curso_id int NOT NULL,
        titulo varchar NOT NULL,
        descr varchar NOT NULL,
        empresa varchar,
		postDate Date,
		locale varchar
    )
    """, """
    CREATE TABLE vaga_geral (
        URL varchar NOT NULL PRIMARY KEY,
        curso_id int NOT NULL,
        titulo varchar NOT NULL,
        descr varchar NOT NULL,
        empresa varchar,
		postDate Date,
		locale varchar
    )
    """)
    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        for command in commands:
            cur.execute(command)
            print(f'\n#########################################\nExecuting: {command}')
            print(f'Status: {cur.statusmessage}')

        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
