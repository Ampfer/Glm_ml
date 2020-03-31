#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs

#ERPFDB = "D:/lieto/Dados/ERP.FDB"
#SERVERNAME = "localhost"

from unicodedata import normalize

@auth.requires_membership('admin')
def remover_acentos(txt, codif='utf-8'):
	return normalize('NFKD', txt.decode(codif)).encode('ASCII', 'ignore')

@auth.requires_membership('admin')
def cobranca():

	form = SQLFORM.factory(Field('csvfile','upload',uploadfield=False,label='Arquivo Retorno:',requires=notempty)
		,submit_button='Mostrar Boletos')

	boletos = []

	if form.process().accepted:
		if request.vars.csvfile != None:
			receber = Receber()
			clientes =Clientes()
			file =  request.vars.csvfile.file
			for linha in file:
				if str(linha[0:1]).zfill(1) == '1' and str(linha[108:110]).zfill(2) == '06':			
					dcto = linha[37:44]
					parcela = linha[45:47]
					tipo = str(linha[47:48]) if str(linha[47:48]) == 'X' else 'A'
					documento = dcto + '-' + parcela + tipo
					vencimento = '{}.{}.20{}'.format(linha[146:148].zfill(2),linha[148:150].zfill(2),linha[150:152].zfill(2)) 
					credito =    '{}.{}.20{}'.format(linha[110:112].zfill(2),linha[112:114].zfill(2),linha[114:116].zfill(2)) 
					
					# Buscar Receber
					query = "NUMDOC = {} and TIPDOC = '{}' and NUMPAR LIKE '{}%'".format(int(dcto),tipo,parcela)
					rec = receber.select('NUMIDE,CODCLI,DATPAG',query).fetchone()
					#Buscar Cliente
					query = "codcli = {}".format(rec[1])
					cliente = clientes.select('codcli,nomcli', query).fetchone()
					status = 'Aberto' if rec[2] is None else 'Pago'


					boleto = dict(rowId = rec[0],
								  documento =  documento,
								  codigo = cliente[0],
								  cliente = cliente[1],
								  vencimento = vencimento,
								  data_credito = credito,
								  valor = round(float(linha[152:165])/100,2),
								  valor_pago = round(float(linha[253:266])/100,2),
								  desconto = round(float(linha[240:253])/100,2),
								  juros = round(float(linha[201:214])/100 + float(linha[266:279])/100,2),
								  status = status
								  )

					boletos.append(boleto)
					session.boletos = boletos

	elif form.errors:
		response.flash = 'Erro no Formulário'

	return dict(form=form, boletos = boletos)

@auth.requires_membership('admin')
def baixar_boletos():
	ids = request.vars['ids[]']
	boletos =session.boletos

	lote = Lotes()
	lote.numide = int(lote.last_id()) + 1 
	lote.codcor = 6 
	lote.valpag = 0
	lote.numche = 0
	lote.tipdoc = 'R' 
	lote.obspag = ' '

	for boleto in boletos:

		if boleto['rowId']:
			receber = Receber()
			query = 'numide = {}'.format(boleto['rowId'])
			rec = receber.select('datpag,numpar', query).fetchone()
			
			if rec[0] is None:

				recebimento = Recebimentos()

				recebimento.numide = int(recebimento.last_id())
				recebimento.iderec = boleto['rowId']
				recebimento.datpag = boleto['data_credito']
				recebimento.valpag = boleto['valor_pago']
				recebimento.codcor = 6 
				recebimento.obspag = ''
				recebimento.idelot = lote.numide

				recebimento.insert()

				lote.valpag += boleto['valor_pago']
				lote.datpag  = boleto['data_credito']

				fluxo = Fluxo()

				fluxo.numide = int(fluxo.last_id())
				fluxo.codcor = 6
				fluxo.datdoc = boleto['data_credito']
				fluxo.hordoc = "{}:{}:{}".format(str(request.now.hour).zfill(2), str(request.now.minute).zfill(2),str(request.now.second).zfill(2))
				fluxo.valdoc = boleto['valor_pago']
				fluxo.hisdoc = "REC. {}-{} de (C{}) {}".format(boleto['documento'],rec[1],boleto['codigo'], boleto['cliente'].encode('UTF-8').replace("'",""))[0:60]
				fluxo.credeb = '+'
				fluxo.codpag = 0
				fluxo.origem = 'REC'
				fluxo.iderec = recebimento.numide
				fluxo.tippag = 'OUT'

				fluxo.insert()

				query = 'numide = {}'.format(boleto['rowId'])
				receber.datpag = boleto['data_credito']
				receber.valpag = boleto['valor_pago']
				receber.valjur = boleto['juros']

				receber.update(query)

	if lote.valpag > 0:
		lote.insert()

	return lote.valpag

