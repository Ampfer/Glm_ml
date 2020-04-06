# -*- coding: utf-8 -*-

@auth.requires_membership('admin')
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

@auth.requires_membership('admin')
def atualiza_produtos():
	rows = db(Importar_Produtos.id > 0).select()
	for row in rows:
		try:
			produto = db.produtos[int(row.codigo)]
			nome = produto.nome 
			preco = produto.preco
			marca = produto.marca
			ean = produto.ean
		except:
			nome = marca = ean = ''
			preco  = 0

		db.produtos.update_or_insert(db.produtos.id == row.codigo,
                id = row.codigo,
                nome=row.nome if row.nome else nome,
                preco = row.preco if row.preco else preco,
                estoque=row.estoque if row.estoque>0 else 0,
                marca = row.marca if row.marca else marca,
                ean = row.ean if row.ean else ean,
                )

@auth.requires_membership('admin')
def atualizar_estoque():

	anuncios = db(Anuncios.id > 0).select()
	for anuncio in anuncios:
		estoque =  sugerido(anuncio)['estoque']
		if estoque != anuncio.estoque:
			Anuncios[anuncio.id] = dict(estoque=estoque,alterado = 'S')

	form = FORM.confirm('Atualizar Estoque',{'Voltar':URL('default','index')})

	if form.accepted:

		if session.ACCESS_TOKEN:
			from meli import Meli 
			meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

			#anuncios = db(Anuncios.alterado == 'S' or Anuncios.forma == 'Multiplos' ).select()
			anuncios = db(Anuncios.item_id != '' and (Anuncios.alterado == 'S' or Anuncios.forma == 'Multiplos') ).select()
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
					else:
						Anuncios[anuncio.id] = dict(alterado = 'N')

			response.flash = 'Estoque Atualizado com Sucesso....'

		else:
			status = 'Antes Faça o Login....'

	return dict(form=form)

@auth.requires_membership('admin')
def zerar_estoque():

	form = FORM.confirm('Zerar Estoque',{'Voltar':URL('default','index')})
	if form.accepted:
		produtos = db(db.produtos.id > 0).select()
		for produto in produtos:
			db.produtos[produto.id] = dict(estoque=0)
	return dict(form=form)

def sincronizar_produtos():
	form = FORM.confirm('Sincronizar Produtos',{'Voltar':URL('default','index')})

	if form.accepted:
		prod = Produtos()
		query = "tabela = 'S' and codgru = 1"
		produtos = prod.select('codpro,nompro,modelo,clafis,codbar,oripro,locpro,sitden,unipro',query).fetchall()
		for produto in produtos:
			preco_tabela = prod.preco_tabela(produto[0])
			try:
				defaut = db.produtos[int(row.codigo)]
				nome = defailt.nome 
				marca = defailt.marca
				ncm = default.ncm
				ean = defailt.ean
				origem = default.origem
				locpro= default.locpro
				cst = default.cst
				unidade = default.unidade
				preco = default.preco

			except:
				nome = marca = ean = ncm = locpro = unidade = origem = cst = ''
				preco = 0

			db.produtos.update_or_insert(db.produtos.id == produto[0],
                id = produto[0],
                nome=produto[1] if produto[1] else nome,
                marca = produto[2] if produto[2] else marca,
                ncm = produto[3] if produto[3] else ncm,
                ean = produto[4] if produto[4] else ean,
                origem = produto[5] if produto[5] else origem,
                locpro = produto[6] if produto[6] else locpro,
                cst = produto[7] if produto[7] else cst,
                unidade = produto[8] if produto[8] else unidade,
                preco = preco_tabela if preco_tabela else preco
            )
	return dict(form=form)

