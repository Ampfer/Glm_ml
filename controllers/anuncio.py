def categorias():
    fields = (Categorias.categoria_id,Categorias.categoria,Categorias.frete)
    formCategorias = grid(Categorias,150,formname="formCategorias",fields=fields, orderby=Categorias.categoria)
            
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
    
    fields = (Anuncios.id,Anuncios.titulo, Anuncios.tipo, Anuncios.status, Anuncios.preco, Anuncios.estoque)
    formAnuncios = grid(Anuncios,80,formname="formAnuncios",fields=fields, ondelete = delete_anuncio,orderby=Anuncios.titulo)
            
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
    Anuncios.preco.default = 0

    Anuncios.desconto.default = 12

    Anuncios.estoque.writable = False
    Anuncios.estoque.default = 0

    Anuncios.descricao.writable = False

    Anuncios.tipo.default = 'gold_pro'

    if idAnuncio == "0":
        formAnuncio = SQLFORM(Anuncios,field_id='id', _id='dados')
        formAnuncioPublicar = formAnuncioPreco = formAnuncioProdutos = formAnuncioDescricao = formAnuncioImagem = formAnuncioAtributos =  "Primeiro Cadastre um Anuncio"
        btnNovo=btnExcluir=btnVoltar = ''
        
    else:
        formAnuncio = SQLFORM(Anuncios,idAnuncio,_id='dados',field_id='id')
        formAnuncioProdutos = LOAD(c='anuncio',f='anuncios_produtos',args=[idAnuncio], target='anunciosprodutos', ajax=True,content='Aguarde, carregando...')
        formAnuncioAtributos = LOAD(c='anuncio',f='anuncios_atributos',args=[idAnuncio], target='anunciosatributos', ajax=True,content='Aguarde, carregando...')        
        formAnuncioDescricao = LOAD(c='anuncio',f='anuncios_descricao',args=[idAnuncio], target='anunciosdescricao', ajax=True,content='Aguarde, carregando...')
        formAnuncioImagem = LOAD(c='anuncio', f='anuncios_imagens',args=[idAnuncio], target='anunciosimagens', ajax=True)
        formAnuncioPreco = LOAD(c='anuncio', f='anuncios_preco',args=[idAnuncio], target='anunciospreco', ajax=True)                
        formAnuncioPublicar = LOAD(c='anuncio', f='anuncios_publicar',args=[idAnuncio], target='anunciospublicar', ajax=True)                
        btnExcluir = excluir("#")
        btnNovo = novo("anuncio")

    btnVoltar = voltar("anuncios")

    formAnuncio.element(_name='familia')['_onchange'] = "if ($('#anuncios_titulo').val() == '' ) {jQuery('#anuncios_titulo').val($('#anuncios_familia option:selected').text())};jQuery('#anuncios_titulo').focus();"
    formAnuncio.element(_name='item_id')['_readonly'] = "readonly"
    formAnuncio.element(_name='titulo')['_onblur']   = "ajax('%s', ['titulo','categoria'], ':eval');" % URL('anuncio', 'sugerir_categoria')

    if formAnuncio.process().accepted:
        response.flash = 'Anuncio Salvo com Sucesso!'
        redirect(URL('anuncio', args=formAnuncio.vars.id))

    elif formAnuncio.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formAnuncio=formAnuncio,btnExcluir=btnExcluir, btnVoltar=btnVoltar, btnNovo=btnNovo, 
                formAnuncioProdutos=formAnuncioProdutos,formAnuncioDescricao=formAnuncioDescricao,
                formAnuncioImagem=formAnuncioImagem, formAnuncioPublicar=formAnuncioPublicar,
                formAnuncioPreco=formAnuncioPreco,formAnuncioAtributos=formAnuncioAtributos,)

