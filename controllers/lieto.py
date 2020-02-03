#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs

#ERPFDB = "D:/lieto/Dados/ERP.FDB"
#SERVERNAME = "localhost"

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
				fluxo.hisdoc = "REC. {}-{} de (C{}) {}".format(boleto['documento'],rec[1],boleto['codigo'], boleto['cliente'])[0:60]
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
		condicao = 'numdoc = {}'.format(row[0])
		try:
			total_itens = orcamentos2.select('sum(qntpro*prepro)',condicao).fetchone()[0]
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
		
def vendas_full():
	fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.numdoc,Pedidos.logistica,Pedidos.enviado)
	selectable = lambda ids: exportar_full(ids)
	query = (Pedidos.logistica == 'fulfillment') & (Pedidos.enviado == None)
	#query = (Pedidos.logistica == 'fulfillment')
	gridPedidos = grid(query,create=False, editable=False,deletable=False,formname="pedidos",
		fields=fields,orderby =~ Pedidos.date_created,selectable=selectable,selectable_submit_button='Exportar Pedidos',)
        
	gridPedidos = DIV(gridPedidos, _class="well")

	return dict(gridPedidos=gridPedidos)

def exportar_full(ids):
	orcamentos = db(Pedidos.id.belongs(ids)).select()
	for orcamento in orcamentos:
		cliente_ml = db(db.clientes.id == orcamento.buyer_id).select().first()
		lieto_clientes(cliente_ml)
		numorc = lieto_orcamentos1(orcamento)
		itens = db(Pedidos_Itens.shipping_id.belongs(ids)).select()
		lieto_orcamentos2(itens)
		numdoc = lieto_pedidos1(numorc)
		lieto_pedidos2(numdoc,numorc)

	session.flash = "Pedido Importado com Sucesso....!"

def lieto_clientes(cliente_ml):
	cliente = Clientes()
	cliente.nomcli = cliente_ml.nome[:50].upper().decode('utf-8')
	cliente.nomfan = cliente_ml.apelido[:30].upper().decode('utf-8')
	cliente.fisjur = 'J' if cliente_ml.tipo == 'CNPJ' else 'F'
	cliente.endcli = cliente_ml.endereco[:50].upper().decode('utf-8')
	cliente.baicli = cliente_ml.bairro[:35].upper().decode('utf-8') if cliente_ml.bairro else 'CENTRO'
	cliente.cidcli = (cliente_ml.cidade[:35].upper()).decode('utf-8')
	cliente.estcli = buscar_uf(cliente_ml.estado).decode('utf-8')
	cliente.cepcli = '{}-{}'.format(cliente_ml.cep[:5],cliente_ml.cep[-3:])
	cliente.emacli = cliente_ml.email[:40]
	cliente.telcli = cliente_ml.fone if cliente_ml.fone else ' '
	cliente.cgccpf = cliente_ml.cnpj_cpf
	cliente.numcli = cliente_ml.numero
	cliente.datalt = '{}'.format(request.now.date())
	cliente.coccli = cliente_ml.codcid if cliente_ml.codcid else cliente.buscar_coccli(cliente.cidcli)
	cliente.emanfe = cliente_ml.email
	cliente.codven = 146
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
		condicao = "CGCCPF = '%s'" %(cliente_ml.cnpj_cpf)
		cliente.update(condicao)		
	else:
		cliente.codcli = int(cliente.lastId())
		cliente.datcad = '%s' %(request.now.date())
		cliente.insert()

	return 

def lieto_orcamentos1(venda):
	orcamentos1 = Orcamentos1()
	venda_itens = db(db.pedidos_itens.shipping_id  == venda.id).select()

	# Retorna última Tabela de Preços
	tabela = orcamentos1.tabela()
	# Retorna Id do Cliente
	cnpj_cpf = db(db.clientes.id == venda.buyer_id).select(db.clientes.cnpj_cpf).first()['cnpj_cpf']
	cliente = Clientes()
	codcli = cliente.buscar_cliente_cnpj(cnpj_cpf)[0]

	obsord = """
	Total Mercado Livre: {}
	Tarifas: {}
	""".format(venda.valor,venda.taxa)

	orcamentos1.codcli = codcli
	orcamentos1.pedven = ''
	orcamentos1.codtab = str(tabela)
	orcamentos1.codven = 148
	orcamentos1.obsord = obsord
	orcamentos1.porcom = ((0.02*(float(venda.valor) - float(venda.taxa))) / float(venda.valor))*100
	orcamentos1.codemp = 3
	orcamentos1.numorc = 0
	orcamentos1.pedcli = ''
	orcamentos1.pdeped = 0
	orcamentos1.pdeqnt = 0
	orcamentos1.pdeval = 0
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

	numdoc = venda.numdoc or 0
	orc =  orcamentos1.buscar(numdoc)

	if orc:	
		condicao = "NUMDOC = '%s'" %(int(orc[0]))
		orcamentos1.update(condicao)
	else:
		lastId = orcamentos1.last_id() # Retorna último Id Tabela ORCAMENTOS1
		numdoc = int(lastId) + 1
		orcamentos1.numdoc = int(lastId) + 1
		#orcamentos1.datdoc = str(request.now.date())
		#orcamentos1.datpro = str(request.now.date())
		orcamentos1.datdoc = str(venda.date_created)
		orcamentos1.datpro = str(venda.date_created)

		orcamentos1.insert()

		Pedidos[venda.id] = dict(numdoc = int(lastId) + 1, enviado='SIM')

	return numdoc