"""
SINCRONIZAR ESTOQUE
"""
@auth.requires_membership('admin')
def importar_estoque():

	form = FORM.confirm('Importar Estoque',{'Voltar':URL('default','index')})

	if form.accepted:
		produtos = db(db.produtos.id>0).select()

		for produto in produtos:
			saldo = estoque_erp(produto.id)
			qtde = qtde_vendida(produto.id)
			qtde_reservada = reservado(produto.id)
			saldo_corrigido = float(saldo)-float(qtde)-float(qtde_reservada)

			estoque = saldo_corrigido if saldo_corrigido > 0 else 0

			db.produtos[produto.id] = dict(estoque = estoque)

		response.flash = 'Estoque Importado com Sucesso....'

	return dict(form=form)

def teste():

	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()
	
	for prod in db(db.produtos.id>0).select():
		db.produtos[prod.id] = dict(estoque1 = 0 )

	select = "select codpro,qntest,(select VENDIDO FROM qtde_vendida(codpro)) from produtos where tabela = 'S'"
	produtos = cur.execute(select).fetchall()
	for produto in produtos:
		estoque = float(produto[1])-float(produto[2]) - reservado(produto[0])
		estoque = 0 if estoque <0 else estoque
		db.produtos[int(produto[0])] = dict(estoque1 = estoque )
	
	con.close()
	
	return 


def estoque_erp1(codpro):
	
	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()
	
	try:
		select = "select tabela from produtos where codpro = {}".format(codpro)
		tabela = cur.execute(select).fetchone()[0]
	except:
		tabela = 'N'

	if tabela == 'S':
		saldo  = float(cur.execute('select saldo from saldo_atual({})'.format(codpro)).fetchone()[0]) 
	else:
		saldo = 0

	con.close()
	
	return saldo


@auth.requires_membership('admin')
def estoque_erp(codpro):
	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()
	
	try:
		select = "select tabela from produtos where codpro = {}".format(codpro)
		tabela = cur.execute(select).fetchone()[0]
	except:
		tabela = 'N'

	if tabela == 'S':
		select = "select SUM(qntent) from entradas2 where codpro = {}".format(codpro)
		qtent = cur.execute(select).fetchone()
		select = "select SUM(qntpro) from pedidos2 where codpro = {}".format(codpro)
		qtsai = cur.execute(select).fetchone()
		select = "select SUM(qntpro) from mestoque where entsai = 'E' and codpro = {}".format(codpro)
		qtace = cur.execute(select).fetchone()
		select = "select SUM(qntpro) from mestoque where entsai = 'S' and codpro = {}".format(codpro)
		qtacs = cur.execute(select).fetchone()
		select = "select SUM(qntpro) from devolucoes2 where codpro = {}".format(codpro)
		qtdev = cur.execute(select).fetchone()

		saldo = float(qtent[0] or 0) - float(qtsai[0] or 0) + float(qtace[0] or 0) - float(qtacs[0] or 0) + float(qtdev[0] or 0)
	else:
		saldo = 0

	con.close()
	
	return saldo

@auth.requires_membership('admin')
def qtde_vendida(codpro):
	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()

	select = "select sum(qntpro) from orcamentos1, orcamentos2 where orcamentos1.sitorc = 'A' and tiporc = 'P' and orcamentos1.numdoc = orcamentos2.numdoc and orcamentos2.codpro = {}".format(codpro)
	orcamentos = cur.execute(select).fetchone()

	select = """select sum(pedidos2.qntpro) from pedidos1, pedidos2, orcamentos1
				where pedidos1.numdoc = pedidos2.numdoc and pedidos2.codpro = {0} and pedidos1.numorc=orcamentos1.numdoc 
				and orcamentos1.sitorc = 'A' and orcamentos1.tiporc = 'P' """.format(codpro)
	
	pedidos = cur.execute(select).fetchone()

	con.close()

	vendido =  orcamentos[0] if orcamentos[0] else 0
	enviado =  pedidos[0] if pedidos[0] else 0

	return (vendido - enviado)

