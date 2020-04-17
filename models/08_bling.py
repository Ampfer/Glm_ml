# -*- coding: utf-8 -*-

Vinculos = db.define_table('vinculos',
	Field('id_produto', 'string', label='Id Produto:', length = 30),
	Field('produto', 'string', label='Produto:', length = 60),
	Field('id_bling', 'string', label='Id Bling:', length = 30),
	Field('id_loja', 'string', label='Id Loja:', length = 30),
	Field('loja',	'string', label = 'Loja', length = 30),
	Field('desconto','decimal(7,2)',label='Desconto:'),
	Field('tarifa','decimal(7,2)',label='Tarifa:'),
	Field('Frete','decimal(7,2)',label='Frete:'),
	Field('preco','decimal(7,2)',label='Preço:'),
	Field('preco_promocional','decimal(7,2)',label='Promocional:'),
	Field('preco_tabela','decimal(7,2)',label='Preco Tabela:'),
    )

Vinculos.desconto.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.desconto.default = 15
Vinculos.tarifa.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.tarifa.default = 11
Vinculos.Frete.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.preco.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Vinculos.preco_promocional.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))



