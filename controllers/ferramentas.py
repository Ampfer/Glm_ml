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
                estoque=row.estoque if row.estoque>0 else 0,
                marca = row.marca if row.marca else marca,
                ean = row.ean if row.ean else ean,
                )

def atualizar_estoque():

	anuncios = db(Anuncios.id > 0).select()
	for anuncio in anuncios:
		estoque =  sugerido(int(anuncio.id))['estoque']
		Anuncios[anuncio.id] = dict(estoque=estoque)

	form = FORM.confirm('Atualizar Estoque',{'Voltar':URL('default','index')})

	if form.accepted:
		if session.ACCESS_TOKEN:
			from meli import Meli 
			meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

			anuncios = db(Anuncios.id > 0).select()
			for anuncio in anuncios:
				if anuncio['item_id']:
					body = dict(available_quantity=float(anuncio['estoque']))
					item_args = "items/%s" %(anuncio['item_id'])	
					item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
					if item.status_code != 200:
						print '%s - %s - %s' %(anuncio['item_id'],anuncio['id'] ,item)

			response.flash = 'Estoque Atualizado com Sucesso....'

		else:
			status = 'Antes Faça o Login....'

	return dict(form=form)




