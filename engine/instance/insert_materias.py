import psycopg2
from config import config


def insert_cursos(cursos):
    sql = "INSERT INTO curso(curso_titulo) VALUES(%s)"
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.executemany(sql, cursos)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    insert_cursos([
        ('Indefinido',),
        ('Agroindústria',),
        ('Agronegócio',),
        ('Alimentos',),
        ('Análise de Processos Agroindustriais',),
        ('Análise e Desenvolvimento de Sistemas',),
        ('Automação e Manufatura Digital',),
        ('Automação Industrial',),
        ('Banco de Dados',),
        ('Big Data no Agronegócio',),
        ('Big Data para Negócios',),
        ('Biocombustíveis',),
        ('Ciência de Dados',),
        ('Comércio Exterior',),
        ('Construção Civil - Edifícios',),
        ('Construção de Edifícios',),
        ('Construção Naval',),
        ('Controle de Obras',),
        ('Cosméticos',),
        ('Desenvolvimento de Produtos Plásticos',),
        ('Desenvolvimento de Software Multiplataforma',),
        ('Design de Mídias Digitais',),
        ('Design de Produto',),
        ('Eletrônica Automotiva',),
        ('Eletrônica Industrial',),
        ('Estradas',),
        ('Eventos',),
        ('Fabricação Mecânica',),
        ('Geoprocessamento',),
        ('Gestão Ambiental',),
        ('Gestão Comercial',),
        ('Gestão da Produção Industrial',),
        ('Gestão da Qualidade',),
        ('Gestão da Tecnologia da Informação',),
        ('Gestão de Energia e Eficiência Energética',),
        ('Gestão de Negócios e Inovação',),
        ('Gestão de Recursos Humanos',),
        ('Gestão de Serviços',),
        ('Gestão de Turismo',),
        ('Gestão Empresarial',),
        ('Gestão Financeira',),
        ('Gestão Hospitalar',),
        ('Gestão Portuária',),
        ('Hidráulica e Saneamento Ambiental',),
        ('Informática para Negócios',),
        ('Instalações Elétricas',),
        ('Jogos Digitais',),
        ('Logística',),
        ('Logística Aeroportuária',),
        ('Manufatura Avançada',),
        ('Manutenção de Aeronaves',),
        ('Manutenção Industrial',),
        ('Marketing',),
        ('Materiais',),
        ('Mecânica - Modalidade Projetos',),
        ('Mecânica - Processos de Produção',),
        ('Mecânica Automobilística',),
        ('Mecânica de Precisão',),
        ('Mecânica: Processos de Soldagem',),
        ('Mecanização em Agricultura de Precisão',),
        ('Mecatrônica Industrial',),
        ('Meio Ambiente e Recursos Hídricos',),
        ('Microeletrônica',),
        ('Polímeros',),
        ('Processos Metalúrgicos',),
        ('Processos Químicos',),
        ('Produção Agropecuária',),
        ('Produção Fonográfica',),
        ('Produção Industrial',),
        ('Produção Têxtil',),
        ('Projetos de Estruturas Aeronáuticas',),
        ('Projetos Mecânicos',),
        ('Radiologia',),
        ('Redes de computadores',),
        ('Refrigeração, Ventilação e Ar Condicionado',),
        ('Secretariado',),
        ('Secretariado e Assessoria Internacional',),
        ('Segurança da Informação',),
        ('Silvicultura',),
        ('Sistemas Biomédicos',),
        ('Sistemas Embarcados',),
        ('Sistemas Navais',),
        ('Sistemas para Internet',),
        ('Soldagem',),
        ('Têxtil e Moda',),
        ('Transporte Terrestre',)
    ])
