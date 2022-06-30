DROP TABLE IF EXISTS vaga_formatada CASCADE;
	CREATE TABLE vaga_formatada (
		URL_formatada varchar NOT NULL PRIMARY KEY,
		format_id int NOT NULL,
		format_desc varchar NOT NULL,
		format_titulo varchar NOT NULL,
		materia_id int NOT NULL
	);
	

COPY vaga_formatada(URL_formatada, format_id, format_desc, format_titulo, materia_id)
FROM 'C:\Users\xarys\Documents\GitHub\TG\fatec_tg\linkedin_formated_data.csv'
DELIMITER ','
CSV HEADER;