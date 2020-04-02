# -*- coding: utf-8 -*-

@auth.requires_membership('admin')
def temp():
	query = (Pedidos.numdoc != None) & (Pedidos.numdoc != 0)
	vendas = db(query).select()
	for venda in vendas:
		orc = Pedidos1()
		orc.codmlb = venda.id
		query = "numorc = '{}'".format(venda.numdoc)
		try:
			orcamento = orc.update(query)
		except Exception as e:
			raise
		else:
			pass
		finally:
			pass

@auth.requires_membership('admin')	
def importar_vendas():
	
	import json
	from datetime import datetime

	form = SQLFORM.factory(
		Field('order_id','string',label='Id do Pedido:'),
		Field('offset','integer',label='Inicio:', default=0),
		Field('limit','integer',label='Quantidade:',default=50,requires=IS_INT_IN_RANGE(1, 51,error_message='Entre 1 e 50 !')),
		table_name='importarvendas',
		submit_button='Importar Pedidos',
		)

	itens = []

	if form.process().accepted:

		order_id = form.vars.order_id
		offset = form.vars.offset
		limit = form.vars.limit 

		if session.ACCESS_TOKEN:
			from meli import Meli 
			meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

			if order_id:
				args = "orders/%s" %(order_id)
				busca = meli.get(args,{'access_token':session.ACCESS_TOKEN})
				if busca.status_code == 200:
					xitens = json.loads(busca.content)    
					itens.append(xitens)
			else:
				args = "/orders/search/recent?seller=%s&sort=date_desc&order.status=paid&offset=%s&limit=%s" %(USER_ID,offset,limit)
				busca = meli.get(args,{'access_token':session.ACCESS_TOKEN})
				#busca = meli.get("/orders/search/recent?seller=158428813&sort=date_desc&order.status=paid", {'access_token':session.ACCESS_TOKEN})
			
				if busca.status_code == 200:
					itens = json.loads(busca.content)    
					itens = itens['results']

		for item in itens:
			# Busca Tarifas
			idsPag ='X'
			for pag in item['payments']:				
				if idsPag == 'X':
					idsPag = pag['id']
				else:
					idsPag = "%s-%s" %(idsPag,pag['id'])

				body = "/v1/payments/%s" %(pag['id'])
				buscaTaxas = meli.get_mp(body, {'access_token':session.ACCESS_TOKEN})
			
				if buscaTaxas.status_code == 200:
					taxas = json.loads(buscaTaxas.content)
					try:
						taxa = 0
						for row in taxas['fee_details']:
							if row['type'] == 'ml_fee' or row['type'] == 'mp_fee' :
								taxa = taxa + row['amount']
					except:
						taxa = 0

			body = "/shipments/%s" %(item['shipping']['id'])
			busca = meli.get(body, {'access_token':session.ACCESS_TOKEN})

			if busca.status_code == 200:
				shipping = json.loads(busca.content)
				try:
					codcid = ibge_cidade(shipping['destination']['shipping_address']['zip_code'])			
				except:
					codcid = ''
				
				body = "/shipments/%s/items" %(item['shipping']['id'])
				buscaItens = meli.get(body, {'access_token':session.ACCESS_TOKEN})
				if buscaItens.status_code == 200:
					mlItens = json.loads(buscaItens.content)
					mlitem = ''
					for row in mlItens:
						mlitem = '%s\n%s' %(mlitem,row['description'])
					#print mlitem

				db.clientes.update_or_insert(db.clientes.id == item['buyer']['id'],
	                id = item['buyer']['id'],
	                nome = "%s %s" %(item['buyer']['first_name'],item['buyer']['last_name']),
	                cnpj_cpf = item['buyer']['billing_info']['doc_number'],
	                tipo = item['buyer']['billing_info']['doc_type'],
	                endereco = shipping['destination']['shipping_address']['street_name'], 
	                numero = str(shipping['destination']['shipping_address']['street_number']), 
	                bairro = shipping['destination']['shipping_address']['neighborhood']['name'],
	                cidade = shipping['destination']['shipping_address']['city']['name'],
	                estado = shipping['destination']['shipping_address']['state']['name'],
	                codcid = codcid,
	                cep = shipping['destination']['shipping_address']['zip_code'],
	                #fone = "%s %s" %(item['buyer']['phone']['area_code'] or '',item['buyer']['phone']['number'] or ''),
	                email = item['buyer']['email'],
	                apelido = item['buyer']['nickname'],
	                )
				
				Pedidos.update_or_insert(Pedidos.id == item['shipping']['id'],
					id = item['shipping']['id'],
					buyer_id = item['buyer']['id'],
					date_created = datetime.strptime(item['date_created'][:10],'%Y-%m-%d'),
					status = shipping['status'],
					pagamento = item['status'],
					logistica = shipping['logistic']['type']
					#total = pedido.valor,
					)
				Pedidos_Itens.update_or_insert(Pedidos_Itens.id == item['id'],
					id = item['id'],
					shipping_id = item['shipping']['id'],
					payments_id = idsPag,
					item = item['order_items'][0]['item']['title'],
					item_id = item['order_items'][0]['item']['id'],
					logistica = shipping['logistic']['type'],
					status = item['status'],
					quantidade =  item['order_items'][0]['quantity'],
					valor = item['order_items'][0]['unit_price'],
					taxa = taxa,
					frete = 0, 
					)

		else:
			status = 'Antes Faça o Login....'

	elif form.errors:
	    response.flash = 'Erro no Formulário'

	return dict(itens=itens,form=form)

