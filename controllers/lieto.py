#!/usr/bin/python
# -*- coding: utf-8 -*-

def teste():
	pedido = Orcamento()
	print pedido.dados.__dict__
	print pedido.itens.__dict__

def vendas_full():
	fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.numdoc,Pedidos.logistica,Pedidos.enviado)
	selectable = lambda ids: exportar_full(ids)
	gridPedidos = grid(Pedidos.logistica == 'fulfillment',create=False, editable=False,deletable=False,formname="pedidos",
		fields=fields,orderby =~ Pedidos.date_created,selectable=selectable,selectable_submit_button='Exportar Pedidos',)
        
	gridPedidos = DIV(gridPedidos, _class="well")

	return dict(gridPedidos=gridPedidos)

def exportar_full(ids):
	orcamentos = db(Pedidos.id.belongs(ids)).select()
	for orcamento in orcamentos:
		cliente_ml = db(db.clientes.id == orcamento.buyer_id).select().first()
		#lieto_cliente(cliente_ml)
		lieto_orcamento(orcamento)

	msg = """
	{}
	Pedido atualizado
	 com sucesso....!
	""".format(session.msg)

	session.flash = msg

def lieto_cliente(cliente_ml):
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

	session.msg = 'Cliente atualizado com sucesso....!'

	return 

def lieto_orcamento(venda):
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
	#orcamentos1.pedven = str(venda_itens['id'][-8:])
	orcamentos1.codtab = str(tabela)
	orcamentos1.codven = 148
	orcamentos1.obsord = obsord

	numdoc = venda.numdoc or 0
	orc =  orcamentos1.buscar(numdoc)

	if orc:	
		orcamentos1.update(int(orc[0]))
	else:
		lastId = orcamentos1.last_id() # Retorna último Id Tabela ORCAMENTOS1
		orcamentos1.numdoc = int(lastId) + 1
		orcamentos1.datdoc = str(request.now.date())
		orcamentos1.datpro = str(request.now.date())

		orcamentos1.insert()

		Pedidos[venda.id] = dict(numdoc = int(lastId) + 1, enviado='SIM')

	return

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

class Pedidos1(Base):
	"""docstring for Pedido"""
	def __init__(self):
		super(Pedidos1,self).__init__()
		self.codemp = 0
		self.codcli = 0
		#self.datdoc = request.now.date()
		#self.datpro = request.now.date()
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
		self.qntvol = 0
		self.espvol = ''
		self.marvol = ''
		self.numvol = 0
		self.pesbru = 0
		self.pesliq = 0
		self.valsub = 0
		self.pedimp = ''
		self.datfat = ''
		self.numnot = 0
		self.obsped = ''
		self.obsord = ''
		self.conimp = ''
		self.pedsub = 0
		self.fretra = 0

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