def sugerir_categoria():
    if request.vars.categoria == '':
        from meli import Meli
        args = "sites/MLB/category_predictor/predict?title=%s" %(request.vars.titulo)
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
        busca = meli.get(args) 
        import json
        if busca.status_code == 200:
            categoria = json.loads(busca.content)
            nomeCategoria = ''
            for r in categoria['path_from_root']:
                if nomeCategoria:
                    nomeCategoria = nomeCategoria + '/' + r['name']
                else:
                    nomeCategoria = r['name']

            Categorias.update_or_insert(Categorias.categoria_id==categoria['id'],
                categoria = nomeCategoria,
                categoria_id = categoria['id'])
            return "jQuery('#anuncios_categoria').append(new Option('%s', '%s')).val('%s');" % (nomeCategoria,categoria['id'],categoria['id'])

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
    
    def validar_forma(form,idAnuncio=idAnuncio):
        forma = Anuncios[idAnuncio].forma
        query1 = (Anuncios_Produtos.anuncio == idAnuncio)
        vazio = db(query1).isempty()
        if vazio == False and forma == 'Individual':
            form.errors.produto = 'Permitido Somente um Produto para Anuncio Individual'
        
    if formProduto.process(onvalidation=validar_forma).accepted:
        idProduto = formProduto.vars.produto
        
        ### Adiciona Produtos ###
        query = (Anuncios_Produtos.anuncio == idAnuncio) & (Anuncios_Produtos.produto == idProduto)
        Anuncios_Produtos.update_or_insert(query, anuncio = idAnuncio, produto = idProduto)

        #### Atualiza Atributos ####
        marca = Produtos[idProduto].marca
        ean = Produtos[idProduto].ean
        if marca:
            query = (Anuncios_Atributos.anuncio == idAnuncio) & (Anuncios_Atributos.atributo == 1)
            Anuncios_Atributos.update_or_insert(query, atributo = 1, valor= marca)
        if ean:
            query = (Anuncios_Atributos.anuncio == idAnuncio) & (Anuncios_Atributos.atributo == 3)
            Anuncios_Atributos.update_or_insert(query, atributo = 3, valor= ean)

        response.flash = 'Produto Adicionado com Sucesso.... !'

    elif formProduto.errors:
        response.flash = 'Erro no Formulário...'
    
    
    def delete_produto(table,id):
		idAnuncio = Anuncios_Produtos[id].anuncio

    query = (Anuncios_Produtos.anuncio==idAnuncio)&(Anuncios_Produtos.produto==Produtos.id)
    fields = (Anuncios_Produtos.id,Anuncios_Produtos.produto, Produtos.atributo, Produtos.variacao ,Produtos.preco, Produtos.estoque)
    formProdutos = grid(query,50,args=[idAnuncio],fields=fields,
                   create=False, editable=False, searchable=False, 
                   orderby = Produtos.nome)
    
    return dict(formProdutos=formProdutos,formProduto=formProduto,)

def anuncios_atributos():
    idAnuncio = idAnuncio = int(request.args(0))

    Anuncios_Atributos.anuncio.writable = Anuncios_Atributos.anuncio.readable =  False
    Anuncios_Atributos.anuncio.default = idAnuncio

    formAtributos = grid(Anuncios_Atributos.anuncio==idAnuncio,args=[idAnuncio], formname= 'anunciosatributos')
    return dict(formAtributos=formAtributos)

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

def anuncios_preco():
    
    idAnuncio = int(request.args(0))
    xsugerido = sugerido(idAnuncio)
    anuncio = Anuncios[idAnuncio]
    es = xsugerido['estoque']
    ep = round(xsugerido['preco'],1)
    preco = anuncio.preco
    desconto = anuncio.desconto
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
        if preco >= 120:
            Anuncios[idAnuncio] = dict(frete = 'gratis')
        response.js = "$('#anunciospreco').get(0).reload()"
    elif form.errors:
        response.flash = 'Erro no Formulário'

    return dict(form=form,es=es,ep=ep,desconto=desconto)

def anuncios_publicar():
    idAnuncio = int(request.args(0))
    anuncio = Anuncios[idAnuncio]
    
    #### Buscando a Descrição do Anuncio ####
    if anuncio.descricao:
        descricao = Descricoes[int(anuncio.descricao)].descricao
    elif Familias[int(anuncio.familia)].descricao:
        descricao = Descricoes[Familias[int(anuncio.familia)].descricao].descricao
    else:
        descricao = ' '
    descricao = dict(plain_text=descricao)

    #### Buscando Tipo de Frete ####
    free_shipping = True if anuncio.frete == 'gratis' else False
    frete = dict(local_pick_up=True,free_shipping=free_shipping,free_methods=[],mode="me2")

    atributos = []
    buscaAtributos = db(Anuncios_Atributos.anuncio == idAnuncio).select()
    
    for atributo in buscaAtributos:
    	atributo_id = Atributos(atributo.atributo).atributo_id
    	atributos.append(dict(id=atributo_id, value_name=atributo.valor))
    
    #### Buscando as Imagens do Anuncio ####
    imagensIds = db(Anuncios_Imagens.anuncio == idAnuncio).select(Anuncios_Imagens.imagem)
    imagens = []
    url = 'http://localhost:8000/glm_ml/uploads/'
    for imagem in imagensIds:
        img = str(Imagens[imagem.imagem].imagem)
        imagens.append(dict(source=url+img))
    
    #### Montando Dicionário com Dados do Anuncio ####
    session.anuncio = dict(id=anuncio.id,
                    title=anuncio.titulo,
                    item_id=anuncio.item_id,
                    category_id=anuncio.categoria,
                    price=float(anuncio.preco),
                    currency_id="BRL",
                    available_quantity=float(anuncio.estoque),
                    status=anuncio.status,
                    buying_mode="buy_it_now",
                    listing_type_id=anuncio.tipo,
                    frete=frete,
                    condition="new",
                    warranty=anuncio.garantia,
                    description = descricao,
                    pictures=imagens,
                    attributes=atributos,
                    )
    #### Verificando se Item Novo ou Alteração ####
    if anuncio.item_id:
        btnPublicar = publicar('alterar_item',' Atualizar Item','anunciospublicar')
    else:
        btnPublicar = publicar('anunciar_item',' Anunciar Item','anunciospublicar')
    
    return dict(anuncio=anuncio,btnPublicar=btnPublicar)