@auth.requires_membership('admin')
def ibge_cidade(cep):
	import requests
	import json
	response = requests.get('https://viacep.com.br/ws/{}/json/'.format(cep))
	if response.status_code == 200:
		codigo = json.loads(response.content)['ibge']
	else:
		codigo = ''
	return codigo		

# substiuido por rotina no controler lieto
@auth.requires_membership('admin')
def exportar_vendas():

	fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.numdoc,Pedidos.logistica,Pedidos.enviado)
	selectable = lambda ids: exportar(ids)
	query = (Pedidos.logistica == 'cross_docking') & (Pedidos.enviado == None)
	
	gridPedidos = grid(query ,create=False, editable=False,deletable=False,formname="pedidos",
		fields=fields,orderby =~ Pedidos.date_created,selectable=selectable,selectable_submit_button='Exportar Pedidos',)
        
	gridPedidos = DIV(gridPedidos, _class="well")
	
	return dict(gridPedidos=gridPedidos)

@auth.requires_membership('admin')
def exportar(ids):

	pedidos = db(Pedidos.id.belongs(ids)).select()
	itens = db(Pedidos_Itens.shipping_id.belongs(ids)).select()
	clientesIds = []
	for pedido in pedidos:
		clientesIds.append(pedido.buyer_id)
	clientes = db(db.clientes.id.belongs(clientesIds)).select()
	salvar_cliente(clientes)
	salvar_pedidos(pedidos)
	salvar_itens(itens)
	response.flash = 'Pedidos Exportados com Sucesso....'
	return