@auth.requires_membership('admin')
def pedidos():
	orcamentos1 = Orcamentos1()
	query = "codven = 146 and sitorc = 'A' and tiporc = 'P' "
	lista = orcamentos1.select('numdoc,datdoc,codcli,valfre',query,'order by datdoc desc').fetchall()
	clientes = Clientes()
	orcamentos2 = Orcamentos2()
	orcamentos = []
	for row in lista:
		query = "codcli = {}".format(row[2])
		cliente = clientes.select('codcli,nomcli', query).fetchone()
		query = 'numdoc = {}'.format(row[0])
		try:
			total_itens = orcamentos2.select('sum(qntpro*prepro)',query).fetchone()[0]
			valor = float(total_itens) or 0
		except:
			valor = 0
		
		orcamento = dict(
			data = str(row[1]),
			rowId = row[0],
			codigo = row[2],
			cliente = cliente[1],
			valor = valor
			)
		orcamentos.append(orcamento)

	return dict(orcamentos=orcamentos)

@auth.requires_membership('admin')
def salvar_pedidos():
	ids = []
	
	if type(request.vars['ids[]']) == list:
		ids = request.vars['ids[]']
	else:
		ids.append(request.vars['ids[]'])
	
	sucesso = 0
	erro = 0

	for id in ids:

		try:
			numdoc = lieto_pedidos1(int(id))
			lieto_pedidos2(int(numdoc),int(id))
			sucesso += 1
		except Exception as e:
			erro += 1

		#mensagem = """{} pedido(s) salvo(s) com sucesso
		#{} erro(s) ao salvar""".format(sucesso,erro)

		mensagem = "{} pedido(s) salvo(s) com sucesso \n{} erro(s) ao salvar".format(sucesso,erro)
		
	return mensagem

@auth.requires_membership('admin')
def exportar_vendas():

	fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.numdoc,Pedidos.logistica,Pedidos.enviado)
	selectable = lambda ids: exportar(ids)
	query = (Pedidos.logistica == 'cross_docking') & (Pedidos.enviado == None)
	
	gridPedidos = grid(query ,create=False, editable=False,deletable=False,formname="pedidos", alt='250px',
		fields=fields,orderby =~ Pedidos.date_created,selectable=selectable,selectable_submit_button='Exportar Pedidos',)
        
	gridPedidos = DIV(gridPedidos, _class="well")
	
	return dict(gridPedidos=gridPedidos)

@auth.requires_membership('admin')
def exportar(ids):
	session.full = False
	vendas = db(Pedidos.id.belongs(ids)).select()
	for venda in vendas:
		cliente_ml = db(db.clientes.id == venda.buyer_id).select().first()
		lieto_clientes(cliente_ml)
		numorc = lieto_orcamentos1(venda)
		itens = db(Pedidos_Itens.shipping_id==venda.id).select()
		lieto_orcamentos2(numorc,itens)
	
	session.flash = 'Pedidos Exportados com Sucesso....'
	return

