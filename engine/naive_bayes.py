from instance.config import config
import psycopg2
import pandas as pd
from sklearn import datasets
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, cross_validate, cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix
from re import sub
import pickle
import time
import traceback

random_state =6
# save classifiers


def saveclassifier(model):
    try:
        f = open('engine\my_classifier.pickle', 'wb')
        pickle.dump(model, f)
        f.close()
        print('Salvo com sucesso')
    except:
        print('⚠️Erro ao salvar o arquivo')
        traceback.print_exc()

# Transform a SELECT query into a pandas dataframe


def postgresql_to_dataframe(select_query, column_names):
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cur.close()
        return 1

    tupples = cur.fetchall()
    cur.close()
    return pd.DataFrame(tupples, columns=column_names)


# main()

def main():
    # Loading Data
    data = postgresql_to_dataframe(
        "SELECT c.curso_titulo, v.descr FROM vaga_formatada v INNER JOIN curso c ON c.curso_id = v.curso_id;", (r'curso_id', r'descr'))

    # Organizing Data
    categories = data['curso_id'].unique()
    print(str(len(categories)) + " Categories Found")
    descriptions = data['descr']
    print(str(len(descriptions)) + " Descriptions Found")

    # Splitting the data into training and testing sets
    train, test, train_labels, test_labels = train_test_split(
        descriptions, data['curso_id'], shuffle=True, random_state=random_state)
    print(f'\n#### Train:\n{train}')
    print(f'\n### Test:\n{test}')

    # Defining base model
    print("\nDefining base model...")
    model = make_pipeline(TfidfVectorizer(), MultinomialNB(), verbose=True)
    # Fitting the model
    print(f"\nFitting the model: {model}")
    model.fit(train, train_labels)

    # Testing the model
    print("\nTesting the model...")
    # scores = cross_val_score(model, data_formatted, data_formatted['descr'])
    # scores = model.predict_proba(test)[:, 1]

    preds = model.predict(test)
    # # print(f'Scores: {scores}')
    # print(f'Scores mean: {scores.mean()}')
    # # print(f'Scores var: {scores.var()}')
    print('###############################################################################')
    print(
        f'🎯Classification Report:\n{classification_report(test_labels, preds, zero_division=0)}')
    print('###############################################################################')
    print(
        f'\n🎯Accuracy Score: {accuracy_score(test_labels, preds)}\n@ Random State #{random_state}')
    # Saving the model into a pickle file
    saveclassifier(model)


if __name__ == '__main__':
    start = time.perf_counter()
    main()
    print(
        f'\n🔥 Total time elapsed: {round(time.perf_counter() - start, 2)} seconds\n')
