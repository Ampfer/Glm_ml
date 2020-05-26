# -*- coding: utf-8 -*-

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
		#print insere
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

		#print update

		con.cur.execute(update)
		con.commit()

	def select(self,fields,condicao,complemento=''):
		con = Connect()
		select = "SELECT %s FROM %s WHERE %s %s" %(
			fields,
			self.__class__.__name__.upper(), #Tabela 
			condicao,
			complemento) 
		#print select
		result = con.cur.execute(select)
		return result

class Pedidos1(Base):
	"""docstring for Pedido"""
	def __init__(self):
		pass

class Pedidos2(Base):
	"""docstring for Pedido"""
	def __init__(self):
		pass

class Receber(Base):
	"""docstring for Pedido"""
	def __init__(self):
		pass
		'''
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
		'''

class Clientes(Base):
	"""docstring for Clientes"""
	def __init__(self):
		pass

	def buscar_coccli(self,cidade):
		con = Connect()
		select = "select codcid from cidades where nomcid = '{}'".format(cidade)
		return con.cur.execute(select).fetchone()[0]

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
		pass

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
		pass

class Produtos(Base):
	"""docstring for Orcamentos2"""
	def __init__(self):
		pass

	def preco_tabela(self,codpro):
		con = Connect()
		select = 'SELECT PREPRO FROM TABELA WHERE CODPRO = {} ORDER BY CODTAB DESC'.format(codpro)
		return con.cur.execute(select).fetchone()[0]

class Lotes(Base):
	"""docstring for Orcamentos2"""
	def __init__(self):
		pass

	def last_id(self):
		con = Connect()
		select = 'SELECT NUMIDE FROM LOTES ORDER BY NUMIDE DESC'
		return con.cur.execute(select).fetchone()[0]

class Recebimentos(Base):
	"""docstring for Orcamentos2"""
	def __init__(self):
		pass
	
	def last_id(self):
		con = Connect()
		select = "select gen_id(GEN_RECEBIMENTOS, 1) from rdb$database"
		return con.cur.execute(select).fetchone()[0]

class Fluxo(Base):
	"""docstring for Orcamentos2"""
	def __init__(self):
		pass
	
	def last_id(self):
		con = Connect()
		select = "select gen_id(GEN_FLUXO, 1) from rdb$database"
		return con.cur.execute(select).fetchone()[0]