"""
**************************************************
"""
@auth.requires_membership('admin')
def reservado(produtos_id):
    
    query = (Envios_Full.status == "Reservado") & (Envios_Produtos.envio_id == Envios_Full.id)
    query = query & '(Envios_Produtos.produtos_id == {})'.format(produtos_id)
    produtos= db(query).select()
    soma = 0
    for row in produtos:
        soma += int(row.envios_produtos.quantidade)
    return soma

@auth.requires_membership('admin')
def atualizar_sugerido():
	anuncios = db(Anuncios.id > 0).select()
	for anuncio in anuncios:
		anuncioId = int(anuncio.id)
		Anuncios[anuncioId] = dict(preco=sugerido(anuncio)['preco'])
	#response.js = "$('#teste').get(0).reload()"
	response.js = "location.reload(true)"

@auth.requires_membership('admin')
def alterar_desconto():
	id = int(request.post_vars.id)
	valor = request.post_vars.valor
	Anuncios[id] = dict(desconto = valor)

@auth.requires_membership('admin')
def alterar_preco():
	id = int(request.post_vars.id)
	valor = request.post_vars.valor
	anuncio = Anuncios[id]
	desconto = anuncio.desconto
	ep = sugerido(anuncio)['preco']
	desc = round((1-(float(valor)*(1-float(desconto/100)))/float(ep))*100,2)
	Anuncios[id] = dict(preco = valor,desconto = desc)

@auth.requires_membership('admin')
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

@auth.requires_membership('admin')
def atualizar_preco():
	Anuncios.sugerido = Field.Virtual('sugerido',lambda row: sugerido(row.anuncios)['preco'], label='Sugerido')
	fields = (Anuncios.id,Anuncios.titulo,Anuncios.categoria,Anuncios.tipo,Anuncios.forma,Anuncios.frete,Anuncios.fretegratis,Anuncios.desconto,Anuncios.preco,Anuncios.sugerido)

	formPrecos = grid(Anuncios,60,formname="formPrecos",fields=fields,orderby=Anuncios.titulo, deletable=False)
	
	btnSugerido = A(SPAN(_class="glyphicon glyphicon-cog"), ' Atualizar Sugerido ', _class="btn btn-default",_id='atualizarsugerido', _onclick="if (confirm('Deseja Atualizar Preços com Sugeridos ?')) ajax('%s',[], 'formPrecos');" %URL('atualizar_sugerido',args=request.vars.keywords))
	btnPreco = A(SPAN(_class="glyphicon glyphicon-cog"), ' Atualizar Preços ', _class="btn btn-default",_id='sincronizarpreco', _onclick="if (confirm('Deseja Atualizar Preços do Mercado Livre ?')) ajax('%s', [], 'formPrecosMl');" %URL('sincronizar_preco'))

	formPrecos[0].insert(-1, btnSugerido)
	formPrecos[0].insert(-1, btnPreco)

	formPrecos = DIV(formPrecos, _class="well")

	if request.args(-3) == 'edit':
		idAnuncio = request.args(-1)
		redirect(URL('anuncio','anuncio', args=idAnuncio,))

	return dict(formPrecos=formPrecos)

@auth.requires_membership('admin')
def buscar_variacao_preco(idAnuncio,preco):
    variacao = []
    rows = db(Anuncios_Produtos.anuncio==idAnuncio).select()
    for row in rows:
        variacaoProduto = dict(id=row.variacao_id,
                               price=float(preco),
                               )
        variacao.append(variacaoProduto)
    return variacao

@auth.requires_membership('admin')
def buscar_variacao_estoque(idAnuncio):
    variacao = [] 
    rows = db(Anuncios_Produtos.anuncio==idAnuncio).select()
    for row in rows:
        produto = db.produtos[row.produto]
        variacaoProduto = dict(id=row.variacao_id,
                               available_quantity=float(produto.estoque),
                               )
        variacao.append(variacaoProduto)
    return variacao

