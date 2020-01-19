# -*- coding: utf-8 -*-

class Pedido:
	"""docstring for Pedido"""
	def __init__(self, numdoc=0):
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


def test():
	pedido = Pedido(3)
	pedido.numdoc = 100
	pedido.codcli = 2
	pedido.codemp = 3
	print '*********************************************'
	print pedido.to_dict().values()

