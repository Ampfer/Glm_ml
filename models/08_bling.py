# -*- coding: utf-8 -*-

def sugerido(tabela,desconto,tarifa,frete):
	preco_sugerido = (tabela*(1 - desconto/100))/(1 - tarifa/100) + frete
	print round(preco_sugerido,1)
	return preco_sugerido

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
	Field.Virtual('preco_sugerido',lambda row: round(sugerido( float(row.vinculos.preco_tabela), float(row.vinculos.desconto), float(row.vinculos.tarifa), float(row.vinculos.frete)),1),label='Preco Sugerido:')
    )

Vinculos.desconto.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.desconto.default = 12
Vinculos.tarifa.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.tarifa.default = 11
Vinculos.frete.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.frete.default = 5
Vinculos.preco.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.preco_promocional.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.id_bling.writable = False
Vinculos.id_loja.writable = False