@auth.requires_membership('admin')
def ean1():
    rows = db(Anuncios.id>0).select()
    for row in rows:
        if row.forma == 'Individual':
            idProduto = db(Anuncios_Produtos.anuncio==row.id).select().first()['produto']
            ean = db(db.produtos.id==idProduto).select().first()['ean']
            if ean:
            	query = (Anuncios_Atributos.anuncio == row.id) & (Anuncios_Atributos.atributo == 3)
            	Anuncios_Atributos.update_or_insert(query,anuncio=row.id, atributo = 3, valor= ean)

@auth.requires_membership('admin')
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

@auth.requires_membership('admin')
def buscar_descricao(produtoId):

	try:
		idAnuncio = db(Anuncios_Produtos.produto == produtoId).select().first()['anuncio']	
	except Exception as e:
		descricao_curta = ''
	else:
		idDescricao = Anuncios[idAnuncio].descricao

		if idDescricao == None:   
			idFamilia = int(Anuncios[idAnuncio].familia)
			try:
				descricao_curta = Descricoes[Familias[idFamilia].descricao].descricao
			except:
				descricao_curta = '' 
		else:
			descricao_curta = Descricoes[Anuncios[int(idAnuncio)].descricao].descricao

	return descricao_curta

@auth.requires_membership('admin')
def exportar_produtos():

	if type(request.vars.ids) is list:
		ids = request.vars.ids
	else:
		ids = []
		ids.append(request.vars.ids)

	familias = db(Familias.id.belongs(ids)).select()
	#bling = []
	tray = []
	tray_variacao = []

	for familia in familias:
		produtos = db(Familias_Produtos.familia == familia.id).select()
		descricao_curta = Descricoes[familia.descricao].descricao
		prod = db.produtos[produtos[0].produto]
		marca = Marcas[familia.marca].marca

		query = (Familias_Imagens.familia == familia.id) & (Familias_Imagens.imagem==Imagens.id)
		rows = db(query).select()
		imagens = []
		for row in rows:
			imagem = "https://webimagens.s3-sa-east-1.amazonaws.com/{}".format(row.imagens.imagem)
			imagens.append(imagem)
		
		b = dict (codigo = familia.id,
				  descricao= familia.nome,
				  ncm =  '',
				  origem =  '',
				  preco =  '',
		          estoque = 0,
				  peso = prod.peso,
			      ean = '',
				  largura ='',
		          altura =  '',
				  comprimento = '',
				  marca = marca,
				  tipo = 'Produto',
				  pai = '',
				  descricao_curta = descricao_curta,
				  img1 = imagens[0]
				  )
		
		#bling.append(lista_bling(b))
		tray.append(lista_tray(b))

		for produto in produtos:
			prod = db.produtos[produto.produto]

			b = dict (codigo = prod.id,
					  descricao=  '%s:%s' % (prod.atributo,prod.variacao),
					  ncm =  prod.ncm,
					  origem =  prod.origem,
					  preco =  prod.preco,
			          estoque =  prod.estoque,
					  peso = prod.peso,
				      ean = prod.ean,
					  largura = prod.largura,
			          altura =  prod.altura,
					  comprimento = prod.comprimento,
					  marca = prod.marca,
					  tipo = 'Produto',
					  pai = familia.id,
					  descricao_curta = buscar_descricao(produto.produto),
					  variacao_nome = prod.variacao,
					  variacao_tipo = prod.atributo
					  )
			
			#bling.append(lista_bling(b))
			tray_variacao.append(lista_tray_variacao(b))

	import xlwt
	wb = xlwt.Workbook(encoding='utf-8')
	wb1 = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Produtos')
	ws1 = wb1.add_sheet('variacao')

	row_num = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['Código do produto (ID Tray)','Nome do produto','Marca','Preço de venda em reais','Nome da categoria - nível 1','Estoque do produto','Código EAN/GTIN/UPC','NCM do produto','Peso do produto (gramas)','Largura (cm)','Altura (cm)','Comprimento (cm)','HTML da descrição completa','Endereço da imagem principal do produto','Endereço da imagem do produto 2','Endereço da imagem do produto 3','Endereço da imagem do produto 4','Endereço da imagem do produto 5','Endereço da imagem do produto 6']
	for col_num in range(len(columns)):
	    ws.write(row_num, col_num, columns[col_num], font_style)

	columns = ['Código da variação (ID)','Referência','Código do produto','CódigoEAN/GTIN/UPC','Estoque da variação','Altura (cm)','Comprimento (cm)','Largura (cm)','Peso da variação (gramas)','Preço de venda em reais','Nome da variação 1 (exemplo: Branco)','Tipo da variação 1 (exemplo: Cor']
	for col_num in range(len(columns)):
	    ws1.write(row_num, col_num, columns[col_num], font_style)

	font_style = xlwt.XFStyle()

	rows = tray
	for row in rows:
	    row_num += 1
	    for col_num in range(len(row)):
	        ws.write(row_num, col_num, row[col_num], font_style)
	
	row_num = 0	
	rows = tray_variacao
	for row in rows:
	    row_num += 1
	    for col_num in range(len(row)):
	        ws1.write(row_num, col_num, row[col_num], font_style)

	wb.save('tray_produtos.xls')
	wb1.save('tray_variacao.xls')
	#********************************

	return dict(tray=tray)

