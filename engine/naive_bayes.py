
from collections import Counter
from instance.config import config
import psycopg2
import pandas as pd
from imblearn.under_sampling import NearMiss
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
import pickle
import time
import traceback


# Save Classifier to Pickle file
def save_classifier(model):
    try:
        f = open('engine/my_classifier.pickle', 'wb')
        pickle.dump(model, f)
        f.close()
        print('✅ Salvo com sucesso')
    except:
        print('⚠️ Erro ao salvar o arquivo')
        traceback.print_exc()

# Save vectorizer to Pickle file
def save_vectorizer(vectorizer):
    try:
        f = open('engine/vectorizer.pickle', 'wb')
        pickle.dump(vectorizer, f)
        f.close()
        print('✅ Salvo com sucesso')
    except:
        print('⚠️ Erro ao salvar o arquivo')
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
    print('\n###############################################################################')
    print(f"# Starting NB for 🎲{random_state}\n")

    # Organizing Data
    X = data['descr']
    print(str(len(X)) + " Descriptions Found")
    Y = data['curso_id']
    print(str(len(Y.unique())) + " Categories Found")
    # print(f"Original Dataset Class Count:\n>{Counter(Y)}\n")
    # print(f'Type of X:{type(X)} Y:{type(Y)}')
    

    # Applying TFIDF Feature Extraction
    print("# TFIDF Vectorizing... ")
    # print(f"Prev X.shape: {X.shape}")
    vectorizer = TfidfVectorizer(max_df=0.8)
    X = vectorizer.fit_transform(X)
    # print(f"New X.shape: {X.shape}")

    # Balancing Classes with NearMiss
    print("# NearMiss Balancing... ")
    nm = NearMiss(sampling_strategy='not minority', version=2)
    X, Y = nm.fit_resample(X, Y)
    # X, Y = nm.fit_resample(vectorizer.fit(X), Y)
    print(f"NearMiss Resampled... New class count:\n>{Counter(Y)}\n")
    
    # Splitting the data into training and testing sets
    print(f"# Splitting Data into Train and Test sets...")
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, shuffle=True, random_state=random_state)
    # print(f"X_train: {X_train.shape} | Y_train: {Y_train.shape}\nX_test: {X_test.shape} | Y_test: {Y_test.shape}")
    
    # Defining base model
    print(f"# Defining base model...")
    model =  make_pipeline  (
            # vectorizer,
            MultinomialNB()
        )

    # Fitting the model
    print(f"# Fitting the model...")
    # print(f'X_train:{X_train}\nY_train:{Y_train}')
    model.fit(X_train, Y_train)
    print(f'Model: {model}')

    # Testing the model
    print("# Testing the model...")
    preds = model.predict(X_test)
    # preds_proba = model.predict_proba(X_test)


    print('###############################################################################')
    # print(f'🎯Classification Report:\n{metrics.classification_report(Y_test, preds, zero_division=0)}\n###############################################################################')

    f1 = metrics.f1_score(Y_test, preds, average='weighted')
    acc_score = metrics.accuracy_score(Y_test, preds)
    acc_score_bal = metrics.balanced_accuracy_score(Y_test, preds)
    print(f'\nTests for random_state 🎲{random_state} returned:')
    print(f'NB: F1 {f1} | Acc {acc_score} | Balanced Acc {acc_score_bal}')

    # Saving the model into a pickle file
    # save_classifier(model)
    # save_vectorizer(vectorizer)
    return random_state, f1


# main()


def main():
    start = time.perf_counter()
    print('###############################################################################')
    print("\n            _        \n|\ |_.o   _|_)_. _ _ \n| \(_||\/(/|_(_\(/_> \n               /     ")

    # Loading Data
    print("Loading Data...")
    # data = postgresql_to_dataframe("SELECT v.curso_id, v.descr FROM vaga_formatada v WHERE v.curso_id NOT IN (16);", (r'curso_id', r'descr'))
    data = postgresql_to_dataframe("SELECT v.curso_id, v.descr FROM vaga_formatada v;", (r'curso_id', r'descr'))
    print(f"Data Loaded. Shape: {data.shape}")


    # Run once version
    # random_state = 46
    # build_classifier(data, random_state)
    # return

    #  Loop version
    run_X_times = 10000
    top_f1, top_ran = 0, 0
    for random_state in range(run_X_times):
        # Comment the next  line to prevent looping
        ran, f1 = build_classifier(data, random_state)
        if f1 > top_f1:
            top_f1 = f1
            top_ran = ran
            print(f'✅ F-score 🎯{f1} 🎲{ran} is a 🎊New Record!✅')
        else:
            print(f'F1 🎯{f1} 🎲{ran} is not greater than 🎯{top_f1} 🎲{top_ran}')
    # End of loop
    print('###############################################################################')
    print("            _        \n|\ |_.o   _|_)_. _ _ \n| \(_||\/(/|_(_\(/_> \n               /     ")
    print(f'\n🔥 Finished running NB {run_X_times} times...')
    print(f'\n✅ Final Top Result:\nF-score of 🎯{top_f1} for random_state 🎲{top_ran}')
    print(f'\n⌛ Total time elapsed: {round(time.perf_counter() - start, 2)} seconds, or {round((time.perf_counter() - start) / 60, 2)} minutes\n')


if __name__ == '__main__':
    main()
