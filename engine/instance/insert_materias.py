import time
import psycopg2
from config import config


def insert_cursos(cursos):
    sql = "INSERT INTO curso VALUES(%s,%s)"
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE curso")
        for i, curso in enumerate(cursos):
            print(f"Inserting curso {i+1}/{len(cursos)}: {curso}")
            cur.execute(sql, (i+1, curso))
            # print(cur.statusmessage)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    start = time.perf_counter()
    insert_cursos([
        ('Indefinido',),
        ('Análise e Desenvolvimento de Sistemas',),
        ('Comércio Exterior',),
        ('Eletrônica Automotiva',),
        ('Fabricação Mecânica',),
        ('Gestão da Qualidade',),
        ('Gestão de Serviços',),
        ('Gestão Empresarial',),
        ('Logística',),
        ('Logística Aeroportuária',),
        ('Manufatura Avançada',),
        ('Polímeros',),
        ('Processos Metalúrgicos',),
        ('Projetos Mecânicos',),
        ('Redes de Computadores',),
        ('Sistemas Biomédicos',),
    ])
    print(
        f'\n🔥 Total time elapsed: {round(time.perf_counter() - start, 2)} seconds\n')
