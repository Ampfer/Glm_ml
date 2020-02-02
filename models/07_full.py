STATUS_FULL = ('Em Preparação','Enviado','Concluido')

Envios_Full = db.define_table('envios_full',
	Field('codigo', 'integer', label='Código:'),
	Field('data_envio', 'date', label='Data:',requires = data),
	Field('status',	'string', label = 'Status', length = 30),
    )
Envios_Full.status.requires= IS_IN_SET(STATUS_FULL,zero=None)