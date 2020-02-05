STATUS_FULL = ('Em Preparação','Enviado','Concluido')

Envios_Full = db.define_table('envios_full',
	Field('codigo', 'integer', label='Código:'),
	Field('data_envio', 'date', label='Data:',requires = data),
	Field('status',	'string', label = 'Status', length = 30),
    )
Envios_Full.status.requires= IS_IN_SET(STATUS_FULL,zero=None)

Envios_Itens = db.define_table('envios_itens',
	Field('envio_id','reference envios_full', label='Envio:'),
	Field('anuncio_id','reference anuncios',label='Anuncio:',unique = True),
	Field('quantidade','decimal(7,2)',label='Quantidade:')
	)

Envios_Itens.id.readable = Envios_Itens.id.writable = False
Envios_Itens.envio_id.readable = Envios_Itens.envio_id.writable = False
Envios_Itens.quantidade.requires = notempty

Envios_Produtos = db.define_table('envios_produtos',
	Field('envio_id','reference envios_full', label='Envio:'),
	Field('produtos_id','reference produtos',label='Produto:',unique = True),
	Field('quantidade','decimal(7,2)',label='Quantidade:')
	)