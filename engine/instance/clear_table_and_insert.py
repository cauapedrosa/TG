from datetime import date
import psycopg2
import traceback
import csv
from config import config
import sys
sys.path.append('C:/Users/xarys/Documents/GitHub/TG/engine')
from Job import Job

# url,curso_id,titulo,descr,empresa,postdate,locale


def clear_table_and_insert(new_data):
    conn = None

    try:
        print(f'Length of new_data: {len(new_data)}')
        # print(f'New_data: {new_data}')
        jobList = []
        for job in new_data:
            j = Job(job[0], job[1], job[2], job[3],
                    job[4], date.today(), job[6])
            # print(f'Job: {j}')
            jobList.append(j)
        print(f'👍jobList has {len(jobList)} elements')
    except Exception as error:
        print(f'⚠️ Error: {error}')
        traceback.print_exc()

    try:
        row_counter = 0
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE vaga_formatada")
        print(f'Row Count: {cur.rowcount}\n')
        print("Table Truncated")
        for count, job in enumerate(jobList):
            print(f"> Inserting vaga {count+1}/{len(jobList)}: {job}")
            cur.execute("""INSERT INTO vaga_formatada (URL, curso_id, titulo, descr, empresa, postDate, locale) VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                        (job.url, job.course_id, job.title, job.desc, job.poster, job.date, job.locale))
            row_counter += cur.rowcount
        print(f'👍Inserted {row_counter} rows')
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    new_data = []
    # with open('db/reports/formattedjobs.csv', encoding="utf8") as csvfile:
    #     reader = csv.reader(csvfile)
    #     for row in reader:
    #         new_data.append(row)
    clear_table_and_insert(new_data)