@auth.requires_membership('admin')
def salvar_cliente(clientes):

	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()
	for c in clientes:

		select = "select codcli from clientes where cgccpf = '%s'" %(c.cnpj_cpf)
		id = cur.execute(select).fetchone()

		estado =  buscar_uf(c.estado)
		pessoa = 'J' if c.tipo == 'CNPJ' else 'F'
		cep = c.cep[:5] + '-' + c.cep[-3:]
		bairro = c.bairro[:35].upper() if c.bairro else 'Centro'
		codcid = c.codcid

		if c.codcid == '':
			select = "select codcid from cidades where nomcid = '{}'".format(c.cidade)
			xcodcid = cur.execute(select).fetchone()
			if xcodcid:
				db.clientes[c.id] = dict(codcid = codcid)
				codcid = xcodcid
		if id:
			update = """UPDATE CLIENTES 
			SET NOMCLI = '{}',
			NOMFAN = '{}',
			ENDCLI = '{}',
			BAICLI = '{}',
			CIDCLI = '{}',
			ESTCLI = '{}',
			CEPCLI = '{}',
			TELCLI = '{}',
			DATALT = '{}',
			EMACLI = '{}',
			COCCLI = '{} '
			WHERE CGCCPF = '{}'
			""".format(c.nome[:50].upper(),
				c.apelido[:30].upper(),
				c.endereco[:50].upper(),
				bairro.upper(),
				c.cidade[:35].upper(),
				estado,
				cep,
				c.fone,
				request.now.date(),
				c.email[:40],
				codcid,
				c.cnpj_cpf)	
			cur.execute(update)

		else:
			campo = """(CODCLI,NOMCLI,NOMFAN,FISJUR,ENDCLI,BAICLI,CIDCLI,ESTCLI,CEPCLI,EMACLI,
						TELCLI,CGCCPF,DATCAD,DATALT,CODVEN,CODCON,CODCOR,CODTRA,CODTIP,PORCOM,
						PDENOR,NUMCLI,COCCLI,REGALT,EMANFE,CALSUB,ENVPDF,RETPIS,RETCOF,REGESP,
						PDEQNT)"""

			valor = "(GEN_ID(GEN_CLIENTES,1)" #CODCLI
			valor = valor + ",'{}'".format(c.nome[:50].upper()) #NOMCLI
			valor = valor + ",'{}'".format(c.apelido[:30].upper()) #NOMFAN
			valor = valor + ",'{}'".format(pessoa) #FISJUR
			valor = valor + ",'{}'".format(c.endereco[:50].upper()) #ENDCLI
			valor = valor + ",'{}'".format(bairro.upper()) #BAICLI
			valor = valor + ",'{}'".format(c.cidade[:35].upper()) #CIDCLI
			valor = valor + ",'{}'".format(estado) #ESTCLI
			valor = valor + ",'{}'".format(cep) #CEPCLI
			valor = valor + ",'{}'".format(c.email[:40]) #EMACLI

			valor = valor + ",'{}'".format(c.fone) #TELCLI
			valor = valor + ",'{}'".format(c.cnpj_cpf) #CGCCPF
			valor = valor + ",'{}'".format(request.now.date()) #DATCAD
			valor = valor + ",'{}'".format(request.now.date()) #DATALT
			valor = valor + ",146" #CODVEN
			valor = valor + ",31" #CODCON
			valor = valor + ",15" #CODCOR
			valor = valor + ",273" #CODTRA
			valor = valor + ",5" #CODTIP
			valor = valor + ",1" #PORCOM

			valor = valor + ",0" #PDENOR
			valor = valor + ",'{}'".format(c.numero) #NUMCLI
			valor = valor + ",'{}'".format(codcid) #COCLCI
			valor = valor + ",'S'" #REGALT
			valor = valor + ",'{}'".format(c.email) #EMANFE
			valor = valor + ",'S'" #CALSUB
			valor = valor + ",'S'" #ENVPDF
			valor = valor + ",'N'" #RETPIS
			valor = valor + ",'N'" #RETCOF
			valor = valor + ",''" #REGESP
			
			valor = valor + ",100" #PDEQNT

			valor = valor + ')'

			insere = "INSERT INTO CLIENTES {} VALUES {}".format(campo,valor)

			cur.execute(insere)

		con.commit()
	con.close()

@auth.requires_membership('admin')
def salvar_pedidos(pedidos):
	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()
	for pedido in pedidos:
		numdoc = pedido.numdoc or 0
		# Retorna último Ida Tabela ORCAMENTOS1
		select = 'SELECT NUMDOC FROM ORCAMENTOS1 ORDER BY NUMDOC DESC'
		lastId = cur.execute(select).fetchone()[0]
		# Retorna última Tabela de Preços
		select = 'SELECT CODTAB FROM TABELA ORDER BY CODTAB DESC'
		tabela = cur.execute(select).fetchone()[0]
		# Retorna Id do Cliente
		cnpj_cpf = db(db.clientes.id == pedido.buyer_id).select(db.clientes.cnpj_cpf).first()['cnpj_cpf']
		select = "select codcli from clientes where cgccpf = '%s'" %(cnpj_cpf)
		codcli = cur.execute(select).fetchone()[0]

		select = "select NUMDOC from ORCAMENTOS1 where NUMDOC = '%s'" %(numdoc)
		numdoc = cur.execute(select).fetchone()
		
		obsord = """
		Total Mercado Livre: {}
		Tarifas: {}
		""".format(pedido.valor,pedido.taxa)

		if not numdoc:
			orc1 = dict(NUMDOC = int(lastId) + 1,
				 	    CODEMP = 3,
					    CODCLI = codcli,
						DATDOC = str(request.now.date()),
						DATPRO = str(request.now.date()),
						NUMORC = 0,
						PEDCLI = '',
						PEDVEN = str(pedido.id)[-8:],
						PDEPED = 0,
						PDEQNT = 100,
						PDEVAL = 100,
						PDEPON = 0,
						CODTAB = str(tabela),
						CODVEN = 146,
						PORCOM = 2,
						CODCON = 2,
						CODCOR = 15,
						CODTRA = 273,
						CODRED = 0,
						VALFRE = 0,
						TIPFRE = 0,
						PEDIMP = 'N',
						TIPORC = 'P',
						SITORC = 'A',
						STATUS = 'PEN',
						NUMLOT = 0,
						HORENT = '',
						OBSORD = obsord
						)

			insere = "INSERT INTO ORCAMENTOS1 ({}) VALUES ({})".format(', '.join(orc1.keys()),str(orc1.values()).strip('[]'))

			cur.execute(insere)

			Pedidos[pedido.id] = dict(numdoc = int(lastId) + 1, enviado='SIM')

		con.commit()
	con.close()
	 
	return

