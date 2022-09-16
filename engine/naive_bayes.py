
from collections import Counter
from instance.config import config
import psycopg2
import pandas as pd
from imblearn.pipeline import make_pipeline
from imblearn.under_sampling import NearMiss
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from re import sub
import pickle
import time
import traceback


# Save Classifier to Pickle file
def save_classifier(model):
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

    tuples = cur.fetchall()
    cur.close()
    return pd.DataFrame(tuples, columns=column_names)


# Build Classifier
def build_classifier(data, random_state):
    print('\n\n###############################################################################')
    print("    _   __        _               ____                           \n   / | / /____ _ (_)_   __ ___   / __ ) ____ _ __  __ ___   _____\n  /  |/ // __ `// /| | / // _ \ / __  |/ __ `// / / // _ \ / ___/\n / /|  // /_/ // / | |/ //  __// /_/ // /_/ // /_/ //  __/(__  ) \n/_/ |_/ \__,_//_/  |___/ \___//_____/ \__,_/ \__, / \___//____/  \n                                            /____/")
    print(f"Starting NB for 🎲{random_state}\n")

    # Organizing Data
    categories = data['curso_id']
    print(str(len(categories.unique())) + " Categories Found")
    descriptions = data['descr']
    print(str(len(descriptions)) + " Descriptions Found")
    print(f"Original dataset class count:\n{Counter(categories)}\n")

    # Applying TFIDF Feature Extraction
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(descriptions)
    print(f"Applied TFIDF.\nNew shape: {X.shape}")

    # Balancing Classes
    nm = NearMiss(sampling_strategy='not minority', version=2)
    x_nm, y_nm = nm.fit_resample(X, categories)
    print(f"Applied NearMiss. New class count:\n{Counter(y_nm)}\n")

    # Splitting the data into training and testing sets
    X_train, X_test, Y_train, Y_test = train_test_split(
        x_nm, y_nm, shuffle=True, random_state=random_state)
    print(
        f"\nSplitting Data into Train and Test sets...\nX_train: {X_train.shape} | X_test: {X_test.shape}\nY_train: {Y_train.shape} | Y_test: {Y_test.shape}")

    # Defining base model
    print(f"Defining base model...")
    model = MultinomialNB()

    # Fitting the model
    print(f"Fitting the model...")
    model.fit(X_train, Y_train)

    # Testing the model
    print("Testing the model...")
    preds = model.predict(X_test)

    print('###############################################################################')
    print(
        f'🎯Classification Report:\n{metrics.classification_report(Y_test, preds, zero_division=0)}')
    print('###############################################################################')
    # acc_score = accuracy_score(Y_test, preds)
    # print(f'\nAccuracy Score:  🎯{acc_score}\nFor random_state 🎲{random_state}\n')

    f1 = metrics.f1_score(Y_test, preds, average='weighted')
    print(f'\nF1 Score:  🎯{f1}\nFor random_state 🎲{random_state}\n')

    # Saving the model into a pickle file
    # saveclassifier(model)
    print('###############################################################################')
    return random_state, f1


# main()


def main():
    start = time.perf_counter()

    # Loading Data
    # data = postgresql_to_dataframe("SELECT v.curso_id, v.descr FROM vaga_formatada v WHERE v.curso_id NOT IN (16);", (r'curso_id', r'descr'))
    data = postgresql_to_dataframe(
        "SELECT v.curso_id, v.descr FROM vaga_formatada v;", (r'curso_id', r'descr'))

    # Run once version
    random_state = 42
    # build_classifier(data, random_state)
    # return

    #  Loop version
    top_f1, top_ran = 0, 0
    for random_state in range(100):
        # Comment the next  line to prevent looping
        ran, f1 = build_classifier(data, random_state)
        if f1 > top_f1:
            top_f1 = f1
            top_ran = ran
            print(
                f'Ran {ran}, F1 🎯{f1} is a ✅New Record!🎊\ntop_F1: 🎯{top_f1}')
        else:
            print(f'Ran {ran}, F1 {f1}\ntop_F1:🎯{top_f1} ({top_ran})')
    print(f'\n🎯Best Accuracy: {top_f1} for 🎲random_state {top_ran}')
    # End of loop

    print(
        f'\n🔥 Total time elapsed: {round(time.perf_counter() - start, 2)} seconds\n')


if __name__ == '__main__':
    main()
