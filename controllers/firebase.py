# -*- coding: utf-8 -*-

def atualiza_produto_firebase():
	produtos = Produtos()
	fields = "codpro, nompro, codbar, pesbru, locpro"
	query = "codgru = 1 and tabela = 'S' and codpro < 100"
	results = produtos.select(fields,query).fetchall()
	print results
	for row in results:
		produto = dict(
			codpro = row[0],
			nompro = row[1],
			codbar = row[2],
			pesbru = row[3],
			locpro = row[4] 
			)
		produto_firebase_set(produto)