@auth.requires_membership('admin')
def lista_tray(b):
	xpeso = b['peso'] or 0
	peso =  float(xpeso) * 1000
	tray_produtos_row = []
	tray_produtos_row.append(b['codigo']) #Código do produto (ID Tray)
	tray_produtos_row.append(b['descricao']) #Nome do produto
	tray_produtos_row.append(b['marca']) #Marca
	tray_produtos_row.append(b['preco']) #Preço de venda em reais
	tray_produtos_row.append('Ferramentas') #Nome da categoria - nível 1
	tray_produtos_row.append(b['estoque']) #Estoque do produto
	tray_produtos_row.append(b['ean']) #Código EAN/GTIN/UPC
	tray_produtos_row.append(b['ncm']) #NCM do produto;
	tray_produtos_row.append(peso) #NCM do produto;Peso do produto (gramas)	#Peso do produto (gramas)
	tray_produtos_row.append(b['largura']) #Largura (cm)
	tray_produtos_row.append(b['altura']) #Altura (cm)
	tray_produtos_row.append(b['comprimento']) #Comprimento (cm)
	tray_produtos_row.append(b['descricao_curta']) #HTML da descrição completa
	tray_produtos_row.append(b['img1']) #Endereço da imagem principal do produto
	tray_produtos_row.append('') #Endereço da imagem do produto 2
	tray_produtos_row.append('') #Endereço da imagem do produto 3
	tray_produtos_row.append('') #Endereço da imagem do produto 4
	tray_produtos_row.append('') #Endereço da imagem do produto 5
	tray_produtos_row.append('') #Endereço da imagem do produto 6
	return tray_produtos_row

@auth.requires_membership('admin')
def lista_tray_variacao(b):	
	tray_variacao_row = []
	xpeso = b['peso'] or 0
	peso = float(xpeso) * 1000
	tray_variacao_row.append('') # Código da variação (ID)
	tray_variacao_row.append(b['codigo']) # Referêcia da variação
	tray_variacao_row.append(b['pai']) # Código do produto
	tray_variacao_row.append(b['ean']) # Código EAN/GTIN/UPC
	tray_variacao_row.append(float(b['estoque'])) # Estoque da variação	
	tray_variacao_row.append(b['altura']) # Altura (cm)	
	tray_variacao_row.append(b['comprimento']) # Comprimento (cm)	
	tray_variacao_row.append(b['largura']) # Largura (cm)	
	tray_variacao_row.append(peso) # Peso da variação (gramas)	
	tray_variacao_row.append(b['preco']) # Preço de venda em reais	
	tray_variacao_row.append(b['variacao_nome']) # Nome da variação 1 (exemplo: Branco)
	tray_variacao_row.append(b['variacao_tipo']) # Tipo da variação 1 (exemplo: Cor)
	return tray_variacao_row