@auth.requires_membership('admin')
def vendas_full():

	fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.numdoc,Pedidos.logistica,Pedidos.enviado)
	selectable = lambda ids: exportar_full(ids)
	query = (Pedidos.logistica == 'fulfillment') & (Pedidos.enviado == None)

	gridPedidos = grid(query,create=False, editable=False,deletable=False,formname="pedidos",
		fields=fields,orderby =~ Pedidos.date_created,selectable=selectable,selectable_submit_button='Exportar Pedidos',)
        
	#gridPedidos = DIV(gridPedidos, _class="well")

	return dict(gridPedidos=gridPedidos)

@auth.requires_membership('admin')
def exportar_full(ids):
	session.full = True
	venda = db(Pedidos.id.belongs(ids)).select()
	for venda in venda:
		cliente_ml = db(db.clientes.id == venda.buyer_id).select().first()
		lieto_clientes(cliente_ml)
		numorc = lieto_orcamentos1(venda)
		itens = db(Pedidos_Itens.shipping_id==venda.id).select()
		lieto_orcamentos2(numorc,itens)
		numdoc = lieto_pedidos1(numorc)
		lieto_pedidos2(numdoc,numorc)

	session.flash = "Pedido Importado com Sucesso....!"
	return

@auth.requires_membership('admin')
def lieto_clientes(cliente_ml):

	cliente = Clientes()

	'''
	cliente.nomcli = cliente_ml.nome[:50].upper().decode('utf-8').replace("'","")
	cliente.nomfan = cliente_ml.apelido[:30].upper().decode('utf-8').replace("'","")
	cliente.fisjur = 'J' if cliente_ml.tipo == 'CNPJ' else 'F'
	cliente.endcli = cliente_ml.endereco[:50].upper().decode('utf-8').replace("'","")
	cliente.baicli = cliente_ml.bairro[:35].upper().decode('utf-8').replace("'","") if cliente_ml.bairro else 'CENTRO'
	cliente.cidcli = (cliente_ml.cidade[:35]).decode('utf-8').replace("'","").upper()
	cliente.estcli = buscar_uf(cliente_ml.estado).decode('utf-8').replace("'","")
	cliente.cepcli = '{}-{}'.format(cliente_ml.cep[:5],cliente_ml.cep[-3:])
	cliente.emacli = cliente_ml.email[:40]
	cliente.telcli = cliente_ml.fone if cliente_ml.fone else ' '
	cliente.cgccpf = cliente_ml.cnpj_cpf
	cliente.numcli = cliente_ml.numero
	cliente.datalt = '{}'.format(request.now.date())
	cliente.coccli = cliente_ml.codcid if cliente_ml.codcid else cliente.buscar_coccli(remover_acentos(cliente_ml.cidade[:35]).upper())
	#cliente.coccli = cliente_ml.codcid if cliente_ml.codcid else cliente.buscar_coccli(remover_acentos(cliente.cidcli))
	'''

	cliente.nomcli = remover_acentos(cliente_ml.nome[:50]).replace("'","").upper()
	cliente.nomfan = remover_acentos(cliente_ml.apelido[:30]).replace("'","").upper()
	cliente.fisjur = 'J' if cliente_ml.tipo == 'CNPJ' else 'F'
	cliente.endcli = remover_acentos(cliente_ml.endereco[:50]).replace("'","").upper()
	cliente.baicli = remover_acentos(cliente_ml.bairro[:35]).replace("'","").upper() if cliente_ml.bairro else 'CENTRO'
	cliente.cidcli = remover_acentos(cliente_ml.cidade[:35]).replace("'","").upper()
	cliente.estcli = buscar_uf(cliente_ml.estado).decode('utf-8').replace("'","")
	cliente.cepcli = '{}-{}'.format(cliente_ml.cep[:5],cliente_ml.cep[-3:])
	cliente.emacli = cliente_ml.email[:40]
	cliente.telcli = cliente_ml.fone if cliente_ml.fone else ' '
	cliente.cgccpf = cliente_ml.cnpj_cpf
	cliente.numcli = cliente_ml.numero
	cliente.datalt = '{}'.format(request.now.date())
	cliente.coccli = cliente_ml.codcid if cliente_ml.codcid else cliente.buscar_coccli(cliente.cidcli)

	cliente.emanfe = cliente_ml.email
	cliente.codven = 148 if session.full else 146
	cliente.codcon = 31
	cliente.codcor = 15
	cliente.codtra = 273
	cliente.codtip = 5
	cliente.porcom = 1
	cliente.pdenor = 0
	cliente.regalt = 'S'
	cliente.calsub = 'N'
	cliente.envpdf = 'S'
	cliente.retpis = 'N'
	cliente.retcof = 'N'
	cliente.regesp = ''
	cliente.pdeqnt = 100

	cli = cliente.buscar_cliente_cnpj(cliente_ml.cnpj_cpf)
	
	if cli:
		query = "CGCCPF = '%s'" %(cliente_ml.cnpj_cpf)
		cliente.update(query)		
	else:
		cliente.codcli = int(cliente.lastId())
		cliente.datcad = '%s' %(request.now.date())
		cliente.insert()

	return 

