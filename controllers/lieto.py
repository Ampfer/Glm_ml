#!/usr/bin/python
# -*- coding: utf-8 -*-

def teste():
	pedido = Orcamento()
	print pedido.dados.__dict__
	print pedido.itens.__dict__

def vendas_full():
	fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.numdoc,Pedidos.logistica,Pedidos.enviado)
	selectable = lambda ids: exportar_full(ids)
	query = (Pedidos.logistica == 'fulfillment') & (Pedidos.enviado == None)
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
	#orcamentos1.pedven = str(venda['id'][-8:])
	orcamentos1.codtab = str(tabela)
	orcamentos1.codven = 148
	orcamentos1.obsord = obsord
	orcamentos1.porcom = ((0.02*(float(venda.valor) - float(venda.taxa))) / float(venda.valor))*100

	numdoc = venda.numdoc or 0
	orc =  orcamentos1.buscar(numdoc)

	if orc:	
		condicao = "NUMDOC = '%s'" %(int(orc[0]))
		orcamentos1.update(condicao)
	else:
		lastId = orcamentos1.last_id() # Retorna último Id Tabela ORCAMENTOS1
		numdoc = int(lastId) + 1
		orcamentos1.numdoc = int(lastId) + 1
		orcamentos1.datdoc = str(request.now.date())
		orcamentos1.datpro = str(request.now.date())

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
			orcamentos2.preori = float(preco_tabela)
			orcamentos2.prepro = prepro

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
	fields = "codcli,numorc,pedcli,pedven,pdeped,pdeqnt,pdeval,pdepon,codtab,codven,porcom,codcon,codcor,codtra,codred,valfre,tipfre"
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
	pedidos1.datdoc = str(request.now.date())
	pedidos1.datpro = str(request.now.date())
	pedidos1.totped = total
	#pedidos1.pesbru = 0
	#pedidos1.pesliq = 0
	#pedidos1.datfat = ''
	pedidos1.numnot = 0
	#pedidos1.obsord = orcamento[16]
	pedidos1.conimp = ''

	condicao = 'numdoc = {}'.format(numdoc)
	pedido = pedidos1.select('*',condicao).fetchone()

	if pedido:
		condicao = "NUMDOC = '%s'" %(numdoc)
		pedidos1.update(condicao)
	else:
		pedidos1.insert()

	return numdoc



#*************************************************
import fdb

class Connect(object):
	"""docstring for Conexao"""
	global cur
	
	def __init__(self):
		try:
			self.con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
			self.cur = self.con.cursor()
		except:
			print "Erro ao se conectar a base de dados!"
	
	def commit(self):
		self.con.commit()
		self.con.close()

class Base(object):
	"""docstring for Conexao"""
	def insert(self):
		con = Connect()
		valores = self.__dict__.values()
		valor = ''
		for item in valores:
			valor = valor + ',' if valor != '' else ''		
			if type(item) == str or type(item) == unicode:
				valor = valor + "'%s'" %(item)
			else:
			 valor = valor + '%s' %(item)

		insere = "INSERT INTO %s (%s) VALUES (%s)" %(self.__class__.__name__.upper(),
													', '.join(self.__dict__.keys()),
													valor)
		print insere
		con.cur.execute(insere)
		con.commit()

	def update(self,condicao):
		con = Connect()
		args = ''
 		for k,v in self.__dict__.items():
 			#print type(v), k
 			args = args + ',' if args != '' else ''
 			if type(v) == str or type(v) == unicode :
 				args = args + "%s = '%s'" %(k,v)
 			else:
 				args = args + "%s = %s" %(k,v)
 					
		update = "UPDATE %s SET %s WHERE %s " %(
			self.__class__.__name__.upper(),
			args,
			condicao)

		print update

		con.cur.execute(update)
		con.commit()

	def select(self,fields,condicao):
		con = Connect()
		select = "SELECT %s FROM %s WHERE %s" %(
			fields,
			self.__class__.__name__.upper(), #Tabela 
			condicao) 
		result = con.cur.execute(select)
		return result

class Pedidos1(Base):
	"""docstring for Pedido"""
	def __init__(self):
		super(Pedidos1,self).__init__()
		self.codemp = 3
		self.codcli = 0
		self.numorc = 0
		self.pedcli = ''
		self.pedven = ''
		self.pdeped = 0
		self.pdeqnt = 0
		self.pdeval = 0
		self.pdepon = 0
		self.codtab = ''
		self.codven = 0
		self.porcom = 0
		self.codcon = 0
		self.codcor = 0
		self.codtra = 0
		self.codred = 0
		self.valfre = 0
		self.tipfre = 0
		self.totped = 0
		self.qntvol = 1
		self.espvol = 'VOLUMES'
		self.marvol = ''
		self.numvol = 0
		self.pesbru = 0
		self.pesliq = 0
		self.valsub = 0
		self.numnot = 0
		self.obsped = ''
		self.obsord = ''
		self.conimp = ''
		self.pedsub = 0
		self.fretra = 0
		self.pedimp = 'N'

