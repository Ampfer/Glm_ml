# -*- coding: utf-8 -*-

notempty=IS_NOT_EMPTY(error_message='Campo Obrigatório')
ATRIBUTO = ('Medida','Tamanho','Modelo','Tensão','Cor')

Clientes = db.define_table('clientes',
	Field('nome','string',label='Nome:',length=60),
	Field('cnpj_cpf','string',label='CNPJ/CPF:',length=20),
	Field('ie_rg','string',label='I.E./RG:',length=20),	
	Field('endereco','string',label='Endereço:',length=60),
	Field('bairro','string',label='Bairro:',length=40),
	Field('cidade','string',label='Cidade:',length=40),
	Field('estado','string',label='Estado:',length=2),
	Field('cep','string',label='Cep:',length=9),        Field('cep','string',label='Cep:',length=9),
    Field('fone','string',label='Fone:',length=30),
    Field('email','string',label='Email:',length=50),
	)
Clientes.id.label = 'Código'
Clientes.nome.requires = notempty

Marcas = db.define_table('marcas',
    Field('marca', 'string', label='Marca:', length=30),
    Field('logo','string',label='logo:',length=100),
    format='%(marca)s',
    )

Descricoes = db.define_table('descricoes',
    Field('descricao','text',label='Descrição:')
    )

Imagens = db.define_table('imagens',
    Field('imagem','upload')
    )
Imagens.imagem.requires = notempty

Familias = db.define_table('familias',
    Field('codigo', 'integer', label='Código:'),
    Field('nome', 'string', label='Nome:', length=60),   
    Field('marca', 'reference marcas', label='Marca:', ondelete='SET NULL'),
    Field('descricao','reference descricoes', label='Descrição:'),
    Field('atributos','string', label='Atributos:', length=100),
    Field('imagem','string',label='Imagem Destacada', length=50),

    format='%(nome)s',
    )

Familias_Imagens = db.define_table('familias_imagens',
    Field('familia', 'reference familias'),
    Field('imagem','reference imagens'),
    )

Produtos = db.define_table('produtos',
    Field('nome', 'string', label='Descrição:', length=100),
    Field('familia','integer'),
    Field('atributo', 'string', label='Atributo:', length=20),
    Field('variacao', 'string', label='Variação:', length=30),
    Field('marca', 'string', label='Marca:', length=30),
    Field('preco','decimal(7,2)',label='Preço'),
    Field('estoque','decimal(7,2)',label='Estoque'),
    format='%(nome)s',
    )
Produtos.preco.requires = IS_DECIMAL_IN_RANGE(dot=',')
Produtos.estoque.requires = IS_DECIMAL_IN_RANGE(dot=',')
Produtos.nome.requires = IS_UPPER()
Produtos.atributo.requires= IS_IN_SET(ATRIBUTO,zero=None)
Produtos.familia.requires = IS_EMPTY_OR(IS_IN_DB(db,'familias.id','%(nome)s'))
Produtos.familia.widget = SQLFORM.widgets.autocomplete(request, Familias.nome, id_field=Familias.id,
                     limitby=(0,10), min_length=0, orderby=Familias.nome, at_beginning=False,
                     )
                     #help_fields=[Familias.nome,Familias.id], help_string= '%(id)s - %(nome)s '
def buscaProduto(id):
    if not id:
        raise HTTP(404, 'ID produto não encontrado')
    try:
        produto = db(db.produtos.id == id).select().first()
    except ValueError:
        raise HTTP(404, 'Argumento Produto inválido')
    if not produto:
        raise HTTP(404, 'Produto não encontrado')
    return produto


