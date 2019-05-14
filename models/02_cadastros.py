# -*- coding: utf-8 -*-
data = IS_NULL_OR(IS_DATE(format=T("%d/%m/%Y")))
notempty=IS_NOT_EMPTY(error_message='Campo Obrigatório')
ATRIBUTO = ('Medidas','Tamanho','Modelo','Voltagem','Cor')
CATALOGO = {'S':"Sim","N":"Não"}
Estados = {'SP':'São Paulo','RJ':'Rio de Janeiro','MG':'Minas Gerais','RS':'Rio Grande do Sul','SC':'Santa Catarina','PR':'Paraná'}

Empresa = db.define_table('empresa',
    Field('nome','string',label='Nome:',length=60),
    Field('desconto','decimal(7,2)',label='Desconto Frete'),
    Field('premium','decimal(7,2)',label='Tarifa Premium'),
    Field('classico','decimal(7,2)',label='Tarifa Clássico'),
    Field('token1','string',label='Token acesso:'),
    Field('token2','string',label='Token atualizar:'),
    )
Empresa.desconto.requires = IS_DECIMAL_IN_RANGE(dot=',')

Marcas = db.define_table('marcas',
    Field('marca', 'string', label='Marca:', length=30),
    Field('logo','string',label='logo:',length=100),
    format='%(marca)s',
    )

Descricoes = db.define_table('descricoes',
    Field('descricao','text',label='Descrição:')
    )

Imagens = db.define_table('imagens',
    Field('imagem','upload'),
    )
Imagens.imagem.requires = notempty


Produtos = db.define_table('produtos',
    Field('nome', 'string', label='Descrição:', length=100),
    Field('familia','integer'),
    Field('atributo', 'string', label='Atributo:', length=20),
    Field('variacao', 'string', label='Variação:', length=30),
    Field('marca', 'string', label='Marca:', length=30),
    Field('preco','decimal(7,2)',label='Preço'),
    Field('estoque','decimal(7,2)',label='Estoque'),
    Field('ean','string',label='Ean:',length=13),
    Field('variacao_id','string', label='Id Variação:', length=20),
    Field('peso','decimal(7,3)',label='Peso'),
    Field('origem','string',label='Origem',length=1),
    Field('ncm', 'string', label='NCM:', length=8),
    Field('largura','decimal(7,3)',label='Largura'),
    Field('altura','decimal(7,3)',label='Altura'),
    Field('comprimento','decimal(7,3)',label='Comprimento'),
    Field('descricao','reference descricoes', label='Descrição:'),
    format='%(nome)s',
    )
Produtos.preco.requires = IS_DECIMAL_IN_RANGE(dot=',')
Produtos.estoque.requires = IS_DECIMAL_IN_RANGE(dot=',')
Produtos.peso.requires = IS_DECIMAL_IN_RANGE(dot=',')
Produtos.altura.requires = IS_DECIMAL_IN_RANGE(dot=',')
Produtos.largura.requires = IS_DECIMAL_IN_RANGE(dot=',')
Produtos.comprimento.requires = IS_DECIMAL_IN_RANGE(dot=',')
Produtos.nome.requires = IS_UPPER()
Produtos.atributo.requires= IS_IN_SET(ATRIBUTO,zero=None)
#Produtos.familia.requires = IS_EMPTY_OR(IS_IN_DB(db,'familias.id','%(nome)s'))
#Produtos.familia.widget = SQLFORM.widgets.autocomplete(request, Familias.nome, id_field=Familias.id,
#                     limitby=(0,10), min_length=0, orderby=Familias.nome, at_beginning=False,
#                     )
                     #help_fields=[Familias.nome,Familias.id], help_string= '%(id)s - %(nome)s '

Produtos_Imagens = db.define_table('produtos_imagens',
    Field('produto', 'reference produtos'),
    Field('imagem','reference imagens'),
    )

Familias = db.define_table('familias',
    Field('codigo', 'integer', label='Código:'),
    Field('nome', 'string', label='Nome:', length=60),
    Field('nome_catalogo', 'string', label='Nome Catálogo:', length=60),
    Field('marca', 'reference marcas', label='Marca:', ondelete='SET NULL'),
    Field('descricao','reference descricoes', label='Descrição:'),
    Field('atributos','string', label='Atributos:', length=100),
    Field('imagem','string',label='Imagem Destacada', length=50),
    Field('catalogo','string',label='Catálogo:', length=1),
    Field('web','string',label='web:', length=1),
    format='%(nome)s',
    )
Familias.descricao.writable = Familias.descricao.readable =  False
Familias.catalogo.requires = IS_IN_SET(CATALOGO,zero=None)
Familias.web.requires = IS_IN_SET(CATALOGO,zero=None)

Familias_Imagens = db.define_table('familias_imagens',
    Field('familia', 'reference familias'),
    Field('imagem','reference imagens'),
    )
Familias_Produtos = db.define_table('familias_produtos',
    Field('familia','reference familias'),
    Field('produto','reference produtos'),
    )


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

Atributos = db.define_table('atributos',
    Field('atributo_id','string', label='Id Atributo:', length=50),
    Field('nome','string', label='Nome:', length=50),
    format='%(nome)s',
    )