@auth.requires_membership('admin')
def exportar_bling():

    fields = (Anuncios.titulo, Anuncios.preco, Anuncios.estoque)
    selectable = lambda ids: bling_csv(ids)
    query = (Anuncios.status == 'active') 
    
    gridAnuncios = grid(query ,create=False, editable=False,deletable=False,formname="pedidos", alt='250px',
        fields=fields,orderby =~ Anuncios.vendido, selectable=selectable, selectable_submit_button='Exportar Bling',)

    return dict(gridAnuncios = gridAnuncios)

def bling_csv(ids):

    anuncios = db(Anuncios.id.belongs(ids)).select()
    produtos_bling = []
    for anuncio in anuncios:

        idProduto = db(Anuncios_Produtos.anuncio == anuncio.id).select().first()['produto']
        produto = db(db.produtos.id == idProduto).select().first()
        descricao = buscar_descricao(idProduto)
        imagens = db(Anuncios_Imagens.anuncio == anuncio.id).select()

        url_imagens = []
        for imagem in imagens:
            img = Imagens[int(imagem.imagem)].imagem
            url_imagens.append('http://18.230.73.54/glm_ml/default/download/{}'.format(img))

        url = ', '.join(url_imagens)

        bling_produto = []
        bling_produto.append('')# Id
        bling_produto.append(str(idProduto).zfill(5)) # codigo
        bling_produto.append(anuncio.titulo) # descrição
        bling_produto.append('un') # unidade
        bling_produto.append(produto.ncm) # Classificacao_fiscal
        bling_produto.append(produto.origem) # Origem
        bling_produto.append(anuncio.preco) # Preco
        bling_produto.append('') #Valor_IPI_fixo
        bling_produto.append('') # Observacoes 
        bling_produto.append('Ativo') # Situacao
        bling_produto.append(anuncio.estoque) # Estoque
        bling_produto.append(0) # Preco_de_custo 
        bling_produto.append(0) # Cod_no_fabricante 
        bling_produto.append(0) # Fabricante  
        bling_produto.append(produto.locpro) # Localizacao
        bling_produto.append(0) # Estoque_maximo
        bling_produto.append(0) # Estoque_minimo
        bling_produto.append(produto.peso) # Peso_liquido_kg
        bling_produto.append(produto.peso) # Peso_bruto_kg
        bling_produto.append(produto.ean) # GTIN_EAN
        bling_produto.append(produto.ean) # GTIN_EAN_da_embalagem
        bling_produto.append(produto.largura) # Largura_do_Produto
        bling_produto.append(produto.altura) # Altura_do_Produto
        bling_produto.append(produto.comprimento) # Profundidade_do_produto
        bling_produto.append('') # Data_Validade = None,
        bling_produto.append('') # Descricao_do_Produto_no_Fornecedor
        bling_produto.append('') # Descricao_Complementar
        bling_produto.append('') # Unidade_por_Caixa
        bling_produto.append('produto') # Produto_Variacao    
        bling_produto.append('Terceiros') # Tipo_Producao 
        bling_produto.append('') # Classe_de_enquadramento_do_IPI
        bling_produto.append('') # Codigo_da_lista_de_servicos
        bling_produto.append('Mercadoria para Revenda') # Tipo_do_item
        bling_produto.append('') # Grupo_de_Tags_Tags
        bling_produto.append(0) # Tributos
        bling_produto.append('') # Codigo_Pai 
        bling_produto.append('') # Codigo_Integracao
        bling_produto.append('') # Grupo_de_Produtos
        bling_produto.append(produto.marca) # Marca
        bling_produto.append('') # CEST 
        bling_produto.append(1) # Volumes
        bling_produto.append(descricao) # Descricao_curta
        bling_produto.append(0) # Cross_Docking
        bling_produto.append(url) # URL_Imagens_Externas
        bling_produto.append('') # Link_Externo
        bling_produto.append(3) # Meses_Garantia
        bling_produto.append('NÃO') # Clonar_dados_do_pai
        bling_produto.append('NOVO') # Condicao_do_produto
        bling_produto.append('NÃO') # Frete_Gratis
        bling_produto.append(0) # Numero_FCI 
        bling_produto.append('') # Video
        bling_produto.append('') # Departamento
        bling_produto.append('Centímetro') # Unidade de Medida

        Anuncios[anuncio.id] = dict(bling = True)
        produtos_bling.append(bling_produto)

    import csv
    c = csv.writer(open("produtos_bling.csv", "wb",),delimiter=';')
    head = ["ID","Codigo","Descricao","Unidade","Classificacao_fiscal","Origem","Preco","Valor_IPI_fixo","Observacoes","Situacao","Estoque","Preco_de_custo","Cod_no_fabricante","Fabricante","Localizacao","Estoque_maximo","Estoque_minimo","Peso_liquido_kg","Peso_bruto_kg","GTIN_EAN","GTIN_EAN_da_ embalagem","Largura_do_ Produto","Altura_do_Produto","Profundidade_do_produto","Data_Validade","Descricao_do_Produto_no_Fornecedor","Descricao_Complementar","Unidade_por_Caixa","Produto_Variacao","Tipo_Producao","Classe_de_enquadramento_do_IPI","Codigo_da_lista_de_servicos","Tipo_do_item","Grupo de Tags/Tags","Tributos","Código Pai","Código Integração","Grupo de Produtos","Marca","CEST","Volumes","Descrição curta","Cross-Docking","URL Imagens Externas","Link Externo","Meses Garantia","Clonar dados do pai","Condição do produto","Frete Grátis","Número FCI","Vídeo"]
    #head = ["Codigo","Descricao","Unidade","Classificacao_fiscal","Origem","Preco","Situacao","Estoque","Localizacao","Peso_liquido_kg","Peso_bruto_kg","GTIN_EAN","Largura_do_ Produto","Altura_do_Produto","Profundidade_do_produto","Produto_Variacao","Código Pai","Marca","CEST","Descrição curta","Meses Garantia","Clonar dados do pai","Condição do produto","Frete Grátis"]
    c.writerow(head)
    for row in produtos_bling:
        c.writerow(row)

    session.flash = 'Arquivo csv gerado com sucesso...!'

    return

