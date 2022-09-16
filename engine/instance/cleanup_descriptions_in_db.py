from time import perf_counter
import time
import traceback
import psycopg2
from config import config
import sys
sys.path.append('C:/Users/xarys/Documents/GitHub/TG/engine')
import scraper_aux as aux


def update(url, descr):
    command = "UPDATE vaga_formatada SET descr = %s WHERE url = %s;"
    conn = None

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(command, (descr, url))
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f'⚠️ Error: {error}')
        traceback.print_exc()
    finally:
        if conn is not None:
            conn.close()


def get_jobs():
    command = "SELECT url, descr FROM vaga_formatada;"
    conn = None
    jobs = []

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(command)
        aux = cur.fetchall()
        for row in aux:
            jobs.append(row)
            # print(f'Appending: {row}')
        print(f'Row Count: {cur.rowcount}\n')
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f'⚠️ Error: {error}')
        traceback.print_exc()
    finally:
        if conn is not None:
            conn.close()
        if jobs is not None:
            return jobs


def main():
    start = perf_counter()
    print(f'Using {len(aux.getStopwords())} Stopwords: {aux.getStopwords()}')
    jobs = get_jobs()
    print(f'Length of jobs: {len(jobs)}')
    for n, job in enumerate(jobs):
        url = job[0]
        descr = aux.treat_text(job[1])
        print(f'\n⏳Updating job #{n+1}/{len(jobs)}:\n{descr}')
        update(url, descr)
    end = perf_counter()
    print(f'\n⏱️ Finished in {round(end - start, 2)} seconds\n\n')


if __name__ == '__main__':
    main()
