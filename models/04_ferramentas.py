# -*- coding: utf-8 -*-

Importar_Produtos = db.define_table('importar_produtos',
	Field('codigo','string',label='Código:',length=10),
	Field('nome', 'string', label='Descrição:', length=100),
    Field('marca', 'string', label='Marca:', length=30),
    Field('preco','decimal(7,2)',label='Preço'),
    Field('estoque','decimal(7,2)',label='Estoque'),
    Field('ean','string',label='Ean:',length=13)
    )