def categorias():
    fields = (Categorias.categoria_id,Categorias.categoria)
    formCategorias = grid(Categorias,50,formname="formCategorias",fields=fields)
            
    formCategorias = DIV(formCategorias, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('categoria'))
    elif request.args(-3) == 'edit':
       idCategoria = request.args(-1)
       redirect(URL('categoria', args=idCategoria ))

    return dict(formCategorias=formCategorias)

def categoria():
    idCategoria = request.args(0) or "0"

    if idCategoria == "0":
        formCategoria = SQLFORM(Categorias,field_id='id', _id='formCategoria')
        btnNovo=btnExcluir=btnVoltar = ''
    else:
        formCategoria = SQLFORM(Categorias,idCategoria,_id='formCategoria',field_id='id')
        btnExcluir = excluir("#")
        btnNovo = novo("categoria")

    btnVoltar = voltar("categorias")

    if formCategoria.process().accepted:
        response.flash = 'Categoria Salvo com Sucesso!'
        redirect(URL('categoria', args=formCategoria.vars.id))

    elif formCategoria.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formCategoria=formCategoria, btnNovo=btnNovo,btnVoltar=btnVoltar,btnExcluir=btnExcluir)

def anuncios():

    def delete_anuncio(table,id):
      idDescricao = Anuncios[id].descricao
      del Descricoes[idDescricao] 

    fields = (Anuncios.id,Anuncios.titulo)
    formAnuncios = grid(Anuncios,50,formname="formAnuncios",fields=fields, ondelete = delete_anuncio)
            
    formAnuncios = DIV(formAnuncios, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('anuncio'))
    elif request.args(-3) == 'edit':
       idAnuncio = request.args(-1)
       redirect(URL('anuncio', args=idAnuncio ))

    return dict(formAnuncios=formAnuncios)

def anuncio():

    idAnuncio = request.args(0) or "0"

    Anuncios.preco.writable = False
    Anuncios.estoque.writable = False
    Anuncios.descricao.writable = False

    if idAnuncio == "0":
        formAnuncio = SQLFORM(Anuncios,field_id='id', _id='formAnuncio')
        formAnuncioPublicar = formAnuncioPreco = formAnuncioProdutos = formAnuncioDescricao = formAnuncioImagem =  "Primeiro Cadastre um Anuncio"
        btnNovo=btnExcluir=btnVoltar = ''
        
    else:
        formAnuncio = SQLFORM(Anuncios,idAnuncio,_id='formAnuncio',field_id='id')
        formAnuncioProdutos = LOAD(c='anuncio',f='anuncios_produtos',args=[idAnuncio], target='anunciosprodutos', ajax=True,content='Aguarde, carregando...')
        formAnuncioDescricao = LOAD(c='anuncio',f='anuncios_descricao',args=[idAnuncio], target='anunciosdescricao', ajax=True,content='Aguarde, carregando...')
        formAnuncioImagem = LOAD(c='anuncio', f='anuncios_imagens',args=[idAnuncio], target='anunciosimagens', ajax=True)
        formAnuncioPreco = LOAD(c='anuncio', f='anuncios_preco',args=[idAnuncio], target='anunciospreco', ajax=True)                
        formAnuncioPublicar = LOAD(c='anuncio', f='anuncios_publicar',args=[idAnuncio], target='anunciospublicar', ajax=True)                
        btnExcluir = excluir("#")
        btnNovo = novo("anuncio")

    btnVoltar = voltar("anuncios")

    formAnuncio.element(_name='familia')['_onchange'] = "jQuery('#anuncios_titulo').val($('#anuncios_familia option:selected').text());"
    formAnuncio.element(_name='item_id')['_readonly'] = "readonly"

    if formAnuncio.process().accepted:
        response.flash = 'Anuncio Salvo com Sucesso!'
        redirect(URL('anuncio', args=formAnuncio.vars.id))

    elif formAnuncio.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formAnuncio=formAnuncio,btnExcluir=btnExcluir, btnVoltar=btnVoltar, btnNovo=btnNovo, 
                formAnuncioProdutos=formAnuncioProdutos,formAnuncioDescricao=formAnuncioDescricao,
                formAnuncioImagem=formAnuncioImagem, formAnuncioPublicar=formAnuncioPublicar,
                formAnuncioPreco=formAnuncioPreco)

