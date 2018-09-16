# -*- coding: utf-8 -*-

Clientes = db.define_table('clientes',
	Field('nome','string',label='Nome:',length=60),
	Field('cnpj_cpf','string',label='CNPJ/CPF:',length=20),
	Field('tipo','string',label='Tipo:',length=04),
	Field('ie_rg','string',label='I.E./RG:',length=20),	
	Field('endereco','string',label='Endereço:',length=60),
	Field('bairro','string',label='Bairro:',length=40),
	Field('cidade','string',label='Cidade:',length=40),
	Field('estado','string',label='Estado:',length=2),
	Field('cep','string',label='Cep:',length=9),
    Field('fone','string',label='Fone:',length=30),
    Field('email','string',label='Email:',length=50),
    Field('apelido','string',label='CEP:',length=60),
	)
Clientes.id.label = 'Código'

Pedidos = db.define_table('pedidos',
	Field('buyer_id', 'reference clientes', label='Id Cliente:', length=20),
	Field('date_created', 'date', label='Data:', length=20),
    )

Pedidos_Itens = db.define_table('pedidos_itens',
	Field('shipping_id','string',label='Id Pedido:',length=20),
	Field('item','string', label='Item:',length=60),
	Field('item_id','string', label='Item:',length=30),
	Field('quantidade','integer',label='quantidade:'),
	Field('valor','decimal(7,2)',label='Valor:'),
	Field('taxa','decimal(7,2)',label='Taxa:'),
	Field('frete','decimal(7,2)',label='Frete:'),
	)