@auth.requires_membership('admin')
def salvar_itens(itens):
	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()

	for item in itens:
		numdoc = db(Pedidos.id == item.shipping_id).select().first()['numdoc']
		anuncio = db(Anuncios.item_id == item.item_id).select().first()
		anuncioId = anuncio['id']
		anuncioForma = anuncio['forma']
		produtos = db(Anuncios_Produtos.anuncio == anuncioId).select()

		for row in produtos:
			indice = int(row.quantidade or 1)
			
			if anuncioForma == "Kit":
				prepro = sugerido(anuncio,int(row.produto))
			else:
				prepro = float(round(item.valor/indice,2))

			# Buscar produto banco firebird
			select = "select CODPRO,CODINT,NOMPRO,UNIPRO FROM PRODUTOS WHERE CODPRO = {}".format(row.produto)
			produto = cur.execute(select).fetchone()
			# Buscar preõ tabela banco firebird
			select = 'SELECT PREPRO FROM TABELA WHERE CODPRO = {} ORDER BY CODTAB DESC'.format(produto[0])
			preco_tabela = cur.execute(select).fetchone()[0]

			pdepro = round((1-((item.valor/indice) / preco_tabela)) * 100,2)

			select = "select * from ORCAMENTOS2 where NUMDOC = {} AND CODPRO = {}".format(int(numdoc),int(produto[0]))
			existe = cur.execute(select).fetchone()
			
			if not existe:
				item_dict = dict(NUMDOC = int(numdoc),
								CODPRO = int(produto[0]),
								CODINT = str(produto[1]),
								NOMPRO = produto[2].encode('UTF-8'),
								UNIPRO = str(produto[3]),
								QNTPRO = float(item.quantidade*indice),
								PDEPRO = float(pdepro),
								PRECUS = 0,
								PREORI = float(preco_tabela),
								PREPRO = prepro,
								ENVIAR = 'S',
								TIPPRO = 'VND',
								QNTPRE = 1)

				insere = "INSERT INTO ORCAMENTOS2 ({}) VALUES ({})".format(', '.join(item_dict.keys()),str(item_dict.values()).strip('[]'))
				
				cur.execute(insere)

		con.commit()
	con.close()
	return

@auth.requires_membership('admin')
def pedidos_cancelados():

    fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.numdoc,Pedidos.logistica,Pedidos.enviado,Pedidos.status,Pedidos.pagamento)
    query = (Pedidos.pagamento == 'cancelled') & (Pedidos.date_created >= '2020-01-01')

    gridPedidos = grid(query,create=False, editable=False,deletable=False,formname="pedidos",
        fields=fields,orderby =~ Pedidos.date_created,)

    return dict(gridPedidos=gridPedidos)

@auth.requires_membership('admin')
def atualizar_status():

	form = FORM.confirm('Atualizar status',{'Voltar':URL('default','index')})

	if form.accepted:

		from meli import Meli 
		import json
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

		rows = db(Pedidos.date_created >= '2020-01-01').select()

		for row in rows:
			args = "orders/%s" %(row.id)
			busca = meli.get(args,{'access_token':session.ACCESS_TOKEN})
			if busca.status_code == 200:
				item = json.loads(busca.content)
				Pedidos_Itens[int(row.id)] = dict(status=item['status']) 

		itens = db(Pedidos_Itens.status == 'cancelled').select()
		for item in itens:
			Pedidos[int(item.shipping_id)] = dict(pagamento=item.status)

	return dict(form=form)




