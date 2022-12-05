import csv
import psycopg2
from config import config

def save_to_csv(list, counter):
    if counter == 0:
        table = 'vaga_formatada'
    if counter == 1:
        table = 'vaga_geral'
    
    with open(f'./db/reports/{table}.csv', 'a', newline='',  encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(list)
    return

def main():
    print('Saving jobs from Database to local .csv file...')

    commands = (
        """SELECT * FROM vaga_formatada""",
        """SELECT * FROM vaga_geral""")
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
            aux = cur.fetchall()
            print(f'Result: {len(aux)} rows')
            save_to_csv(aux, counter)            
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    main()
