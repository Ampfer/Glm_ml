# -*- coding: utf-8 -*-

import csv

def importar_vinculo():

	form = SQLFORM.factory(Field('csvfile','upload',uploadfield=False,label='Arquivo Vínculos de Produto:',requires=notempty)
		,submit_button='Importar Vínculos')

	if form.process().accepted:
		if request.vars.csvfile != None:
			file =  request.vars.csvfile.file
			head = False
			for linha in file:
				if head:
					a,b,c,d,e,f,g,h,i = linha.split(';')

					id_bling = a.replace('"','')
					id_loja = b.replace('"','')
					id_produto = d.replace('"','')
					loja = i.replace('"','')
					preco = float(e.replace('"','').replace(',','.'))
					preco_promocional = float(f.replace('"','').replace(',','.'))

					query = (Vinculos.id_bling == id_bling) & (Vinculos.id_loja == id_loja ) & (Vinculos.id_produto == id_produto) & (Vinculos.loja == loja)

					Vinculos.update_or_insert(query,
						id_bling = id_bling,
						id_loja = id_loja,
						id_produto = id_produto,
						loja = loja,
						preco = preco,
						preco_promocional = preco_promocional
					)
				head = True

	return dict(form=form)