def anuncios_descricao():

    idAnuncio = int(request.args(0))
    idDescricao = Anuncios[idAnuncio].descricao
    
    if idDescricao == None:   
        # Buscar Descrição Default
        idFamilia = Anuncios[idAnuncio].familia
        
        idDescricaoDefault = Familias[idFamilia].descricao
       
        try:
            Descricoes.descricao.default = Descricoes[idDescricaoDefault].descricao 
        except:
            pass        

        formDescricao = SQLFORM(Descricoes,field_id='id', _id='formdescricao')
    else:
        formDescricao = SQLFORM(Descricoes,idDescricao,field_id='id', _id='formdescricao')

    if formDescricao.process().accepted:
        response.flash = 'Salvo !'
        Anuncios[idAnuncio] = dict(descricao=int(formDescricao.vars.id))
        response.js = "$('#anunciosdescricao').get(0).reload()"

    elif formDescricao.errors:
        response.flash = 'Erro no Formulário !' 

    return dict(formDescricao=formDescricao)        

def atualiza_anuncio(id):
    db.commit()
    idAnuncio = int(id)
    max = Produtos.preco.max()
    sum = Produtos.estoque.sum()
    query = (Anuncios_Produtos.anuncio == idAnuncio) & (Anuncios_Produtos.produto == Produtos.id)
    preco = float(db(query).select(max).first()[max] or 0)
    estoque = float(db(query).select(sum).first()[sum] or 0)
    Anuncios[idAnuncio] = dict(preco=preco,estoque=estoque)
    
def anuncios_produtos():
    idAnuncio = int(request.args(0))

    Anuncios_Produtos.anuncio.writable = False
    Anuncios_Produtos.anuncio.default = idAnuncio

    idFamilia = Anuncios[idAnuncio].familia

    q1 = db(Produtos.familia == idFamilia)

    formProduto = SQLFORM.factory(
        Field('produto',label='Produto:', 
             requires=IS_IN_DB(q1,Produtos.id,'%(nome)s',zero='Selecione um Produto')),
        table_name='pesquisarproduto',
        submit_button='Adicionar',
        )
    
    if formProduto.process().accepted:
        response.flash = 'Salvo !'
        idProduto = formProduto.vars.produto
        q = (Anuncios_Produtos.anuncio == idAnuncio) & (Anuncios_Produtos.produto == idProduto)
        try:      
            id = db(q).select().first()['id']
        except:
            id = 0
        Anuncios_Produtos[id] = dict(anuncio = idAnuncio, produto = idProduto)
        atualiza_anuncio(idAnuncio)

    elif formProduto.errors:
        response.flash = 'Erro no Formulário'
    
    def delete_produto(table,id):
		idAnuncio = Anuncios_Produtos[id].anuncio
		atualiza_anuncio(idAnuncio)

    query = (Anuncios_Produtos.anuncio==idAnuncio)&(Anuncios_Produtos.produto==Produtos.id)
    fields = (Anuncios_Produtos.id,Anuncios_Produtos.produto, Produtos.atributo, Produtos.variacao ,Produtos.preco, Produtos.estoque)
    formProdutos = grid(query,50,args=[idAnuncio],fields=fields,
                   create=False, editable=False, searchable=False, 
                   orderby = Produtos.nome,onvalidation=delete_produto)
    
    
    
    return dict(formProdutos=formProdutos,formProduto=formProduto,)

def anuncios_imagens():
    idAnuncio = int(request.args(0))

    btnAtualizar = atualizar('atualiza_imagem',' Atualizar Imagens ','anunciosimagens')

    q3 = (Anuncios_Imagens.anuncio == idAnuncio) & (Anuncios_Imagens.imagem==Imagens.id)
    imagens = db(q3).select()

    return dict(imagens=imagens,btnAtualizar=btnAtualizar)

def atualiza_imagem():
    idAnuncio = int(request.args(0))
    idFamilia = Anuncios[idAnuncio].familia
    q1 = (Familias_Imagens.familia == idFamilia) & (Familias_Imagens.imagem==Imagens.id)
    imagensFamilia = db(q1).select()
    for row in imagensFamilia:
        imagem = row.familias_imagens.imagem
        q2 = (Anuncios_Imagens.anuncio == idAnuncio) & (Anuncios_Imagens.imagem == imagem)
        Anuncios_Imagens.update_or_insert(q2,anuncio=idAnuncio,imagem=imagem)
    response.js = "$('#anunciosimagens').get(0).reload();"
    
def remove_imagem():
    idImagem = int(request.args(0))
    del Anuncios_Imagens[idImagem]
    response.js = "$('#anunciosimagens').get(0).reload()"

def sugerido(id):
    anuncio = Anuncios(id)
    preco = estoque = 0
    q = (Produtos.id == Anuncios_Produtos.produto) & (Anuncios_Produtos.anuncio==id)
    if anuncio.forma == 'Individual':
        max = Produtos.estoque.max()
        estoque = db(q).select(max).first()[max]
        max = Produtos.preco.max()
        preco = db(q).select(max).first()[max]
    elif anuncio.forma =='Multiplos':
        sum = Produtos.estoque.sum()
        estoque = db(q).select(sum).first()[sum]
        max = Produtos.preco.max()
        preco = db(q).select(max).first()[max]
    elif anuncio.forma =='Kit':
        min = Produtos.estoque.min()
        estoque = db(q).select(min).first()[min]
        sum = Produtos.preco.sum()
        preco = db(q).select(sum).first()[sum]
    return dict(estoque=estoque,preco=preco)