def anunciar_item():
    idAnuncio = session.anuncio['id']

    body = dict(title=session.anuncio['title'],
                category_id=session.anuncio['category_id'],
                price=session.anuncio['price'],
                currency_id=session.anuncio['currency_id'],
                available_quantity=session.anuncio['available_quantity'],
                buying_mode=session.anuncio['buying_mode'],
                listing_type_id=session.anuncio['listing_type_id'],
                condition=session.anuncio['condition'],
                warranty=session.anuncio['warranty'],
                description=session.anuncio['description'],
                shipping=session.anuncio['frete'],
                pictures=session.anuncio['pictures'],
                )
    bodyAtributo = dict(attributes=session.anuncio['attributes'])
        
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
    if item.status_code == 201:
    	### Salvando item_id no banco de dados
        xitem = json.loads(item.content)    
        Anuncios[int(idAnuncio)] = dict(item_id=xitem['id'])
        ### Salvando Atributos no ML
        atrib_args = "items/%s" %(xitem['id'])
        atrib = meli.put(atrib_args, bodyAtributo, {'access_token':session.ACCESS_TOKEN})   

    #response.flash = status
    #response.js = "$('#anunciospublicar').get(0).reload()"
    return atrib

def alterar_item():

    body = dict(title=session.anuncio['title'],
                price=session.anuncio['price'],
                available_quantity=session.anuncio['available_quantity'],
                shipping=session.anuncio['frete'],
                attributes=session.anuncio['attributes']
                )
    #bodyAtributo = dict(attributes=session.anuncio['attributes'])
    
    listing_type_id = dict(id=session.anuncio['listing_type_id']) 
    description = session.anuncio['description']

    item_args = "items/%s" %(session.anuncio['item_id'])
    descricao_args = "%s/description" %(item_args)
    tipo_args = "%s/listing_type" %(item_args)
    if session.ACCESS_TOKEN:
        from meli import Meli    
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
        item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
        desc = meli.put(descricao_args,description, {'access_token':session.ACCESS_TOKEN})
        tipo = meli.post(tipo_args, listing_type_id, {'access_token':session.ACCESS_TOKEN})
        #atrib = meli.put(item_args, bodyAtributo, {'access_token':session.ACCESS_TOKEN})   

        if item.status_code != 200 or desc.status_code != 200:
            status = 'Falha na Atualização do Item : %s %s %s' %(item,desc,tipo)
        else:
            status = 'Anuncio Atualizado com Sucesso....'
    else:
        status = 'Antes Faça o Login....'
        item = ''   
       
    response.flash = status
    response.js = "$('#anunciospublicar').get(0).reload()"
    return 

def importar_anuncios():
	# Cunsulta de itens na Api do mercado livre
    from meli import Meli
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
    busca = meli.get("sites/MLB/search?seller_id=158428813&offset=100&limit=100")
    import json
    if busca.status_code == 200:
        itens = json.loads(busca.content)    

    xitens = itens['results']
  
    #Loop nos itens encontrados
    for item in xitens: 
    	# Verifica Tipo de Frete
        if item['shipping']['free_shipping'] == False:
            frete = 'comprador'
        else:
            frete = 'gratis'
		# Busca Categorias       
        args = "categories/%s" %(item['category_id'])
        categoria = meli.get(args) 
        if categoria.status_code == 200:
            categoria = json.loads(categoria.content) 
        
        nomeCategoria = ''
        for r in categoria['path_from_root']:
            if nomeCategoria:
                nomeCategoria = nomeCategoria + '/' + r['name']
            else:
                nomeCategoria = r['name']
        valorFrete = 0 ### Fazer Rotina para Buscar valor do Frete por Categoria

        # Salva Categorias
        Categorias.update_or_insert(Categorias.categoria_id == item['category_id'],
                categoria = nomeCategoria,
                categoria_id = item['category_id'],
                frete = valorFrete,
                )
        # Salva Anuncios
        Anuncios.update_or_insert(Anuncios.item_id == item['id'],
                item_id=item['id'],
                titulo=item['title'],
                categoria=item['category_id'],
                preco=item['price'],
                estoque=item['available_quantity'],
                tipo=item['listing_type_id'],
                frete = frete,
                status = 'active',
                )
        # Salva Atributos
        for atributo in item['attributes'] :
        	#salva atributos na tabele atributos
        	id = Atributos.update_or_insert(Atributos.atributo_id == atributo['id'],
        		atributo_id = atributo['id'],
        		nome = atributo['name'],
        		)
        	idAnuncio = int(db(Anuncios.item_id == item['id']).select().first()['id'])
        	idAtributo = int(db(Atributos.atributo_id==atributo['id']).select().first()['id'])
        	#salva atributos na tabela anucios_atributos
        	Anuncios_Atributos.update_or_insert((Anuncios_Atributos.anuncio == idAnuncio) & (Anuncios_Atributos.atributo == idAtributo),
        		anuncio = idAnuncio,
        		atributo = idAtributo,
        		valor =  atributo['value_name']
        		)

    return busca