# -*- coding: utf-8 -*-
def importar_produtos():

	form = SQLFORM.factory(Field('csvfile','upload',uploadfield=False,label='Arquivo csv:',requires=notempty)
		,submit_button='Carregar Produtos')

	gridProdutos = file = ''

	#form = FORM(INPUT(_type='file',_name='csvfile'),INPUT(_type='submit',_value='Upload'))
	Importar_Produtos.truncate()
	
	if form.process().accepted:
		if request.vars.csvfile != None:
			try:
				Importar_Produtos.import_from_csv_file(request.vars.csvfile.file, delimiter=";")
				gridProdutos = grid(Importar_Produtos,formname="importarprodutos",create=False, editable=False,
					searchable=False,orderby = Importar_Produtos.nome)
				
				btnAtualizar = atualizar('atualiza_produtos',' Atualizar Produtos', 'importarprodutos')
				gridProdutos[0].insert(-1, btnAtualizar)
				btnAtualizar["_onclick"] = "return confirm('Confirma a Atualização dos Produtos?');"
				if btnAtualizar:
					atualiza_produtos()
					response.js = "teste();"

				file = 'Arquivo Carregado: %s' %(request.vars.csvfile.filename)
			except:
				response.flash = 'Arquivo Inválido'

	elif form.errors:
		response.flash = 'Erro no Formulário'

	return dict(form=form,gridProdutos=gridProdutos,file=file)

def atualiza_produtos():
	rows = db(Importar_Produtos.id > 0).select()
	for row in rows:
		try:
			produto = Produtos[int(row.codigo)]
			nome = produto.nome 
			preco = produto.preco
			marca = produto.marca
			ean = produto.ean
		except:
			nome = marca = ean = ''
			preco  = 0

		Produtos.update_or_insert(Produtos.id == row.codigo,
                id = row.codigo,
                nome=row.nome if row.nome else nome,
                preco = row.preco if row.preco else preco,
                estoque=row.estoque if row.estoque else 0,
                marca = row.marca if row.marca else marca,
                ean = row.ean if row.ean else ean,
                )

def atualizar_anuncios():
	gridAnuncios = grid(Anuncios)
	pass
	



