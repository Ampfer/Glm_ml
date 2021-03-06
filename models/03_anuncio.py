# -*- coding: utf-8 -*-

notempty=IS_NOT_EMPTY(error_message='Campo Obrigatório')
TIPOANUNCIO = {'gold_pro':'Premium','gold_special':'Clássico'}
STATUS = {'active':'Ativo','paused':'Pausado'}
FORMA = ('Individual','Multiplos','Kit','Pack')
FRETE = {'comprador':'Por conta do Comprador','gratis':'Frete Grátis'}
LOCALIZACAO = ['MATRIZ', 'FULL']

Categorias = db.define_table('categorias',
    Field('categoria','string',label='Categoria:',length=100),
    Field('categoria_id','string',label='Id Categoria',length=30),
    Field('frete','decimal(7,2)',label='Valor do Frete'),
    Field('qtde_anuncios','integer',label='Quantidade de Anuncios'),
    )
Categorias.categoria.requires  = notempty
Categorias.categoria_id.requires = notempty
Categorias.frete.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))

Categorias_Bling = db.define_table('categorias_bling',
    Field('categoria','string',label='Categoria:',length=100),
    Field('pai_id','integer',label='Valor do Frete'),
    )

Anuncios = db.define_table('anuncios',
    Field('familia', 'reference familias'),
    Field('titulo', 'string', label='Título:', length=60),
    Field('item_id', 'string', label='ID do Anuncio:', length=30),
    Field('categoria', 'string',label='Categoria:', length=30),
    Field('preco','decimal(7,2)',label='Preço'),
    Field('desconto','decimal(7,2)',label='Desconto'),
    Field('estoque','decimal(7,2)',label='Estoque'),
    Field('frete','string',label='Frete:',length=30),
    Field('fretegratis','decimal(7,2)',label='Valor Frete Grátis'),
    Field('tipo','string',label='Tipo:', length=30),
    Field('garantia','string',label='Garantia',length=100),
    Field('status','string',label='Status:',length=30),
    Field('forma','string',label='Forma:',length=30),
    Field('localizacao','string',label='Localização:',length=30),
    Field('alterado','string',label='Alterado:',length=1),
    Field('preco_alterado','string',label='Preço Alterado:',length=1),
    Field('descricao','reference descricoes', label='Descrição:'),
    Field('vendido','integer'),
    Field('qtevar','integer'),
    Field('bling','boolean'),

    format='%(titulo)s'
    )
Anuncios.titulo.requires = [notempty,IS_LENGTH(60)]
Anuncios.preco.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Anuncios.desconto.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Anuncios.estoque.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Anuncios.tipo.requires = IS_IN_SET(TIPOANUNCIO,zero=None)
Anuncios.localizacao.requires = IS_IN_SET(LOCALIZACAO,zero=None)
Anuncios.tipo.represent = lambda tipo, row: TIPOANUNCIO[tipo]
Anuncios.frete.requires = IS_IN_SET(FRETE,zero=None)
#Anuncios.fretegratis.writable = Anuncios.fretegratis.readable = False
Anuncios.categoria.requires = IS_IN_DB(db,"categorias.categoria_id",'%(categoria)s',)
Anuncios.status.requires = IS_IN_SET(STATUS,zero=None)
Anuncios.status.represent = lambda status, row: STATUS[status]
Anuncios.forma.requires = IS_IN_SET(FORMA,zero=None)
Anuncios.bling.default = False
Anuncios.preco_alterado.writable = False
Anuncios.alterado.writable = False

Anuncios_Produtos = db.define_table('anuncios_produtos',
    Field('anuncio', 'reference anuncios'),
    Field('produto', 'reference produtos'),
    Field('quantidade', 'integer',label='Qtde'),
    Field('variacao_id','string', label='Id Variação:', length=20),
    Field('imagens_ids','list:string'),
    Field.Virtual('preco_sugerido',lambda row: round(sugerido(Anuncios[int(row.anuncios_produtos.anuncio)],int(row.anuncios_produtos.produto)),1))
    )
Anuncios_Atributos = db.define_table('anuncios_atributos',
    Field('anuncio', 'reference anuncios'),
    Field('atributo', 'reference atributos'),
    Field('valor', 'string',label='Valor:',length=50),
    )
Anuncios_Atributos.atributo.requires = IS_IN_DB(db,"atributos.id",'%(nome)s',)

Anuncios_Imagens = db.define_table('anuncios_imagens',
    Field('anuncio', 'reference anuncios'),
    Field('imagem','reference imagens'),
    Field('imagem_id','string',length='50')
    )