@auth.requires_membership('admin')
def lieto_orcamentos1(venda):
	orcamentos1 = Orcamentos1()
	#venda_itens = db(db.pedidos_itens.shipping_id  == venda.id).select()

	# Retorna última Tabela de Preços
	tabela = orcamentos1.tabela()
	# Retorna Id do Cliente
	cnpj_cpf = db(db.clientes.id == venda.buyer_id).select(db.clientes.cnpj_cpf).first()['cnpj_cpf']
	cliente = Clientes()
	codcli = cliente.buscar_cliente_cnpj(cnpj_cpf)[0]

	obsord = """Total Mercado Livre: {}
	Tarifas: {}
	Pedido ML : {}""".format(venda.valor,venda.taxa,venda.id)

	orcamentos1.codcli = codcli
	orcamentos1.pedven = ''
	orcamentos1.codmlb = str(venda.id)
	orcamentos1.codtab = str(tabela)
	orcamentos1.codven = 148 if session.full else 146
	orcamentos1.obsord = obsord
	orcamentos1.porcom = ((0.02*(float(venda.valor) - float(venda.taxa))) / float(venda.valor))*100
	orcamentos1.codemp = 3
	orcamentos1.numorc = 0
	orcamentos1.pedcli = ''
	orcamentos1.pdeped = 0
	orcamentos1.pdeqnt = 0 if session.full else 100
	orcamentos1.pdeval = 0 if session.full else 100
	orcamentos1.pdepon = 0
	orcamentos1.codcon = 1
	orcamentos1.codcor = 15
	orcamentos1.codtra = 273
	orcamentos1.codred = 0
	orcamentos1.valfre = 0
	orcamentos1.tipfre = 0
	orcamentos1.pedimp = 'N'
	orcamentos1.tiporc = 'P'
	orcamentos1.sitorc = 'A'
	orcamentos1.status = 'PEN'
	orcamentos1.numlot = 0
	orcamentos1.horent = ''

	#numdoc = venda.numdoc or 0
	#orc =  orcamentos1.buscar(numdoc)

	query = "codmlb = '{}'".format(venda.id)
	try:
		numdoc = orcamentos1.select('NUMDOC',query).fetchone()[0]
	except:
		numdoc = None

	if numdoc:
		print 'orcamento ja cadastrado'	
		Pedidos[venda.id] = dict(numdoc = numdoc, enviado='SIM')
		#query = "NUMDOC = '%s'" %(int(numdoc))
		#orcamentos1.update(query)
	else:
		lastId = orcamentos1.last_id() # Retorna último Id Tabela ORCAMENTOS1
		numdoc = int(lastId) + 1
		orcamentos1.numdoc = int(lastId) + 1
		orcamentos1.datdoc = str(venda.date_created)
		orcamentos1.datpro = str(venda.date_created)

		orcamentos1.insert()

		Pedidos[venda.id] = dict(numdoc = int(lastId) + 1, enviado='SIM')

	return numdoc