def lieto_orcamentos2(itens):
	orcamentos2 = Orcamentos2()
	
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
	
			prod = Produtos()
			# Buscar produto banco firebird
			condicao = "CODPRO = {}".format(row.produto)
			produto = prod.select('CODPRO,CODINT,NOMPRO,UNIPRO', condicao).fetchone()
			# Buscar preco tabela banco firebird
			preco_tabela = prod.preco_tabela(produto[0])
			# calcular porcentagem de desconto do item
			pdepro = round((1-((item.valor/indice) / preco_tabela)) * 100,2)
			# verificar se existe item cadastrado
			condicao = "NUMDOC = {} AND CODPRO = {}".format(int(numdoc),int(produto[0]))
			existe = orcamentos2.select('*',condicao).fetchone()
		
			orcamentos2.numdoc = int(numdoc)
			orcamentos2.codpro = int(produto[0])
			orcamentos2.codint = str(produto[1])
			orcamentos2.nompro = produto[2].encode('UTF-8')
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
				orcamentos2.update(condicao)
			else:
				try:
					orcamentos2.insert()
				except:
					orcamentos2.codpro = 1679
					orcamentos2.nompro = 'PRODUTO NÃO ENCOTRADO'		
					orcamentos2.insert()
	return

def lieto_pedidos1(numorc):
	pedidos1 = Pedidos1()
	orcamentos1 = Orcamentos1()
	orcamentos2 = Orcamentos2()
	numdoc = (numorc*100) + 01
	
	# Buscar Orcamento
	fields = "codcli,numorc,pedcli,pedven,pdeped,pdeqnt,pdeval,pdepon,codtab,codven,porcom,codcon,codcor,codtra,codred,valfre,tipfre,datdoc,datpro"
	condicao = " numdoc = {}".format(numorc)
	orcamento = orcamentos1.select(fields,condicao).fetchone()

	# total do orçamento 
	condicao = 'numdoc = {}'.format(numorc)
	total_itens = orcamentos2.select('sum(qntpro*prepro)',condicao).fetchone()[0]
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
	pedidos1.totped = total
	#pedidos1.datfat = ''
	#pedidos1.numnot = 0
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
	pedidos1.conimp = 'ON'
	pedidos1.pedsub = 0
	pedidos1.fretra = 0
	pedidos1.pedimp = 'N'



	condicao = 'numdoc = {}'.format(numdoc)
	pedido = pedidos1.select('*',condicao).fetchone()

	if pedido:
		condicao = "NUMDOC = '%s'" %(numdoc)
		pedidos1.update(condicao)
	else:
		pedidos1.insert()

	return numdoc

def lieto_pedidos2(numdoc,numorc):

	pedidos2 = Pedidos2()
	orcamentos2 = Orcamentos2()
	produtos = Produtos()

	# buscar itens do orçamento
	fields = 'codpro,codint,nompro,unipro,qntpro,pdepro,precus,preori,prepro,tippro'
	condicao = 'NUMDOC = {}'.format(numorc)
	itens = orcamentos2.select(fields,condicao).fetchall()
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
		condicao = 'CODPRO = {}'.format(item[0])
		peso = float(produtos.select('pesbru',condicao).fetchone()[0])

		total_peso = total_peso + peso

		condicao = 'NUMDOC = {} AND CODPRO = {}'.format(numdoc,item[0])
		existe = pedidos2.select('*',condicao).fetchone()
		if existe:
			pedidos2.update(condicao)
		else:
			pedidos2.insert()

	#Atualiza pesos na tabela pedidos1
	pedidos1 = Pedidos1()
	pedidos1.pesliq = total_peso
	pedidos1.pesbru = total_peso + 0.100
	condicao = 'NUMDOC = {}'.format(numdoc)
	pedidos1.update(condicao)
	
	#Atializa Tabela Orcamento 1
	orcamentos1 = Orcamentos1()
	orcamentos1.pedimp = 'S'
	orcamentos1.sitorc ='E'
	condicao = 'NUMDOC = {}'.format(numorc)
	orcamentos1.update(condicao)

	return

#*************************************************