def anuncios_preco():
    idAnuncio = int(request.args(0))
    xsugerido = sugerido(idAnuncio)
    anuncio = Anuncios[idAnuncio]
    es = xsugerido['estoque']
    ep = xsugerido['preco']
    preco = anuncio.preco
    estoque = anuncio.estoque
    
    if preco == None:
        Anuncios[idAnuncio] = dict(preco = ep)
        preco = anuncio.preco
    if estoque == None :
        Anuncios[idAnuncio] = dict(estoque = es)
        estoque = anuncio.estoque

    form = SQLFORM.factory(
        Field('preco','decimal(7,2)',label='Preço',default=preco,requires=IS_DECIMAL_IN_RANGE(dot=',')),
        Field('estoque','decimal(7,2)',label='Estoque',default=estoque,requires=IS_DECIMAL_IN_RANGE(dot=',')),
        )
    if form.process().accepted: 
        preco = form.vars.preco
        estoque = form.vars.estoque
        Anuncios[idAnuncio] = dict(preco=preco,estoque = estoque)
        response.js = "$('#anunciospreco').get(0).reload()"
    elif form.errors:
        response.flash = 'Erro no Formulário'

    return dict(form=form,es=es,ep=ep)


def anuncios_publicar():
    idAnuncio = int(request.args(0))
    anuncio = Anuncios[idAnuncio]
    
    if anuncio.descricao:
        descricao = Descricoes[int(anuncio.descricao)].descricao
    elif Familias[int(anuncio.familia)].descricao:
        descricao = Descricoes[Familias[int(anuncio.familia)].descricao].descricao
    else:
        descricao = ' '
    descricao = dict(plain_text=descricao)

    session.item = dict(title=anuncio.titulo,
                    item_id=anuncio.item_id,
                    category_id=anuncio.categoria,
                    price=float(anuncio.preco),
                    currency_id="BRL",
                    available_quantity=float(anuncio.estoque),
                    status=anuncio.status,
                    buying_mode="buy_it_now",
                    listing_type_id=anuncio.tipo,
                    condition=anuncio.condicao,
                    warranty=anuncio.garantia,
                    description = descricao,
                    )

    if anuncio.item_id:
        btnPublicar = publicar('alterar_item',' Atualizar Item','anunciospublicar')
    else:
        btnPublicar = publicar('anunciar_item',' Anunciar Item','anunciospublicar')
    
    return dict(anuncio=anuncio,btnPublicar=btnPublicar)

def anunciar_item():
    item = session.item
    body = dict(title=item['title'],
                category_id=item['category_id'],
                price=item['price'],
                currency_id=item['currency_id'],
                available_quantity=item['available_quantity'],
                buying_mode=item['buying_mode'],
                listing_type_id=item['listing_type_id'],
                condition=item['condition'],
                warranty=item['warranty'],
                description = item['description'],
                )
        
    if session.ACCESS_TOKEN:
        from meli import Meli 
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
        item = meli.post("/items", body, {'access_token':session.ACCESS_TOKEN})
        status = 'Anunciado com Sucesso....'
        #teste = meli.get("categories/MLB2527")        
    else:
        status = 'Antes Faça o Login....'
        item = ''    

    import json
    print item.status_code
    if item.status_code == 201:
        xitem = json.loads(item.content)    
        print xitem['id']

    #response.flash = status
    #response.js = "$('#anunciospublicar').get(0).reload()"
    return  item

def alterar_item():
    
    item = session.item
    body = dict(title=item['title'],
                category_id=item['category_id'],
                price=item['price'],
                available_quantity=item['available_quantity'],
                #status=item['status'],
                #condition=item['condition'],
                #warranty=item['warranty'],
                )
    
    listing_type_id = dict(id=item['listing_type_id']) 
    description = item['description']

    item_args = "items/%s" %(item['item_id'])
    descricao_args = "%s/description" %(item_args)
    tipo_args = "%s/listing_type" %(item_args)
     
    if session.ACCESS_TOKEN:
        from meli import Meli    
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
        #teste = meli.get("categories/MLB2527")
        
        item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
        desc = meli.put(descricao_args,description, {'access_token':session.ACCESS_TOKEN})
        tipo = meli.post(tipo_args, listing_type_id, {'access_token':session.ACCESS_TOKEN})
        
        status = 'Anuncio Atualizado com Sucesso....'
    else:
        status = 'Antes Faça o Login....'
        item = ''   
       
    response.flash = status
    response.js = "$('#anunciospublicar').get(0).reload()"
    return 

