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
		if estoque != anuncio.estoque:
			Anuncios[anuncio.id] = dict(estoque=estoque,alterado = 'S')

	form = FORM.confirm('Atualizar Estoque',{'Voltar':URL('default','index')})

	if form.accepted:

		if session.ACCESS_TOKEN:
			from meli import Meli 
			meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

			anuncios = db(Anuncios.alterado == 'S' or Anuncios.forma == 'Multiplos' ).select()
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
"""
SINCRONIZAR ESTOQUE
"""
def sicronizar_estoque():
	import time
	produtos = db(Produtos.id>0).select()
	ini =  time.time()

	for produto in produtos:
		saldo = estoque_erp(produto.id)
		med = time.time()
		qtde = qtde_vendida(produto.id)
		estoque = (float(saldo)-float(qtde)) if (float(saldo)-float(qtde)) > 0 else 0
		Produtos[produto.id] = dict(estoque1 = estoque)

	print time.time() - med
	print time.time() - ini
	
	return

def estoque_erp(codpro):
	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()
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
	
	con.close()
	
	return saldo

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

def buscar_descricao(produtoId):

	try:
		anuncioId = db(Anuncios_Produtos.produto == produtoId).select().first()['anuncio']	
	except Exception as e:
		print '1'
		descricao_curta = ''
	else:
		descricao_curta = Descricoes[Anuncios[int(anuncioId)].descricao].descricao

	return descricao_curta

