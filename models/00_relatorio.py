Relatorio = db.define_table('relatorio',
                            Field('datarel','date',label ='Data'),
                            Field('codigo','string',label='Código',length=7),
                            Field('descricao','string',label='Descrição'),
                            Field('unidade','string',label='Unidade',length=4),
                            Field('etapa','string',label='Etapa',length=30),
                            Field('quantidade','decimal(9,4)',label='Quantidade'),
                            Field('valor','decimal(7,2)',label='Valor'),
                            Field('total','decimal(7,2)',label='Total'),
                            Field('porcentagem','decimal(7,2)',label='%'),
                            Field('acumulado','decimal(7,2)',label='Acumulado')
                            )
Relatorio.quantidade.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.porcentagem.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.acumulado.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.total.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.datarel.requires = data
Relatorio.datarel.represent = lambda value, row: value.strftime("%d/%m/%Y")

Emails = db.define_table('email',
    Field('email','string',label='Email:',length=100),
    Field('assunto','string',label='Assunto:',length=100),
    Field('mensagem','text',label='Mensagem:'),
    Field('anexo','string',label='Anexo:',length=20)
    )
Emails.email.requires=IS_NOT_EMPTY()
Emails.assunto.requires=IS_NOT_EMPTY()
Emails.mensagem.requires=IS_NOT_EMPTY()