from naive_bayes import postgresql_to_dataframe
import pickle
import psycopg2
from instance.config import config


def de_para_previsao(previsao):
    return {
        'Indefinido': 1,
        'Agroindústria': 2,
        'Agronegócio': 3,
        'Alimentos': 4,
        'Análise de Processos Agroindustriais': 5,
        'Análise e Desenvolvimento de Sistemas': 6,
        'Automação e Manufatura Digital': 7,
        'Automação Industrial': 8,
        'Banco de Dados': 9,
        'Big Data no Agronegócio': 10,
        'Big Data para Negócios': 11,
        'Biocombustíveis': 12,
        'Ciência de Dados': 13,
        'Comércio Exterior': 14,
        'Construção Civil - Edifícios': 15,
        'Construção de Edifícios': 16,
        'Construção Naval': 17,
        'Controle de Obras': 18,
        'Cosméticos': 19,
        'Desenvolvimento de Produtos Plásticos': 20,
        'Desenvolvimento de Software Multiplataforma': 21,
        'Design de Mídias Digitais': 22,
        'Design de Produto': 23,
        'Eletrônica Automotiva': 24,
        'Eletrônica Industrial': 25,
        'Estradas': 26,
        'Eventos': 27,
        'Fabricação Mecânica': 28,
        'Geoprocessamento': 29,
        'Gestão Ambiental': 30,
        'Gestão Comercial': 31,
        'Gestão da Produção Industrial': 32,
        'Gestão da Qualidade': 33,
        'Gestão da Tecnologia da Informação': 34,
        'Gestão de Energia e Eficiência Energética': 35,
        'Gestão de Negócios e Inovação': 36,
        'Gestão de Recursos Humanos': 37,
        'Gestão de Serviços': 38,
        'Gestão de Turismo': 39,
        'Gestão Empresarial': 39,
        'Gestão Financeira': 40,
        'Gestão Hospitalar': 41,
        'Gestão Portuária': 42,
        'Hidráulica e Saneamento Ambiental': 43,
        'Informática para Negócios': 44,
        'Instalações Elétricas': 45,
        'Jogos Digitais': 46,
        'Logística': 47,
        'Logística Aeroportuária': 48,
        'Manufatura Avançada': 49,
        'Manutenção de Aeronaves': 50,
        'Manutenção Industrial': 51,
        'Marketing': 52,
        'Materiais': 53,
        'Mecânica - Modalidade Projetos': 54,
        'Mecânica - Processos de Produção': 55,
        'Mecânica Automobilística': 56,
        'Mecânica de Precisão': 57,
        'Mecânica: Processos de Soldagem': 58,
        'Mecanização em Agricultura de Precisão': 59,
        'Mecatrônica Industrial': 60,
        'Meio Ambiente e Recursos Hídricos': 61,
        'Microeletrônica': 62,
        'Polímeros': 63,
        'Processos Metalúrgicos': 64,
        'Processos Químicos': 65,
        'Produção Agropecuária': 66,
        'Produção Fonográfica': 67,
        'Produção Industrial': 68,
        'Produção Têxtil': 69,
        'Projetos de Estruturas Aeronáuticas': 70,
        'Projetos Mecânicos': 71,
        'Radiologia': 72,
        'Redes de Computadores': 73,
        'Refrigeração, Ventilação e Ar Condicionado': 74,
        'Secretariado': 75,
        'Secretariado e Assessoria Internacional': 76,
        'Segurança da Informação': 77,
        'Silvicultura': 78,
        'Sistemas Biomédicos': 79,
        'Sistemas Embarcados': 80,
        'Sistemas Navais': 81,
        'Sistemas para Internet': 82,
        'Soldagem': 83,
        'Têxtil e Moda': 84,
        'Transporte Terrestre': 85
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

    print(type(data_geral))
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
        print(f'#{index+1}/{len(data_geral)} | Predicting {previsao}')


if __name__ == '__main__':
    main()