def exportar_produtos():
	familias = db(Familias.id < 10).select()
	bling = []
	tray = []
	tray_variacao = []
	for familia in familias:
		produtos = db(Familias_Produtos.familia == familia.id).select()
		familiaId = '1%s' %('{:0>4}'.format(familia.id))
		descricao_curta = Descricoes[familia.descricao].descricao
		if len(produtos) == 1:
			prod = Produtos[produtos[0].produto]
			codigo = '{:0>5}'.format(prod.id)
			b = dict (codigo = codigo,
					  descricao= (prod.nome).upper(),
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
					  pai = '',
					  descricao_curta = buscar_descricao(produtos[0].produto)
					  )
			bling.append(lista_bling(b))
			tray.append(lista_tray(b))

		elif len(produtos) == 0:
			print familia.id
		else:
			prod = Produtos[produtos[0].produto]
			
			b = dict (codigo = familiaId,
					  descricao = (familia.nome).upper(),
					  ncm = prod.ncm,
					  origem = prod.origem,
					  preco = 0,
			          estoque = 0,
					  peso = prod.peso,
				      ean = 0,
					  largura = 0,
			          altura = 0,
					  comprimento = 0,
					  marca = '',
					  tipo = 'Variação',
					  pai = '',
					  descricao_curta = descricao_curta
					  )
				
			bling.append(lista_bling(b))
			tray.append(lista_tray(b))

			for produto in produtos:
				prod = Produtos[produto.produto]
				codigo = '{:0>5}'.format(prod.id)
				b = dict (codigo = codigo,
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
						  pai = familiaId,
						  descricao_curta = buscar_descricao(produto.produto),
						  variacao_nome = prod.variacao,
						  variacao_tipo = prod.atributo
						  )
				
				bling.append(lista_bling(b))
				tray_variacao.append(lista_tray_variacao(b))

	import csv
	c = csv.writer(open("produto.csv", "wb",),delimiter=';')
	head = ["ID","Codigo","Descricao","Unidade","Classificacao_fiscal","Origem","Preco","Valor_IPI_fixo","Observacoes","Situacao","Estoque","Preco_de_custo","Cod_no_fabricante","Fabricante","Localizacao","Estoque_maximo","Estoque_minimo","Peso_liquido_kg","Peso_bruto_kg","GTIN_EAN","GTIN_EAN_da_ embalagem","Largura_do_ Produto","Altura_do_Produto","Profundidade_do_produto","Data_Validade","Descricao_do_Produto_no_Fornecedor","Descricao_Complementar","Unidade_por_Caixa","Produto_Variacao","Tipo_Producao","Classe_de_enquadramento_do_IPI","Codigo_da_lista_de_servicos","Tipo_do_item","Grupo de Tags/Tags","Tributos","Código Pai","Código Integração","Grupo de Produtos","Marca","CEST","Volumes","Descrição curta","Cross-Docking","URL Imagens Externas","Link Externo","Meses Garantia","Clonar dados do pai","Condição do produto","Frete Grátis","Número FCI","Vídeo"]
	#head = ["Codigo","Descricao","Unidade","Classificacao_fiscal","Origem","Preco","Situacao","Estoque","Localizacao","Peso_liquido_kg","Peso_bruto_kg","GTIN_EAN","Largura_do_ Produto","Altura_do_Produto","Profundidade_do_produto","Produto_Variacao","Código Pai","Marca","CEST","Descrição curta","Meses Garantia","Clonar dados do pai","Condição do produto","Frete Grátis"]
	c.writerow(head)
	for row in bling:
		c.writerow(row)
	
    #head= ['Código do produto (ID Tray)';'Referência (código fornecedor)';'Nome do produto';'Marca;Preço de venda em reais';'Nome da categoria - nível 1';'Estoque do produto';'Código EAN/GTIN/UPC';'NCM do produto';'Peso do produto (gramas)';'Largura (cm)';'Altura (cm)';'Comprimento (cm)';'HTML da descrição completa';'Endereço da imagem principal do produto';'Endereço da imagem do produto 2';'Endereço da imagem do produto 3';'Endereço da imagem do produto 4';'Endereço da imagem do produto 5';'Endereço da imagem do produto 6']

    #********************************
	import xlwt
	wb = xlwt.Workbook(encoding='utf-8')
	wb1 = xlwt.Workbook(encoding='utf-8')
	ws = wb.add_sheet('Produtos')
	ws1 = wb1.add_sheet('variacao')

	row_num = 0

	font_style = xlwt.XFStyle()
	font_style.font.bold = True

	columns = ['Código do produto (ID Tray)','Referência (código fornecedor)','Nome do produto','Marca','Preço de venda em reais','Nome da categoria - nível 1','Estoque do produto','Código EAN/GTIN/UPC','NCM do produto','Peso do produto (gramas)','Largura (cm)','Altura (cm)','Comprimento (cm)','HTML da descrição completa','Endereço da imagem principal do produto','Endereço da imagem do produto 2','Endereço da imagem do produto 3','Endereço da imagem do produto 4','Endereço da imagem do produto 5','Endereço da imagem do produto 6']
	for col_num in range(len(columns)):
	    ws.write(row_num, col_num, columns[col_num], font_style)

	columns = ['Referência','CódigoEAN/GTIN/UPC','Código da variação (ID)','Estoque da variação','Altura (cm)','Comprimento (cm)','Largura (cm)','Peso da variação (gramas)','Preço de venda em reais','Nome da variação 1 (exemplo: Branco)','Tipo da variação 1 (exemplo: Cor']
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

	return dict(bling=bling)

def lista_tray(b):
	xpeso = b['peso'] or 0
	peso =  float(xpeso) * 1000
	tray_produtos_row = []
	tray_produtos_row.append('') #Código do produto (ID Tray)
	tray_produtos_row.append(b['codigo']) #Referência (código fornecedor)
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
	tray_produtos_row.append('') #Endereço da imagem principal do produto
	tray_produtos_row.append('') #Endereço da imagem do produto 2
	tray_produtos_row.append('') #Endereço da imagem do produto 3
	tray_produtos_row.append('') #Endereço da imagem do produto 4
	tray_produtos_row.append('') #Endereço da imagem do produto 5
	tray_produtos_row.append('') #Endereço da imagem do produto 6
	return tray_produtos_row

