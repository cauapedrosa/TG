import time
from instance.config import config
from naive_bayes import postgresql_to_dataframe
import pickle
import psycopg2


def de_para_previsao(previsao):
    return {
        'Indefinido': 1,
        'Análise e Desenvolvimento de Sistemas': 2,
        'Comércio Exterior': 3,
        'Eletrônica Automotiva': 4,
        'Fabricação Mecânica': 5,
        'Gestão da Qualidade': 6,
        'Gestão de Serviços': 7,
        'Gestão Empresarial': 8,
        'Logística': 9,
        'Logística Aeroportuária': 10,
        'Manufatura Avançada': 11,
        'Polímeros': 12,
        'Processos Metalúrgicos': 13,
        'Projetos Mecânicos': 14,
        'Redes de Computadores': 15,
        'Sistemas Biomédicos': 16,
    }[previsao]

# update table vagas_geral


def table_update(url, previsao):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            """UPDATE vaga_geral SET curso_id = %s WHERE url = %s""", (previsao, url))
        print(f'>{cur.rowcount} rows updated')
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f'ERROR: {error}')
        # cur.close()
    finally:
        if conn is not None:
            conn.close()


def main():
    # load data
    data_geral = postgresql_to_dataframe(
        "SELECT url, descr FROM vaga_geral WHERE curso_id = 1;", (r'url', r'descr'))

    print(f'{data_geral} vagas carregadas')

    # Open pickle file
    f = open('engine\my_classifier.pickle', 'rb')
    classifier = pickle.load(f)
    f.close()
    print(f'Loaded classifier: {classifier}')
    for index, row in data_geral.iterrows():
        text = row['descr']
        previsao = classifier.predict([text])
        previsao = str(previsao).replace(
            "'", "").replace("[", "").replace("]", "")
        table_update(row['url'], de_para_previsao(previsao))
        print(
            f'\n⏱️ #{index+1}/{len(data_geral)} | Predicting >{previsao.upper()}< for:\n{text}')


if __name__ == '__main__':
    start = time.perf_counter()
    main()
    print(
        f'🔥 Total time elapsed: {round(time.perf_counter() - start, 2)} seconds')
