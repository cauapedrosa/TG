# from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
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
    status = 0
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(
            """UPDATE vaga_geral SET curso_id = %s WHERE url = %s""", (previsao, url))
        # print(f'>{cur.rowcount} rows updated')
        if cur.rowcount > 0:
            status = 1
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f'⚠️ ERROR: {error}')
        return status
    finally:
        if conn is not None:
            conn.close()
            print(f'✅table_update Successful! {status} row(s) affected.')
        return status


def main():
    n_updated_jobs = 0 # Tracker for number of updated jobs

    # Load jobs from Database into a Pandas.Dataframe
    data_geral = postgresql_to_dataframe(
        "SELECT url, descr FROM vaga_geral WHERE curso_id = 1;", (r'url', r'descr'))
    print(f'######################################\n{len(data_geral)} jobs loaded with shape {data_geral.shape}')

    if len(data_geral) < 1:
        print('❌ No jobs to classify')
        return 0

    # Load TF-IDF Vectorizer from pickle file
    f = open('engine/vectorizer.pickle', 'rb')
    vectorizer = pickle.load(f)
    f.close()
    print(f'✅ Loaded vectorizer: {vectorizer} with a vocabulary of {len(vectorizer.vocabulary_)} words')

    # Load Multinomial Naive Bayes classifier from pickle file
    f = open('engine/my_classifier.pickle', 'rb')
    classifier = pickle.load(f)
    f.close()
    print(f'✅ Loaded classifier: {classifier} with {len(classifier.classes_)} classes')

    # Apply TF-IDF to loaded descriptions
    descrs_tfidf = vectorizer.transform(data_geral['descr'])

    # Perform prediction for all jobs in array
    previsoes = classifier.predict(descrs_tfidf)

    # Store predictions into Data Frame
    data_geral['curso_id'] = previsoes

    # Update Database 
    for index, row in data_geral.iterrows():
        id = row['curso_id']
        url = row['url']
        print(f'\n⏱️ #{index+1}/{len(data_geral)} | Predicting >{id}< for:\n{url}')
        n_updated_jobs += table_update(row['url'], row['curso_id'])
        print(f'\n⚙️ #{n_updated_jobs}/{len(data_geral)} jobs updated...')

    return n_updated_jobs


if __name__ == '__main__':
    start = time.perf_counter()
    n=main()
    print(f'🔥 Classified {n} jobs in {round(time.perf_counter() - start, 2)} seconds')