def lista_tray_variacao(b):	
	tray_variacao_row = []
	xpeso = b['peso'] or 0
	peso = float(xpeso) * 1000
	tray_variacao_row.append(b['pai']) # Referência
	tray_variacao_row.append(b['ean']) # Código EAN/GTIN/UPC
	tray_variacao_row.append(b['codigo']) # Código da variação (ID)
	tray_variacao_row.append(float(b['estoque'])) # Estoque da variação	
	tray_variacao_row.append(b['altura']) # Altura (cm)	
	tray_variacao_row.append(b['comprimento']) # Comprimento (cm)	
	tray_variacao_row.append(b['largura']) # Largura (cm)	
	tray_variacao_row.append(peso) # Peso da variação (gramas)	
	tray_variacao_row.append(b['preco']) # Preço de venda em reais	
	tray_variacao_row.append(b['variacao_nome']) # Nome da variação 1 (exemplo: Branco)
	tray_variacao_row.append(b['variacao_tipo']) # Tipo da variação 1 (exemplo: Cor)
	return tray_variacao_row

def lista_bling(b):
	bling_produtos = []
	bling_produtos.append('') # Id
	bling_produtos.append(b['codigo']) # codigo
	bling_produtos.append(b['descricao']) # descrição
	bling_produtos.append('un') # unidade
	bling_produtos.append(b['ncm']) # Classificacao_fiscal
	bling_produtos.append(b['origem']) # Origem
	bling_produtos.append(b['preco']) # Preco
	bling_produtos.append('') #Valor_IPI_fixo
	bling_produtos.append('') # Observacoes 
	bling_produtos.append('Ativo') # Situacao
	bling_produtos.append(b['estoque']) # Estoque
	bling_produtos.append(0) # Preco_de_custo 
	bling_produtos.append(0) # Cod_no_fabricante 
	bling_produtos.append(0) # Fabricante  
	bling_produtos.append('') # Localizacao
	bling_produtos.append(0) # Estoque_maximo
	bling_produtos.append(0) # Estoque_minimo
	bling_produtos.append(b['peso']) # Peso_liquido_kg
	bling_produtos.append(b['peso']) # Peso_bruto_kg
	bling_produtos.append(b['ean']) # GTIN_EAN
	bling_produtos.append('') # GTIN_EAN_da_embalagem
	bling_produtos.append(b['largura']) # Largura_do_Produto
	bling_produtos.append(b['altura']) # Altura_do_Produto
	bling_produtos.append(b['comprimento']) # Profundidade_do_produto
	bling_produtos.append('') # Data_Validade = None,
	bling_produtos.append('') # Descricao_do_Produto_no_Fornecedor
	bling_produtos.append('') # Descricao_Complementar
	bling_produtos.append('') # Unidade_por_Caixa
	bling_produtos.append(b['tipo']) # Produto_Variacao	  
	bling_produtos.append('') # Tipo_Producao 
	bling_produtos.append('') # Classe_de_enquadramento_do_IPI
	bling_produtos.append('') # Codigo_da_lista_de_servicos
	bling_produtos.append('') # Tipo_do_item
	bling_produtos.append('') # Grupo_de_Tags_Tags
	bling_produtos.append(0) # Tributos
	bling_produtos.append(b['pai']) # Codigo_Pai 
	bling_produtos.append('') # Codigo_Integracao
	bling_produtos.append('') # Grupo_de_Produtos
	bling_produtos.append(b['marca']) # Marca
	bling_produtos.append('') # CEST	
	bling_produtos.append(0) # Volumes
	bling_produtos.append(b['descricao_curta']) # Descricao_curta
	bling_produtos.append(0) # Cross_Docking
	bling_produtos.append('') # URL_Imagens_Externas
	bling_produtos.append('') # Link_Externo
	bling_produtos.append(3) # Meses_Garantia
	bling_produtos.append('NÃO') # Clonar_dados_do_pai
	bling_produtos.append('NOVO') # Condicao_do_produto
	bling_produtos.append('NÃO') # Frete_Gratis
	bling_produtos.append(0) # Numero_FCI 
	bling_produtos.append('') #  Video
	return bling_produtos


