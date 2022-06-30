SELECT c.curso_titulo, v.geral_titulo FROM vaga_geral v INNER JOIN curso c ON v.curso_id = c.curso_id
SELECT c.curso_titulo, v.formatada_titulo ,v.formatada_desc FROM vaga_formatada v INNER JOIN curso c ON v.curso_id = c.curso_id ORDER BY c.curso_id
SELECT count(c.curso_id), c.curso_id, c.curso_titulo FROM vaga_geral v JOIN curso c ON v.curso_id = c.curso_id GROUP BY c.curso_id ORDER BY count(c.curso_id) DESC
SELECT count(c.curso_id), c.curso_id, c.curso_titulo FROM vaga_formatada v JOIN curso c ON v.curso_id = c.curso_id GROUP BY c.curso_id ORDER BY count(c.curso_id) DESC
SELECT * FROM vaga_formatada
SELECT * FROM vaga_formatada ORDER BY curso_id ASC
SELECT * FROM vaga_geral 
SELECT * FROM vaga_geral ORDER BY curso_id ASC
SELECT curso_id, geral_titulo, geral_desc FROM vaga_geral ORDER BY curso_id
SELECT v.curso_id, c.curso_titulo ,v.geral_titulo, v.geral_desc FROM vaga_geral v INNER JOIN curso c ON v.curso_id = c.curso_id ORDER BY curso_id
SELECT curso_id, formatada_titulo FROM vaga_formatada ORDER BY curso_id
SELECT curso_id, formatada_titulo FROM vaga_formatada ORDER BY curso_id
SELECT * FROM curso
UPDATE vaga_geral SET curso_id = 1

TRUNCATE TABLE vaga_formatada
TRUNCATE TABLE vaga_geral