def bling_estoque():

	form = FORM.confirm('Gerar csv',{'Voltar':URL('default','index')})

	if form.accepted:

		head = ['ID Produto','Codigo produto *','GTIN **','Descrição Produto','Deposito (OBRIGATÓRIO)','Balanço (OBRIGATÓRIO)','Valor (OBRIGATÓRIO)','Preço de Custo,Observação','Data']
		estoque_bling = []
		estoque_bling.append(head)
		dt = request.now.strftime('%d/%m/%Y')

		anuncios = db(Anuncios.bling == True).select()
		for anuncio in anuncios:
			print anuncio.titulo
			idProduto = str(db(Anuncios_Produtos.anuncio == anuncio.id).select().first()['produto']).zfill(5)
			row = []
			row.append('') #ID Produto
			row.append(idProduto) #Codigo produto *
			row.append('') #GTIN **,
			row.append('') #Descrição Produto
			row.append('Geral') #Deposito (OBRIGATÓRIO)
			row.append(anuncio.estoque) #Balanço (OBRIGATÓRIO)
			row.append(anuncio.preco) #Valor (OBRIGATÓRIO)
			row.append(0) #Preço de Custo
			row.append('') #Observação
			row.append(dt) #Data

			estoque_bling.append(row)

		import csv
		c = csv.writer(open("estoque_bling.csv", "wb",),delimiter=';')
		for row in estoque_bling:
			c.writerow(row)

			session.flash = 'Arquivo csv gerado com sucesso...!'

	return dict(form=form)

		