class Pedidos2(Base):
	"""docstring for Pedido"""
	def __init__(self, numdoc=0):
		super(Pedidos2,self).__init__()
		self.codpro = 0
		self.codint = ''
		self.nompro = ''
		self.unipro = ''
		self.qntpro = 0
		self.pdepro = 0
		self.precus = 0
		self.preori = 0
		self.prepro = 0
		self.tippro = ''
		self.dattro = request.now.date(),

class Receber(Base):
	"""docstring for Pedido"""
	def __init__(self, numide=0):
		super(Receber,self).__init__()
		self.numide = 0
		self.numped = 0
		self.numdoc = 0
		self.codemp = 0
		self.tipdoc = ''
		self.numpar = ''
		self.codcli = 0
		self.codcor = 0
		self.datdoc = request.now.date()
		self.datven = request.now.date()
		self.valpar = 0
		self.valdes = 0
		self.valjur = 0
		self.datpag = 0
		self.valpag = 0
		self.nosnum = 0
		self.observ = ''
		self.datenv = request.now.date()
		self.codcar = 0
		self.gerbol = ''
		self.sitdoc = ''
		self.idelot = 0
		self.sernot = ''

class Clientes(Base):
	"""docstring for Clientes"""
	def __init__(self):
		self.nomcli = ''
		self.nomfan = ''
		self.fisjur = ''
		self.endcli = ''
		self.baicli = ''
		self.cidcli = ''
		self.estcli = ''
		self.cepcli = ''
		self.emacli = ''
		self.telcli = ''
		self.cgccpf = ''
		self.datalt = ''
		self.codven = 146
		self.codcon = 31
		self.codcor = 15
		self.codtra = 273
		self.codtip = 5
		self.porcom = 1
		self.pdenor = 0
		self.numcli = ''
		self.coccli = ''
		self.regalt = 'S'
		self.emanfe = ''
		self.calsub = 'S'
		self.envpdf = 'S'
		self.retpis = 'N'
		self.retcof = 'N'
		self.regesp = ''
		self.pdeqnt = 100

	def buscar_coccli(self,cidade):
		con = Connect()
		select = "select codcid from cidades where nomcid = '{}'".format(cidade)
		return con.cur.execute(select).fetchone()

	def buscar_cliente_cnpj(self,cnpj_cpf):
		con = Connect()
		select = "select codcli,datcad from clientes where cgccpf = '{}'".format(cnpj_cpf)
		return con.cur.execute(select).fetchone()
	
	def lastId(self):
		con = Connect()
		select = "select gen_id(GEN_CLIENTES, 1) from rdb$database"
		return con.cur.execute(select).fetchone()[0]

class Orcamentos1(Base):
	"""docstring for Orcamentos1"""
	def __init__(self):
		self.codemp = 3
		self.codcli = 0
		self.numorc = 0
		self.pedcli = ''
		self.pedven = ''
		self.pdeped = 0
		self.pdeqnt = 100
		self.pdeval = 100
		self.pdepon = 0
		self.codtab = ''
		self.codven = 146
		self.porcom = 2
		self.codcon = 2
		self.codcor = 15
		self.codtra = 273
		self.codred = 0
		self.valfre = 0
		self.tipfre = 0
		self.pedimp = 'N'
		self.tiporc = 'P'
		self.sitorc = 'A'
		self.status = 'PEN'
		self.numlot = 0
		self.horent = ''
		self.obsord = ''

	def buscar(self,numdoc):
		con = Connect()
		select = "select * from ORCAMENTOS1 where NUMDOC = '%s'" %(numdoc)
		return con.cur.execute(select).fetchone()

	def last_id(self):
		con = Connect()
		select = 'SELECT NUMDOC FROM ORCAMENTOS1 ORDER BY NUMDOC DESC'
		return con.cur.execute(select).fetchone()[0]
	
	def tabela(self):
		con = Connect()
		select = 'SELECT CODTAB FROM TABELA ORDER BY CODTAB DESC'
		return con.cur.execute(select).fetchone()[0]

class Orcamentos2(Base):
	"""docstring for Orcamentos2"""
	def __init__(self):
		self.codpro = 0
		self.codint = ''
		self.nompro = ''
		self.unipro = ''
		self.qntpro = 0
		self.pdepro = 0
		self.precus = 0
		self.preori = 0
		self.prepro = 0
		self.enviar = 'S'
		self.tippro = 'VND'
		self.qntpre = 1

class Produtos(Base):
	"""docstring for Orcamentos2"""
	def __init__(self):
		self.nompro = ''

	def preco_tabela(self,codpro):
		con = Connect()
		select = 'SELECT PREPRO FROM TABELA WHERE CODPRO = {} ORDER BY CODTAB DESC'.format(codpro)
		return con.cur.execute(select).fetchone()[0]





