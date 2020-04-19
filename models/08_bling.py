# -*- coding: utf-8 -*-

LOJAS = ['Amazon', 'Magalu', 'Olist']

def sugerido_multiloja(loja,tabela,desconto,tarifa,frete):
	#preco_sugerido = 0
	preco_sugerido = (float(tabela)*(1 - float(desconto)/100))/(1 - float(tarifa)/100) + float(frete)

	return round(preco_sugerido,1)

Vinculos = db.define_table('vinculos',
	Field('id_produto', 'string', label='Id Produto:', length = 30),
	Field('produto', 'string', label='Produto:', length = 60),
	Field('id_bling', 'string', label='Id Bling:', length = 30),
	Field('id_loja', 'string', label='Id Loja:', length = 30),
	Field('loja', 'string', label = 'Loja', length = 30),
	Field('desconto','decimal(7,2)',label='Desconto:'),
	Field('tarifa','decimal(7,2)',label='Tarifa:'),
	Field('frete','decimal(7,2)',label='Frete:'),
	Field('preco','decimal(7,2)',label='Preço:'),
	Field('preco_promocional','decimal(7,2)',label='Promocional:'),
	Field('preco_tabela','decimal(7,2)',label='Preco Tabela:'),
	Field.Virtual('preco_sugerido',lambda row: sugerido_multiloja(row.vinculos.loja,
		row.vinculos.preco_tabela,
		row.vinculos.desconto,
		row.vinculos.tarifa, 
		row.vinculos.frete, 
		),label='Preco Sugerido:')
    )

Vinculos.desconto.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.desconto.default = 12
Vinculos.tarifa.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.frete.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.preco.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.preco_promocional.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.id_bling.writable = False
Vinculos.id_loja.writable = False
Vinculos.loja.requires = IS_IN_SET(LOJAS,zero=None)