@auth.requires_membership('admin')
def lieto_orcamentos2(numdoc,itens):
	orcamentos2 = Orcamentos2()
	
	for item in itens:
		#numdoc = db(Pedidos.id == item.shipping_id).select().first()['numdoc']
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
	
			prod = Produtos()
			# Buscar produto banco firebird
			query = "CODPRO = {}".format(row.produto)
			produto = prod.select('CODPRO,CODINT,NOMPRO,UNIPRO', query).fetchone()
			# Buscar preco tabela banco firebird
			preco_tabela = prod.preco_tabela(produto[0])
			# calcular porcentagem de desconto do item
			pdepro = round((1-((item.valor/indice) / preco_tabela)) * 100,2)
			# verificar se existe item cadastrado
			query = "NUMDOC = {} AND CODPRO = {}".format(int(numdoc),int(produto[0]))
			existe = orcamentos2.select('*',query).fetchone()
		
			orcamentos2.numdoc = int(numdoc)
			orcamentos2.codpro = int(produto[0])
			orcamentos2.codint = str(produto[1])
			orcamentos2.nompro = produto[2].encode('UTF-8').replace("'","")
			orcamentos2.unipro = str(produto[3])
			orcamentos2.qntpro = float(item.quantidade*indice)
			orcamentos2.pdepro = float(pdepro)
			orcamentos2.preori = 0
			orcamentos2.precus = 0
			orcamentos2.prepro = prepro
			orcamentos2.enviar = 'S'
			orcamentos2.tippro = 'VND'
			orcamentos2.qntpre = 1

			if existe:
				orcamentos2.update(query)
			else:
				try:
					orcamentos2.insert()
				except:
					orcamentos2.codpro = 1679
					orcamentos2.nompro = 'PRODUTO NÃO ENCOTRADO'		
					orcamentos2.insert()
	return

@auth.requires_membership('admin')
def lieto_pedidos1(numorc):
	pedidos1 = Pedidos1()
	orcamentos1 = Orcamentos1()
	orcamentos2 = Orcamentos2()
	numdoc = (numorc*100) + 01
	
	# Buscar Orcamento
	fields = "codcli,numorc,pedcli,pedven,pdeped,pdeqnt,pdeval,pdepon,codtab,codven,porcom,codcon,codcor,codtra,codred,valfre,tipfre,datdoc,datpro,codmlb"
	query = " numdoc = {}".format(numorc)
	orcamento = orcamentos1.select(fields,query).fetchone()

	# total do orçamento 
	query = 'numdoc = {}'.format(numorc)
	total_itens = orcamentos2.select('sum(qntpro*prepro)',query).fetchone()[0]
	total = float(total_itens) + float(orcamento[15])
	
	pedidos1.numdoc = numdoc
	pedidos1.codcli = orcamento[0]
	pedidos1.numorc = numorc
	pedidos1.pedcli = orcamento[2]
	pedidos1.pedven = orcamento[3]
	pedidos1.pdeped = orcamento[4]
	pedidos1.pdeqnt = orcamento[5]
	pedidos1.pdeval = orcamento[6]
	pedidos1.pdepon = orcamento[7]
	pedidos1.codtab = orcamento[8]
	pedidos1.codven = orcamento[9]
	pedidos1.porcom = orcamento[10]
	pedidos1.codcon = orcamento[11]
	pedidos1.codcor = orcamento[12]
	pedidos1.codtra = orcamento[13]
	pedidos1.codred = orcamento[14]
	pedidos1.valfre = orcamento[15]
	pedidos1.tipfre = orcamento[16]
	pedidos1.datdoc = str(orcamento[17])
	pedidos1.datpro = str(orcamento[18])
	pedidos1.codmlb = str(orcamento[19])
	pedidos1.totped = total
	pedidos1.conimp = ''
	pedidos1.codemp = 3
	pedidos1.qntvol = 1
	pedidos1.espvol = 'VOLUMES'
	pedidos1.marvol = ''
	pedidos1.numvol = 0
	pedidos1.pesbru = 0
	pedidos1.pesliq = 0
	pedidos1.valsub = 0
	pedidos1.numnot = 0
	pedidos1.obsped = ''
	pedidos1.obsord = ''
	pedidos1.conimp = '0N' if session.full else 'N0'
	pedidos1.pedsub = 0
	pedidos1.fretra = 0
	pedidos1.pedimp = 'N'

	query = 'numdoc = {}'.format(numdoc)
	pedido = pedidos1.select('*',query).fetchone()

	if pedido:
		print 'pedido ja cadastrado'	
		#query = "NUMDOC = '%s'" %(numdoc)
		#pedidos1.update(query)
	else:
		pedidos1.insert()
		
		#Atualiza Tabela Orcamento 1
		query = "NUMDOC = '%s'" %(int(numorc))
		orcamentos1.pedimp = 'S'
		orcamentos1.sitorc = 'E'
		orcamentos1.update(query)

	return numdoc

