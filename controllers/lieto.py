# -*- coding: utf-8 -*-
import fdb

class Conexao:
	"""docstring for Conexao"""
	def __init__(self, arg):
		self.con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
		self.cur = con.cursor()
		self.tabela = '111'
		
	def inserir(self,arg):
		print self.tabela
		
class Pedido(Conexao):
	"""docstring for Pedido"""
	def __init__(self, numdoc=0):
		self.tabela = '222'
		self.numdoc = numdoc,
		self.codemp = 0,
		self.codcli = 0,
		self.datdoc = request.now.date(),
		self.datpro = request.now.date(),
		self.numorc = 0,
		self.pedcli = '',
		self.pedven = '',
		self.pdeped = 0,
		self.pdeqnt = 0,
		self.pdeval = 0,
		self.pdepon = 0,
		self.codtab = '',
		self.codven = 0,
		self.porcom = 0,
		self.codcon = 0,
		self.codcor = 0,
		self.codtra = 0,
		self.codred = 0,
		self.valfre = 0,
		self.tipfre = 0,
		self.totped = 0,
		self.qntvol = 0,
		self.espvol = '',
		self.marvol = '',
		self.numvol = 0,
		self.pesbru = 0,
		self.pesliq = 0,
		self.valsub = 0,
		self.pedimp = '',
		self.datfat = request.now.date(),
		self.numnot = 0,
		self.obsped = '',
		self.obsord = '',
		self.conimp = '',
		self.pedsub = 0,
		self.fretra = 0,

	def to_dict(self):
		return self.__dict__

class Pedido1:
	"""docstring for Pedido"""
	def __init__(self, numdoc=0):
		self.codpro = 0,
		self.codint = '',
		self.nompro = '',
		self.unipro = '',
		self.qntpro = 0,
		self.pdepro = 0,
		self.precus = 0,
		self.preori = 0,
		self.prepro = 0,
		self.tippro = '',
		self.dattro = request.now.date(),

	def to_dict(self):
		return self.__dict__

class Receber:
	"""docstring for Pedido"""
	def __init__(self, numide=0):
		self.numide = 0,
		self.numped = 0,
		self.numdoc = 0,
		self.codemp = 0,
		self.tipdoc = '',
		self.numpar = '',
		self.codcli = 0,
		self.codcor = 0,
		self.datdoc = request.now.date(),
		self.datven = request.now.date(),
		self.valpar = 0,
		self.valdes = 0,
		self.valjur = 0,
		self.datpag = 0,
		self.valpag = 0,
		self.nosnum = 0,
		self.observ = '',
		self.datenv = request.now.date(),
		self.codcar = 0,
		self.gerbol = '',
		self.sitdoc = '',
		self.idelot = 0,
		self.sernot = '',

	def to_dict(self):
		return self.__dict__


class Clientes:
	"""docstring for Clientes"""
	def __init__(self, codcli=0):
		self.nomcli = '',
		self.nomfan = '',
		self.fisjur = '',
		self.endcli = '',
		self.baicli = '',
		self.cidcli = '',
		self.estcli = '',
		self.cepcli = '',
		self.emacli = '',
		self.telcli = '',
		self.cgccpf = '',
		self.datcad = request.now.date(),
		self.datalt = request.now.date(),
		self.codven = 146,
		self.codcon = 31,
		self.codcor = 15,
		self.codtra = 273,
		self.codtip = 5,
		self.porcom = 1,
		self.pdenor = 0,
		self.numcli = '',
		self.coclci = '',
		self.regalt = 'S',
		self.emanfe = '',
		self.calsub = 'S',
		self.envpdf = 'S',
		self.retpis = 'N',
		self.retcof = 'N',
		self.regesp = '',
		self.pdeqnt = 100,

	def to_dict(self):
		return self.__dict__		

class Orcamentos1:
	"""docstring for Orcamentos1"""
	def __init__(self, numdoc=0):
		self.codemp = 3,
		self.codcli = codcli,
		self.datdoc = request.now.date(),
		self.datpro = request.now.date(),
		self.numorc = 0,
		self.pedcli = '',
		self.pedven = '',
		self.pdeped = 0,
		self.pdeqnt = 100,
		self.pdeval = 100,
		self.pdepon = 0,
		self.codtab = '',
		self.codven = 146,
		self.porcom = 2,
		self.codcon = 2,
		self.codcor = 15,
		self.codtra = 273,
		self.codred = 0,
		self.valfre = 0,
		self.tipfre = 0,
		self.pedimp = 'N',
		self.tiporc = 'P',
		self.sitorc = 'A',
		self.status = 'PEN',
		self.numlot = 0,
		self.horent = '',
		self.obsord = obsord

	def to_dict(self):
		return self.__dict__


class Orcamentos2:
	"""docstring for Orcamentos2"""
	def __init__(self, numdoc=0):
		self.codpro = 0,
		self.codint = '',
		self.nompro = '',
		self.unipro = '',
		self.qntpro = 0,
		self.pdepro = 0,
		self.precus = 0,
		self.preori = 0,
		self.prepro = 0,
		self.enviar = 'S',
		self.tippro = 'VND',
		self.qntpre = 1,

	def to_dict(self):
		return self.__dict__


def test():
	pedido = Pedido()
	pedido.inserir('teste 2')

