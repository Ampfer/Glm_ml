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
    #formAnuncio.element(_name='preco')['_readonly'] = "readonly"

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

    if anuncio.item_id:
        session.item = dict(title=anuncio.titulo,
                            category_id=anuncio.categoria,
                            price=float(anuncio.preco),        
                            available_quantity=float(anuncio.estoque),
                            )
        session.description = descricao
        btnPublicar = publicar('alterar_item',' Atualizar Item','anunciospublicar',anuncio.item_id)
    else:
        session.item = dict(title=anuncio.titulo,
                            category_id=anuncio.categoria,
                            price=float(anuncio.preco),
                            currency_id="BRL",
                            available_quantity=float(anuncio.estoque),
                            buying_mode="buy_it_now",
                            listing_type_id=anuncio.tipo,
                            condition=anuncio.condicao,
                            warranty=anuncio.garantia,
                            description = descricao,
                            )
        btnPublicar = publicar('anunciar_item',' Anunciar Item','anunciospublicar',anuncio.item_id)
    
    return dict(anuncio=anuncio,btnPublicar=btnPublicar)

def anunciar_item():
    from meli import Meli 
    body = session.item
    #body = {"title":"Item De Teste - Por Favor, Não Ofertar! --kc:off","category_id":"MLB257111","price":10,"currency_id":"BRL","available_quantity":1,"buying_mode":"buy_it_now","listing_type_id":"bronze","condition":"new","description":"Item de Teste. Mercado Livre's PHP SDK.","video_id":"Q6dsRpVyyWs","warranty":"12 month","pictures":[{"source":"https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/IPhone_7_Plus_Jet_Black.svg/440px-IPhone_7_Plus_Jet_Black.svg.png"},{"source":"https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/IPhone7.jpg/440px-IPhone7.jpg"}],"attributes":[{"id":"EAN","value_name":"190198043566"},{"id":"COLOR","value_id":"52049"},{"id":"WEIGHT","value_name":"188g"},{"id":"SCREEN_SIZE","value_name":"4.7 polegadas"},{"id":"TOUCH_SCREEN","value_id":"242085"},{"id":"DIGITAL_CAMERA","value_id":"242085"},{"id":"GPS","value_id":"242085"},{"id":"MP3","value_id":"242085"},{"id":"OPERATING_SYSTEM","value_id":"296859"},{"id":"OPERATING_SYSTEM_VERSION","value_id":"iOS 10"},{"id":"DISPLAY_RESOLUTION","value_id":"1920 x 1080"},{"id":"BATTERY_CAPACITY","value_name":"3980 mAh"},{"id":"FRONT_CAMERA_RESOLUTION","value_name":"7 mpx"}]}
        
    if session.ACCESS_TOKEN:
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
        item = meli.post("/items", body, {'access_token':session.ACCESS_TOKEN})
        status = 'Anunciado com Sucesso....'
        #teste = meli.get("categories/MLB2527")        
    else:
        status = 'Antes Faça o Login....'
        item = ''    

    #response.flash = status
    #response.js = "$('#anunciospublicar').get(0).reload()"
    return  item

def alterar_item():
    from meli import Meli    
    body = session.item
    item_args = "items/%s" %(request.args(0))
    descricao_args = "%s/description" %(item_args)
    print descricao_args   
    if session.ACCESS_TOKEN:
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
        item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
        desc = meli.put(descricao_args, session.description, {'access_token':session.ACCESS_TOKEN})
        status = 'Anuncio Atualizado com Sucesso....'
    else:
        status = 'Antes Faça o Login....'
        item = ''   
    
    import json
    teste = json.loads(desc)

    #response.flash = status
    #response.js = "$('#anunciospublicar').get(0).reload()"
    return desc

