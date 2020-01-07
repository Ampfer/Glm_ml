# -*- coding: utf-8 -*-
from decimal import *

Clientes = db.define_table('clientes',
	Field('nome','string',label='Nome:',length=60),
	Field('cnpj_cpf','string',label='CNPJ/CPF:',length=20),
	Field('tipo','string',label='Tipo:',length=04),
	Field('endereco','string',label='Endereço:',length=60),
	Field('numero','string',label='Numero:',length=10),
	Field('bairro','string',label='Bairro:',length=40),
	Field('cidade','string',label='Cidade:',length=40),
	Field('estado','string',label='Estado:',length=30),
	Field('codcid','string',label='Estado:',length=20),
	Field('cep','string',label='Cep:',length=9),
    Field('fone','string',label='Fone:',length=30),
    Field('email','string',label='Email:',length=100),
    Field('apelido','string',label='Apelido:',length=60),
    format='%(nome)s',
	)
Clientes.id.label = 'Código'

def totalCompra(row):
	try:
		itens= db(Pedidos_Itens.shipping_id == int(row.pedidos.id)).select()
	except:
		itens=[]
	valorCompra = 0
	for item in itens:
		valorCompra += (item.quantidade * item.valor).quantize(Decimal('1.00'), rounding=ROUND_DOWN)
	return valorCompra

def totalTaxas(row):
	try:
		itens= db(Pedidos_Itens.shipping_id == int(row.pedidos.id)).select()
	except:
		itens=[]
	valorTaxa = 0
	for item in itens:
		valorTaxa += item.taxa
	return valorTaxa


Pedidos = db.define_table('pedidos',
	Field('buyer_id', 'reference clientes', label='Cliente:', length=20),
	Field('date_created', 'date', label='Data:', length=20,requires = data),
	Field.Virtual('valor',lambda row: totalCompra(row), label='Valor:'),
	Field.Virtual('taxa',lambda row: totalTaxas(row), label='Valor:'),
	Field('status', 'string', label='Status:', length=30),
	Field('logistica', 'string', label='Logistica:', length=30),
	Field('numdoc', 'integer', label='Docto:'),
	Field('enviado', 'string', label='Enviado:', length=3),
	Field('total','decimal(7,2)',label='Total:'),
    )

Pedidos_Itens = db.define_table('pedidos_itens',
	Field('shipping_id','reference pedidos',label='Id Pedido:',length=20),
	Field('payments_id','string',label='Id Pedido:',length=50),
	Field('item','string', label='Item:',length=60),
	Field('item_id','string', label='Item:',length=30),
	Field('logistica', 'string', label='Logistica:', length=30),
	Field('quantidade','integer',label='quantidade:'),
	Field('valor','decimal(7,2)',label='Valor:'),
	Field('taxa','decimal(7,2)',label='Taxa:'),
	Field('frete','decimal(7,2)',label='Frete:'),
	)