# -*- coding: utf-8 -*-
data = IS_NULL_OR(IS_DATE(format=T("%d/%m/%Y")))
notempty=IS_NOT_EMPTY(error_message='Campo Obrigatório')
ATRIBUTO = ('Medida','Tamanho','Modelo','Voltagem','Cor')
CATALOGO = {'S':"Sim","N":"Não"}

estados = []
estados.append(dict(estado = 'Acre',uf = 'AC'))
estados.append(dict(estado = 'Alagoas',uf = 'AL'))
estados.append(dict(estado = 'Amapá',uf = 'AP'))    
estados.append(dict(estado = 'Amazonas',uf = 'AM'))
estados.append(dict(estado = 'Bahia',uf = 'BA'))
estados.append(dict(estado = 'Ceará',uf = 'CE'))
estados.append(dict(estado = 'Distrito Federal',uf = 'DF'))
estados.append(dict(estado = 'Espírito Santo',uf = 'ES')) 
estados.append(dict(estado = 'Goiás',uf = 'GO'))
estados.append(dict(estado = 'Maranhão',uf = 'MA'))
estados.append(dict(estado = 'Mato Grosso',uf = 'MT'))
estados.append(dict(estado = 'Mato Grosso do Sul',uf = 'MS'))
estados.append(dict(estado = 'Minas Gerais',uf = 'MG'))
estados.append(dict(estado = 'Pará',uf = 'PA'))
estados.append(dict(estado = 'Paraíba',uf = 'PB'))
estados.append(dict(estado = 'Paraná',uf = 'PR'))  
estados.append(dict(estado = 'Pernambuco',uf = 'PE'))
estados.append(dict(estado = 'Piauí',uf = 'PI'))
estados.append(dict(estado = 'Rio de Janeiro',uf = 'RJ'))
estados.append(dict(estado = 'Rio Grande do Norte',uf = 'RN'))
estados.append(dict(estado = 'Rio Grande do Sul',uf = 'RS'))
estados.append(dict(estado = 'Rondônia',uf = 'RO'))
estados.append(dict(estado = 'Roraima',uf = 'RR'))
estados.append(dict(estado = 'Santa Catarina',uf = 'SC'))
estados.append(dict(estado = 'São Paulo',uf = 'SP'))     
estados.append(dict(estado = 'Sergipe',uf = 'SE'))
estados.append(dict(estado = 'Tocantins',uf = 'TO'))

def buscar_uf(estado):
    for e in estados:
        if e['estado'] == estado:
            return e['uf']

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
    Field('locpro','string',label='Local:',length=5),
    Field('variacao_id','string', label='Id Variação:', length=20),
    Field('peso','decimal(7,3)',label='Peso'),
    Field('origem','string',label='Origem',length=1),
    Field('ncm', 'string', label='NCM:', length=8),
    Field('largura','decimal(7,3)',label='Largura'),
    Field('altura','decimal(7,3)',label='Altura'),
    Field('comprimento','decimal(7,3)',label='Comprimento'),
    Field('descricao','reference descricoes', label='Descrição:'),
    Field('vendido','integer'),
    Field('estoque1','decimal(7,2)',label='Estoque'),
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
    Field('atributos','string', label='Atributos:', length=150),
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