@auth.requires_membership('admin')
def lieto_pedidos2(numdoc,numorc):

	pedidos2 = Pedidos2()
	orcamentos2 = Orcamentos2()
	produtos = Produtos()

	# buscar itens do orçamento
	fields = 'codpro,codint,nompro,unipro,qntpro,pdepro,precus,preori,prepro,tippro'
	query = 'NUMDOC = {}'.format(numorc)
	itens = orcamentos2.select(fields,query).fetchall()
	total_peso = 0
	for item in itens:

		pedidos2.numdoc = numdoc
		pedidos2.codpro = item[0]
		pedidos2.codint = item[1]
		pedidos2.nompro = item[2]
		pedidos2.unipro = item[3]
		pedidos2.qntpro = item[4]
		pedidos2.pdepro = item[5]
		pedidos2.precus = item[6]
		pedidos2.preori = item[7]
		pedidos2.prepro = item[8]
		pedidos2.tippro = item[9]

		# buscar peso na tabela de produtos
		query = 'CODPRO = {}'.format(item[0])
		peso = float(produtos.select('pesbru',query).fetchone()[0])

		total_peso = total_peso + peso

		query = 'NUMDOC = {} AND CODPRO = {}'.format(numdoc,item[0])
		existe = pedidos2.select('*',query).fetchone()
		if existe:
			pedidos2.update(query)
		else:
			pedidos2.insert()

	#Atualiza pesos na tabela pedidos1
	pedidos1 = Pedidos1()
	pedidos1.pesliq = total_peso
	pedidos1.pesbru = total_peso + 0.100
	query = 'NUMDOC = {}'.format(numdoc)
	pedidos1.update(query)
	
	return

#*************************************************

@auth.requires_membership('admin')
def receber():

	links=[dict(header='Selecionar',
	        body=lambda row: A(TAG.button(I(_class='glyphicon glyphicon-edit')),
	       _href='{}'.format(URL('receber_baixar',args=row.id))))]

	fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.numdoc,Pedidos.taxa, Pedidos.nota, Pedidos.valpag)
	
	query = (Pedidos.receber =='N') & (Pedidos.date_created >= '2020-03-01') & (Pedidos.nota != None)

	gridPedidos = grid(query,create=False, editable=False,deletable=False,formname="pedidos", links=links,
	    fields=fields,orderby = Pedidos.date_created)

	return dict(gridPedidos=gridPedidos)

