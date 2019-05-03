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
		estoque =  sugerido(anuncio)['estoque']
		Anuncios[anuncio.id] = dict(estoque=estoque)

	form = FORM.confirm('Atualizar Estoque',{'Voltar':URL('default','index')})

	if form.accepted:

		if session.ACCESS_TOKEN:
			from meli import Meli 
			meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

			anuncios = db(Anuncios.id > 0).select()
			#anuncios = db(Anuncios.forma == 'Multiplos').select()
			for anuncio in anuncios:
				if anuncio['item_id']:
					variacao = []
					if anuncio['forma'] == 'Multiplos':
						body = dict(variations=buscar_variacao_estoque(anuncio['id']))
					else:
						body = dict(available_quantity=float(anuncio['estoque']))
					item_args = "items/%s" %(anuncio['item_id'])	
					item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
					if item.status_code != 200:
						print '%s - %s - %s' %(anuncio['item_id'],anuncio['id'] ,item)

			response.flash = 'Estoque Atualizado com Sucesso....'

		else:
			status = 'Antes Faça o Login....'

	return dict(form=form)

def atualizar_sugerido():
	anuncios = db(Anuncios.id > 0).select()
	for anuncio in anuncios:
		anuncioId = int(anuncio.id)
		Anuncios[anuncioId] = dict(preco=sugerido(anuncio)['preco'])
	#response.js = "$('#teste').get(0).reload()"
	response.js = "location.reload(true)"

def alterar_desconto():
	id = int(request.post_vars.id)
	valor = request.post_vars.valor
	Anuncios[id] = dict(desconto = valor)

def alterar_preco():
	id = int(request.post_vars.id)
	valor = request.post_vars.valor
	anuncio = Anuncios[id]
	desconto = anuncio.desconto
	ep = sugerido(anuncio)['preco']
	desc = round((1-(float(valor)*(1-float(desconto/100)))/float(ep))*100,2)
	Anuncios[id] = dict(preco = valor,desconto = desc)

def sincronizar_preco():
	if session.ACCESS_TOKEN:
		from meli import Meli 
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
		anuncios = db(Anuncios.status == 'active').select()
		#anuncios = db(Anuncios.id == 841).select()
		#anuncios = db(Anuncios.forma == 'Multiplos').select()
		for anuncio in anuncios:		
			if anuncio['item_id']:
				if anuncio['forma'] == 'Multiplos':
					body = dict(variations=buscar_variacao_preco(anuncio['id'],anuncio['preco']))
				else:
					body = dict(price=float(anuncio['preco']))
				item_args = "items/%s" %(anuncio['item_id'])	
				item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
				if item.status_code != 200:
					print '%s - %s - %s' %(anuncio['item_id'],anuncio['id'] ,item)

		session.flash = 'Preços Atualizado com Sucesso'
	else:
		session.flash = 'Antes Faça o Login....'
	response.js = "location.reload(true)"
	return

def atualizar_preco():
	Anuncios.sugerido = Field.Virtual('sugerido',lambda row: sugerido(row.anuncios)['preco'], label='Sugerido')
	fields = (Anuncios.id,Anuncios.titulo,Anuncios.categoria,Anuncios.tipo,Anuncios.forma,Anuncios.frete,Anuncios.fretegratis,Anuncios.desconto,Anuncios.preco,Anuncios.sugerido)

	formPrecos = grid(Anuncios,60,paginate=200,formname="formPrecos",fields=fields,orderby=Anuncios.titulo, deletable=False)
	
	btnSugerido = A(SPAN(_class="glyphicon glyphicon-cog"), ' Atualizar Sugerido ', _class="btn btn-default",_id='atualizarsugerido', _onclick="if (confirm('Deseja Atualizar Preços com Sugeridos ?')) ajax('%s',[], 'formPrecos');" %URL('atualizar_sugerido',args=request.vars.keywords))
	btnPreco = A(SPAN(_class="glyphicon glyphicon-cog"), ' Atualizar Preços ', _class="btn btn-default",_id='sincronizarpreco', _onclick="if (confirm('Deseja Atualizar Preços do Mercado Livre ?')) ajax('%s', [], 'formPrecosMl');" %URL('sincronizar_preco'))

	formPrecos[0].insert(-1, btnSugerido)
	formPrecos[0].insert(-1, btnPreco)

	formPrecos = DIV(formPrecos, _class="well")

	if request.args(-3) == 'edit':
		idAnuncio = request.args(-1)
		redirect(URL('anuncio','anuncio', args=idAnuncio,))

	return dict(formPrecos=formPrecos)

def buscar_variacao_preco(idAnuncio,preco):
    variacao = []
    rows = db(Anuncios_Produtos.anuncio==idAnuncio).select()
    for row in rows:
        variacaoProduto = dict(id=row.variacao_id,
                               price=float(preco),
                               )
        variacao.append(variacaoProduto)
    return variacao

def buscar_variacao_estoque(idAnuncio):
    variacao = [] 
    rows = db(Anuncios_Produtos.anuncio==idAnuncio).select()
    for row in rows:
        produto = Produtos[row.produto]
        variacaoProduto = dict(id=row.variacao_id,
                               available_quantity=float(produto.estoque),
                               )
        variacao.append(variacaoProduto)
    return variacao


def ean():
    rows = db(Anuncios.id>0).select()
    for row in rows:
        if row.forma == 'Individual':
            idProduto = db(Anuncios_Produtos.anuncio==row.id).select().first()['produto']
            ean = db(Produtos.id==idProduto).select().first()['ean']
            if ean:
            	query = (Anuncios_Atributos.anuncio == row.id) & (Anuncios_Atributos.atributo == 3)
            	Anuncios_Atributos.update_or_insert(query,anuncio=row.id, atributo = 3, valor= ean)

def atualizar_ean():
	rows = db(Anuncios.id>0).select()
	for row in rows:
		atributos = []
		buscaAtributos = db(Anuncios_Atributos.anuncio == row.id).select()
		for atributo in buscaAtributos:
			atributo_id = Atributos(atributo.atributo).atributo_id
			atributos.append(dict(id=atributo_id, value_name=atributo.valor))
		if atributos:
			body = dict(attributes=atributos)
			item_id = Anuncios[int(row.id)].item_id
			item_args = "items/%s" %(item_id)

			if session.ACCESS_TOKEN:
				from meli import Meli    
				meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

				item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})

				if item.status_code != 200:
					status = 'Falha na Atualização do Item : item:%s Descrição:%s Tipo:%s' %(item,desc,tipo)
				else:
					status = 'Anuncio Atualizado com Sucesso....'
			else:
				status = 'Antes Faça o Login....'
				item = ''   

def exportar_produtos():
	familias = db(Familias.id < 10).select()
	bling = []
	for familia in familias:
		produtos = db(Familias_Produtos.familia == familia.id).select()
		if len(produtos) == 1:
			bling.append(dict(codigo=produto.produto,tipo = 'produto'))
		else:
			bling.append(dict(codigo=familia.id,nome = familia.nome,tipo = 'variacao'))
			for produto in produtos:
				print produto
				bling.append(dict(codigo=produto.produto,tipo = 'produto'))
	#print bling
	return dict(bling=bling)