@auth.requires_membership('admin')
def receber_baixar():

	idPedido = int(request.args[0])

	pedido = db(Pedidos.id == idPedido).select().first()
	itens = db(Pedidos_Itens.shipping_id == idPedido).select()

	receber = Receber()
	query = "numdoc = '{}'".format(pedido.nota)
	parcela = receber.select('codcli,valpar,datven,numide',query).fetchone()
	vencimento = parcela[2].strftime('%d.%m.%Y')


	cliente = Clientes()
	query = "codcli = {}".format(parcela[0])
	nomcli = cliente.select('nomcli',query).fetchone()[0]

	nome = '{} - {}'.format(parcela[0],nomcli)

	dados = dict(cliente=nome,valpar = "{:.2f}".format(parcela[1]),datven=parcela[2].strftime('%d/%m/%Y'))

	formReceber = SQLFORM.factory(
	Field('tarifa','decimal(7,2)', default = pedido.taxa, Label='Tarifa:'),
	Field('restou','decimal(7,2)', default = float(pedido.valor)-float(pedido.taxa), label='Mercado Pago:'),
	table_name='receber',
	submit_button='Baixar',
	)
	btnVoltar = voltar('receber')

	def validar(form):
		resultado = float(form.vars.tarifa) + float(form.vars.restou)
		if resultado != float(parcela[1]):
			form.errors.tarifa = 'a soma Tarifa + Restou deve ser igual ao valor do pedido'

	if formReceber.process(onvalidation=validar).accepted:
		recebimento = Recebimentos()

		recebimento.numide = int(recebimento.last_id())
		recebimento.iderec = parcela[3]
		recebimento.datpag = vencimento
		recebimento.valpag = formReceber.vars.tarifa
		recebimento.codcor = 21
		recebimento.obspag = ''
		recebimento.idelot = 0

		recebimento.insert()

		fluxo = Fluxo()

		fluxo.numide = int(fluxo.last_id())
		fluxo.codcor = 21
		fluxo.datdoc = vencimento
		fluxo.hordoc = "{}:{}:{}".format(str(request.now.hour).zfill(2), str(request.now.minute).zfill(2),str(request.now.second).zfill(2))
		fluxo.valdoc = formReceber.vars.tarifa
		fluxo.hisdoc = "REC. {}-01/01 de (C{}) {}".format(str(pedido.nota).zfill(7),parcela[0], nomcli.encode('UTF-8').replace("'",""))[0:60]
		fluxo.credeb = '+'
		fluxo.codpag = 0
		fluxo.origem = 'REC'
		fluxo.iderec = recebimento.numide
		fluxo.tippag = 'OUT'

		fluxo.insert()

		recebimento.numide = int(recebimento.last_id())
		recebimento.valpag = formReceber.vars.restou
		recebimento.codcor = 15

		recebimento.insert()

		fluxo.numide = int(fluxo.last_id())
		fluxo.codcor = 15
		fluxo.valdoc = formReceber.vars.restou
		fluxo.iderec = recebimento.numide

		fluxo.insert()

		query = 'numide = {}'.format(int(parcela[3]))
		receber.datpag = vencimento
		receber.valpag = float(parcela[1])

		receber.update(query)

		Pedidos[idPedido] = dict(receber = 'S')

		session.flash = 'Recebimento Baixado com sucesso...!'

		redirect(URL('receber'))
       
	return dict(formReceber=formReceber,btnVoltar=btnVoltar,dados=dados, itens = itens)

@auth.requires_membership('admin')
def importar_nota():
	query = (Pedidos.nota == None) & (Pedidos.date_created >= '2020-01-01')
	pedidos = db(query).select()
	for pedido in pedidos:
		
		try:
			pedido1 = Pedidos1()
			query = "numorc = '{}'".format(pedido.numdoc)
			nota = pedido1.select('NUMNOT',query).fetchone()[0]

			receber = Receber()
			query = "numdoc = '{}'".format(nota)
			valorBaixado = receber.select('valpag',query).fetchone()[0]

			if valorBaixado == 0:
				rec = 'N'
			else:
				rec = 'S'
			
			Pedidos[pedido.id] = dict(nota = nota,valpag = valorBaixado, receber= rec)
		except:
			pass
	return
