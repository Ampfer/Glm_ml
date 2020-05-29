# -*- coding: utf-8 -*-

from math import floor

def teste():
    categorias = db(Categorias.id > 0).select()
    for item in categorias:
         db(Anuncios.categoria == item.categoria_id ).update(fretegratis=item.frete)


@auth.requires_membership('admin')
def categorias():
    fields = (Categorias.categoria_id,Categorias.categoria,Categorias.frete)
    formCategorias = grid(Categorias,150,formname="formCategorias",fields=fields, orderby=Categorias.categoria)
            
    if request.args(-2) == 'new':
       redirect(URL('categoria'))
    elif request.args(-3) == 'edit':
       idCategoria = request.args(-1)
       redirect(URL('categoria', args=idCategoria ))

    return dict(formCategorias=formCategorias)

@auth.requires_membership('admin')
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

@auth.requires_membership('admin')
def categoria_qtde_anuncio():
    categorias = db(Categorias.id > 0).select()
    for item in categorias:
        # Buscar Categorias
        qtde = db(Anuncios.categoria == item.categoria_id).count()
        Categorias[item.id] = dict(qtde_anuncios = qtde)

@auth.requires_membership('admin')

def vincular_categoria():
    categorias = []
    nivel1 = db(Categorias_Bling.pai_id == 0).select()
    for n1 in nivel1:
        item = []
        nivel2 = db(Categorias_Bling.pai_id == n1.pai_id).select()
        for n2 in nivel2:
            nivel3 = db(Categorias_Bling.pai_id == n2.pai_id).select()
            for n3 in nivel3:
                item.append(n3.id)
                item.append('{}/{}/{}'.format(n1.categoria,n2.categoria,n3.categoria))
        categorias.append(item)
    print categorias


@auth.requires_membership('admin')
def atualizar_categorias():

    form = FORM.confirm('Atualizar Categoria',{'Voltar':URL('default','index')})

    if form.accepted:
        categorias = db(Categorias.id > 0).select()
        for item in categorias:
             # Buscar Categorias
            categoria = buscar_categoria(item['categoria_id'])
            
            # Salvar Categorias
            Categorias.update_or_insert(Categorias.categoria_id == item.categoria_id,
                    categoria = categoria['categoria'],
                    categoria_id = item['categoria_id'],
                    frete = categoria['valorFrete'],
                    )

            # Atualizar anuncios
            db(Anuncios.categoria == item['categoria_id'] ).update(fretegratis=categoria['valorFrete'])
        
        response.flash = 'Categorias Atualizadas com Sucesso'

    return dict(form=form)

def duplicar_anuncio():
    anuncio_id = request.vars.anuncio
    x = request.vars.x
    anuncio = Anuncios[anuncio_id]
    produtos = db(Anuncios_Produtos.anuncio == anuncio_id).select()
    atributos = db(Anuncios_Atributos.anuncio == anuncio_id).select()
    imagens = db(Anuncios_Imagens.anuncio == anuncio_id).select()
      
    tp = 'P' if anuncio.tipo == 'gold_pro' else 'C'
   
    if int(x) > 1:
        quantidade = int(x)
        forma = 'Pack'
        sk = tp[0] + x
        tipo = anuncio.tipo
        tt = ' ({} PEÇAS)'.format(x)
    else:
        quantidade = 0
        forma = anuncio.forma
        sk = tp[0]
        tipo = 'gold_special' if anuncio.tipo == 'gold_pro' else 'gold_pro'
        tt = ''

    # Duplicando dados do Anuncio
    newAnuncio = anuncio.as_dict()
    newAnuncio['forma'] = forma
    newAnuncio['tipo'] = tipo
    del newAnuncio['id']
    del newAnuncio['item_id']
    Anuncios[None] = newAnuncio
    newAnuncioId = db(Anuncios.id>0).select(orderby =~ Anuncios.id).first()['id']
    # Duplicando Produtos do Anuncio
    for produto in produtos:
        newProduto = produto.as_dict()
        quantidade = quantidade if quantidade > 0 else int(produto.quantidade)
        newProduto['quantidade'] = quantidade
        del newProduto['id']
        newProduto['anuncio'] = newAnuncioId
        Anuncios_Produtos[None] = newProduto
    # Duplicando Atributos do Anuncio
    for atributo in atributos:
        newAtributo = atributo.as_dict()
        if atributo.atributo == 313:
            newAtributo['valor'] = newAtributo['valor'] + sk
        del newAtributo['id']
        newAtributo['anuncio'] = newAnuncioId
        Anuncios_Atributos[None] = newAtributo
    # Duplicando Imagens do Anuncio
    for imagem in imagens:
        newImagem = imagem.as_dict()
        del newImagem['id']
        newImagem['anuncio'] = newAnuncioId
        Anuncios_Imagens[None] = newImagem

    newSugerido = sugerido(Anuncios[newAnuncioId])
    titulo = (Anuncios[newAnuncioId].titulo + tt)[:60]

    if newSugerido['preco'] >= 120:
        Anuncios[newAnuncioId] = dict(frete = 'gratis')
        newSugerido = sugerido(Anuncios[newAnuncioId])

    Anuncios[newAnuncioId] = dict(preco = newSugerido['preco'], 
                                  estoque = floor(newSugerido['estoque']),
                                  titulo=titulo,
                                  )

    redirect(URL('anuncio', args=newAnuncioId ))

@auth.requires_membership('admin')      
def anuncios():

    def delete_anuncio(table,id):
        try:
            idDescricao = Anuncios[id].descricao
            del Descricoes[idDescricao] 
        except:
            pass
    '''
    links=[
    dict(header='',
        body=lambda row: A(TAG.button('P/C',_class='btn btn-secondary btn-sm'),
         _href=URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=1)) , _target = '_blank', _onclick="return confirm('Deseja Duplicar esse Anuncio ?');" )),
    dict(header='',
        body=lambda row: A(TAG.button('2X',_class='btn btn-secondary btn-sm'),
         _href=URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=2)) , _target = '_blank', _onclick="return confirm('Deseja gerar kit com 2 unidades ?');" )),
    dict(header='',
        body=lambda row: A(TAG.button('5X',_class='btn btn-secondary btn-sm'),
         _href=URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=5)) , _target = '_blank', _onclick="return confirm('href={} target = '_blank' onclick="return confirm('Deseja Duplicar esse Anuncio ?');"s ?');" )),
    dict(header='',
        body=lambda row: A(TAG.button('10X',_class='btn btn-secondary btn-sm'),
        _href=URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=10)) , _target = '_blank', _onclick="return confirm('Deseja gerar kit com 10 unidades ?');" ))
    ]
    '''
    def btn(row):
        btnHtml = """
        <div class="dropdown">
          <button class="btn btn-secondary dropdown-toggle" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            Duplicar
          </button>
          <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
            <a class="dropdown-item" href={} target = '_blank' onclick="return confirm('Deseja Duplicar esse Anuncio ?');" style='padding:10px'>Premium / Clássico</a><br>
            <a class="dropdown-item" href={} target = '_blank' onclick="return confirm('Deseja gerar kit com 02 unidades ?');" style='padding:10px'>Kit 02 unidades</a><br>
            <a class="dropdown-item" href={} target = '_blank' onclick="return confirm('Deseja gerar kit com 04 unidades ?');" style='padding:10px'>Kit 04 unidades</a><br>
            <a class="dropdown-item" href={} target = '_blank' onclick="return confirm('Deseja gerar kit com 06 unidades ?');" style='padding:10px'>Kit 06 unidades</a><br>
            <a class="dropdown-item" href={} target = '_blank' onclick="return confirm('Deseja gerar kit com 10 unidades ?');" style='padding:10px'>Kit 10 unidades</a><br>
            <a class="dropdown-item" href={} target = '_blank' onclick="return confirm('Deseja gerar kit com 12 unidades ?');" style='padding:10px'>Kit 12 unidades</a><br>
          </div>
        </div>
        """.format(
            URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=1)),
            URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=2)),
            URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=4)),
            URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=8)),
            URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=10)),
            URL('duplicar_anuncio',vars = dict(anuncio=row.id,x=12)),

            )
        return XML(btnHtml)

    links=[dict(header='Ações',body=lambda row: btn(row))]

    fields = (Anuncios.id,Anuncios.titulo, Anuncios.tipo, Anuncios.desconto, Anuncios.preco, Anuncios.estoque)
    formAnuncios = grid(Anuncios,80,formname="formAnuncios",fields=fields, ondelete = delete_anuncio,
        orderby=Anuncios.titulo, links=links)   

    if request.args(-2) == 'new':
       redirect(URL('anuncio'))
    elif request.args(-3) == 'edit':
       idAnuncio = request.args(-1)
       redirect(URL('anuncio', args=idAnuncio ))

    return dict(formAnuncios=formAnuncios)

@auth.requires_membership('admin')
def anuncio():

    idAnuncio = request.args(0) or "0"

    Anuncios.preco.writable = False
    Anuncios.preco.default = 0

    Anuncios.desconto.default = 0
    Anuncios.garantia.default = 'Garantia de 3 Meses contra Defeitos de Fabricação'

    Anuncios.estoque.writable = False
    Anuncios.estoque.default = 0

    Anuncios.descricao.writable = False

    Anuncios.tipo.default = 'gold_pro'
    Anuncios.fretegratis.default = 0

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
    formAnuncio.element(_name='fretegratis')['_readonly'] = "readonly"
    formAnuncio.element(_name='titulo')['_onblur']   = "ajax('%s', ['titulo','categoria'], ':eval');" % URL('anuncio', 'sugerir_categoria')

    def validar(form):
        valorfrete = buscar_categoria(form.vars.categoria)['valorFrete'] or 0
        form.vars.fretegratis = valorfrete

    if formAnuncio.process(onvalidation=validar).accepted:

		response.flash = 'Anuncio Salvo com Sucesso!'
		redirect(URL('anuncio', args=formAnuncio.vars.id))

    elif formAnuncio.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formAnuncio=formAnuncio,btnExcluir=btnExcluir, btnVoltar=btnVoltar, btnNovo=btnNovo, 
                formAnuncioProdutos=formAnuncioProdutos,formAnuncioDescricao=formAnuncioDescricao,
                formAnuncioImagem=formAnuncioImagem, formAnuncioPublicar=formAnuncioPublicar,
                formAnuncioPreco=formAnuncioPreco,formAnuncioAtributos=formAnuncioAtributos,)

@auth.requires_membership('admin')
def sugerir_categoria():
    if request.vars.categoria == '':
        from meli import Meli

        args = "sites/MLB/category_predictor/predict?title=%s" %(request.vars.titulo)
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
        busca = meli.get(args) 
        import json
        if busca.status_code == 200:
            sugestao = json.loads(busca.content)
            categoria = buscar_categoria(sugestao['id'])

            Categorias.update_or_insert(Categorias.categoria_id==sugestao['id'],
                categoria_id = sugestao['id'],
                categoria = categoria['categoria'],
                frete = categoria['valorFrete'],)
            
            return "jQuery('#anuncios_categoria').append(new Option('%s', '%s')).val('%s');" % (categoria['categoria'],sugestao['id'],sugestao['id'])

@auth.requires_membership('admin')
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

@auth.requires_membership('admin')
def anuncios_produtos():
    idAnuncio = int(request.args(0))
    anuncio = Anuncios[idAnuncio]
    forma = anuncio.forma

    Anuncios_Produtos.anuncio.writable = False
    Anuncios_Produtos.anuncio.default = idAnuncio
    
    idFamilia = Anuncios[idAnuncio].familia

    #q1 = db(Produtos.familia == idFamilia)
    q1 = (db.produtos.id == Familias_Produtos.produto) & (Familias_Produtos.familia == idFamilia)

    formProduto = SQLFORM.factory(
        Field('produto',label='Produto:',requires=IS_IN_DB(db(q1),db.produtos.id,'%(nome)s',zero='Selecione um Produto')),
        Field('quantidade','integer',default=1,label='Quantidade:'),
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
        qtde = formProduto.vars.quantidade
        ### Adiciona Produtos ###
        query = (Anuncios_Produtos.anuncio == idAnuncio) & (Anuncios_Produtos.produto == idProduto)
        Anuncios_Produtos.update_or_insert(query, anuncio = idAnuncio, produto = idProduto, quantidade = qtde)

        #### Atualiza Atributos ####
        marca = db.produtos[idProduto].marca    
        ean = db.produtos[idProduto].ean
        sku = '%05d' % int(idProduto)

        if marca:
            query = (Anuncios_Atributos.anuncio == idAnuncio) & (Anuncios_Atributos.atributo == 1)
            Anuncios_Atributos.update_or_insert(query,anuncio=idAnuncio, atributo = 1, valor= marca)
        if ean and forma=='Individual':
            query = (Anuncios_Atributos.anuncio == idAnuncio) & (Anuncios_Atributos.atributo == 3)
            Anuncios_Atributos.update_or_insert(query,anuncio=idAnuncio, atributo = 3, valor= ean)
        if sku and forma !='Multiplos':
            query = (Anuncios_Atributos.anuncio == idAnuncio) & (Anuncios_Atributos.atributo == 313)
            Anuncios_Atributos.update_or_insert(query,anuncio=idAnuncio, atributo = 313, valor= sku)            

        #### Atualiza Preço e Estoque ####
        sugerir = sugerido(anuncio)
        if Anuncios[idAnuncio].preco == 0:
            Anuncios[idAnuncio] = dict(preco=sugerir['preco'],estoque=sugerir['estoque'])
        else:
            Anuncios[idAnuncio] = dict(estoque=sugerir['estoque'])
        response.flash = 'Produto Adicionado com Sucesso.... !'

    elif formProduto.errors:
        response.flash = 'Erro no Formulário...'
 
    query = (Anuncios_Produtos.anuncio==idAnuncio)&(Anuncios_Produtos.produto==db.produtos.id)

    fields = (Anuncios_Produtos.quantidade,Anuncios_Produtos.produto, db.produtos.atributo, db.produtos.variacao,db.produtos.preco, db.produtos.estoque, Anuncios_Produtos.preco_sugerido)

    formProdutos = grid(query,50,args=[idAnuncio],fields=fields,
                   create=False, editable=False, searchable=False, 
                   orderby = db.produtos.nome)
    
    return dict(formProdutos=formProdutos,formProduto=formProduto,)

@auth.requires_membership('admin')
def anuncios_atributos():
    idAnuncio = idAnuncio = int(request.args(0))

    Anuncios_Atributos.anuncio.writable = Anuncios_Atributos.anuncio.readable =  False
    Anuncios_Atributos.anuncio.default = idAnuncio

    formAtributos = grid(Anuncios_Atributos.anuncio==idAnuncio,args=[idAnuncio], formname= 'anunciosatributos')
    return dict(formAtributos=formAtributos)

@auth.requires_membership('admin')
def anuncios_imagens():
    idAnuncio = int(request.args(0))

    btnAtualizar = atualizar('atualiza_imagem_familia',' Imagens Familia','anunciosimagens')
    btnAtualizar1 = atualizar('atualiza_imagem_produto',' Imagens Produto ','anunciosimagens')

    q3 = (Anuncios_Imagens.anuncio == idAnuncio) & (Anuncios_Imagens.imagem==Imagens.id)
    imagens = db(q3).select()

    return dict(imagens=imagens,btnAtualizar=btnAtualizar,btnAtualizar1=btnAtualizar1)

@auth.requires_membership('admin')
def atualiza_imagem_familia():
    idAnuncio = int(request.args(0))
    idFamilia = Anuncios[idAnuncio].familia
    q1 = (Familias_Imagens.familia == idFamilia) & (Familias_Imagens.imagem==Imagens.id)
    imagensFamilia = db(q1).select()
    for row in imagensFamilia:
        imagem = row.familias_imagens.imagem
        q2 = (Anuncios_Imagens.anuncio == idAnuncio) & (Anuncios_Imagens.imagem == imagem)
        Anuncios_Imagens.update_or_insert(q2,anuncio=idAnuncio,imagem=imagem)
    response.js = "$('#anunciosimagens').get(0).reload();"

@auth.requires_membership('admin')
def atualiza_imagem_produto():
    idAnuncio = int(request.args(0))
    anuncios_produtos = db(Anuncios_Produtos.anuncio == idAnuncio).select()
    for anuncio_produto in anuncios_produtos:
        idproduto = anuncio_produto.produto
        q1 = (Produtos_Imagens.produto == idproduto) & (Produtos_Imagens.imagem==Imagens.id)
        imagensProduto = db(q1).select()
        for row in imagensProduto:
            imagem = row.produtos_imagens.imagem
            q2 = (Anuncios_Imagens.anuncio == idAnuncio) & (Anuncios_Imagens.imagem == imagem)
            Anuncios_Imagens.update_or_insert(q2,anuncio=idAnuncio,imagem=imagem)
    response.js = "$('#anunciosimagens').get(0).reload();"
    
@auth.requires_membership('admin')
def remove_imagem():
    idImagem = int(request.args(0))
    del Anuncios_Imagens[idImagem]
    response.js = "$('#anunciosimagens').get(0).reload()"

@auth.requires_membership('admin')
def anuncios_preco():
    
    idAnuncio = int(request.args(0))
    anuncio = Anuncios[idAnuncio]

    xsugerido = sugerido(anuncio)
    
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
        desc = round((1-(float(preco)*(1-float(desconto/100)))/float(ep))*100,2)

        precoAnterior = Anuncios[idAnuncio].preco

        preAlt = 'S' if abs(float(preco)-float(precoAnterior))> float(0.05) else 'N'
        
        Anuncios[idAnuncio] = dict(preco=preco,estoque = estoque,desconto=desc, preco_alterado = preAlt)
        response.js = "$('#anuncios_desconto').val(%s)" %(desc)
        if preco >= 120:
            Anuncios[idAnuncio] = dict(frete = 'gratis')
        response.js = "$('#anunciospreco').get(0).reload()"

    elif form.errors:
        response.flash = 'Erro no Formulário'

    return dict(form=form,es=es,ep=ep,desconto=desconto)

@auth.requires_membership('admin')
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
    frete = dict(local_pick_up=False,free_shipping=free_shipping,free_methods=[],mode="me2")

    atributos = []
    buscaAtributos = db(Anuncios_Atributos.anuncio == idAnuncio).select()
    
    for atributo in buscaAtributos:
    	atributo_id = Atributos(atributo.atributo).atributo_id
    	if atributo_id == "ITEM_CONDITION" and anuncio.item_id:
    		pass
    	else:
    		atributos.append(dict(id=atributo_id, value_name=atributo.valor))
    
    sku = '%05d' % anuncio.id

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
                    attributes=atributos,
                    forma=anuncio.forma,
                    sku =sku
                    )

    #### Verificando se Item Novo ou Alteração ####
    if anuncio.item_id:
        btnPublicar = publicar('alterar_item',' Atualizar Item','anunciospublicar')
    else:
        btnPublicar = publicar('anunciar_item',' Anunciar Item','anunciospublicar')
    
    return dict(anuncio=anuncio,btnPublicar=btnPublicar)

@auth.requires_membership('admin')
def buscar_variacao(idAnuncio,imagens):
    variacao = []
    if session.anuncio['forma'] == 'Multiplos':
        imgs = []
        for img in imagens:
            imgs.append(img['id'])

        rows = db(Anuncios_Produtos.anuncio==idAnuncio).select()
        for row in rows:
            produto = db.produtos[row.produto]
            variacaoProduto = dict(id=row.variacao_id,
                                   price=float(row.preco_sugerido),
                                   attribute_combinations = [dict(name = produto.atributo,value_name=produto.variacao,id=produto.id)],
                                   available_quantity=float(produto.estoque),
                                   seller_custom_field = str(produto.id),
                                   picture_ids = imgs
                                   )
            variacao.append(variacaoProduto)
    return variacao

@auth.requires_membership('admin')
def anunciar_item():
    idAnuncio = session.anuncio['id']

    ## Faz Uploads das imagens e retorna Ids
    imagens = imagem_upload(idAnuncio)
    #### Buscar Variações ####
    variacao = buscar_variacao(idAnuncio,imagens)

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
                seller_custom_field = session.anuncio['sku'],
                pictures=imagens,
                variations = variacao,
                )
    
    bodyAtributo = dict(attributes=session.anuncio['attributes'])

    if session.ACCESS_TOKEN:
        from meli import Meli 
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
        item = meli.post("/items", body, {'access_token':session.ACCESS_TOKEN})
    else:
        status = 'Antes Faça o Login....'
        item = ''    

    import json
    if item.status_code == 201:
        status = 'Anunciado com Sucesso....'
    	### Salvando item_id no banco de dados
        xitem = json.loads(item.content)
        valorfrete = buscar_valor_frete(xitem['id'])
        Anuncios[int(idAnuncio)] = dict(item_id=xitem['id'], preco_alterado = 'N')
        ### Salvando Atributos no ML
        atrib_args = "items/%s" %(xitem['id'])
        atrib = meli.put(atrib_args, bodyAtributo, {'access_token':session.ACCESS_TOKEN})
        if atrib.status_code != 200:
            status = 'Falha na Atualização do Item : item:%s ' %(atrib)        
    else:
        status = 'Falha na Atualização do Item : item:%s ' %(item)   

    response.flash = status
    response.js = "$('#anunciospublicar').get(0).reload()"

    return

@auth.requires_membership('admin')
def alterar_item():
    idAnuncio = session.anuncio['id']

    ## Faz Uploads das imagens e retorna Ids
    imagens = imagem_upload(idAnuncio)

    body = dict(title=session.anuncio['title'],
                price=session.anuncio['price'],
                available_quantity=session.anuncio['available_quantity'],
                shipping=session.anuncio['frete'],
                attributes=session.anuncio['attributes'],
                seller_custom_field = session.anuncio['sku'],
                pictures=imagens,
                )

    #### Buscar Variações ####
    variacao = buscar_variacao(idAnuncio,imagens)

    bodyvariacao = dict(title=session.anuncio['title'],
                        shipping=session.anuncio['frete'],
                        attributes=session.anuncio['attributes'],
                        variations=variacao,
                        )
    
    listing_type_id = dict(id=session.anuncio['listing_type_id']) 
    description = session.anuncio['description']

    item_args = "items/%s" %(session.anuncio['item_id'])
    descricao_args = "%s/description" %(item_args)
    tipo_args = "%s/listing_type" %(item_args)
    
    if session.ACCESS_TOKEN:
        from meli import Meli    
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

        if session.anuncio['forma'] == 'Multiplos':
            item = meli.put(item_args, bodyvariacao, {'access_token':session.ACCESS_TOKEN})
        else:
            item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
        
        desc = meli.put(descricao_args,description, {'access_token':session.ACCESS_TOKEN})
        tipo = meli.post(tipo_args, listing_type_id, {'access_token':session.ACCESS_TOKEN})

        if item.status_code != 200 or desc.status_code != 200:
            status = 'Falha na Atualização do Item : item:%s Descrição:%s' %(item.content,desc)
        else:
            status = 'Anuncio Atualizado com Sucesso....'

        Anuncios[int(idAnuncio)] = dict(preco_alterado = 'N')

    else:
        status = 'Antes Faça o Login....'
        item = ''   

    response.flash = status
    response.js = "$('#anunciospublicar').get(0).reload()"

    return 

@auth.requires_membership('admin')
def importar_anuncios():

    form = SQLFORM.factory(
        Field('anuncio_id','string',label='Id do Anuncio:'),
        Field('offset','integer',label='Inicio:', default=0),
        Field('limit','integer',label='Quantidade:',default=50),
        table_name='importaranuncio',
        submit_button='Carregar Anuncios',
        )

    xitens = []
    btnAtualizar = ''

    if form.process().accepted:

        anuncio_id = form.vars.anuncio_id
        offset = form.vars.offset
        limit = form.vars.limit 

        # Cunsulta de itens na Api do mercado livre
        xitens = buscar_anuncio(anuncio_id,offset,limit)
        
        atualizar_anuncios(xitens)
        
    elif form.errors:
        response.flash = 'Erro no Formulário'

    return dict(form=form,itens = xitens,btnAtualizar=btnAtualizar)

@auth.requires_membership('admin')
def buscar_anuncio(item_id=None,offset=0,limit=50):

    import json
    xitens = []
    
    from meli import Meli
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)

    if item_id: 
        argsItem = "items/%s" %(item_id)
        busca = meli.get(argsItem,{'access_token':session.ACCESS_TOKEN})

        if busca.status_code == 200:
            itens = json.loads(busca.content)    
            xitens.append(itens)
    else:
        argsItem = "sites/MLB/search?seller_id=%s&offset=%s&limit=%s" %(USER_ID,offset,limit)
        busca = meli.get(argsItem)
        
        if busca.status_code == 200:
            itens = json.loads(busca.content)    
            xitens = itens['results']
    return xitens

@auth.requires_membership('admin')
def multiplos():
    # Cunsulta de itens na Api do mercado livre
    import json
    from meli import Meli
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
    xitens = []
    rows = db(Anuncios.forma == 'Multiplos').select()
    for row in rows:
        anuncio_id = row.item_id
        argsItem = "items/%s" %(anuncio_id)
        busca = meli.get(argsItem)
        
        if busca.status_code == 200:
            itens = json.loads(busca.content)    
            xitens.append(itens)
    
    atualizar_anuncios(xitens)
    return

@auth.requires_membership('admin')
def atualizar_anuncios(xitens):

    #Loop nos itens encontrados
    for item in xitens: 

        # Verifica Tipo de Frete
        if item['shipping']['free_shipping'] == False:
            frete = 'comprador'
        else:
            frete = 'gratis'
        
        # Buscar Categorias
        categoria = buscar_categoria(item['category_id'])  

        # Salvar Categorias
        Categorias.update_or_insert(Categorias.categoria_id == item['category_id'],
                categoria = categoria['categoria'],
                categoria_id = item['category_id'],
                frete = categoria['valorFrete'],
                )
        
        #### Calculando Desconto ####
        anuncio = db(Anuncios.item_id == item['id']).select().first()
        try:
            idAnuncio = anuncio.id
            desconto = anuncio.desconto
            preco = item['price']
            precoSugerido = sugerido(anuncio)['preco']
            desc = round((1-(float(preco)*(1-float(desconto/100)))/float(precoSugerido))*100,2)
        except:
            desc = 0

        valorfrete = buscar_valor_frete(item['id'])
        
        # Salvar Anuncios
        Anuncios.update_or_insert(Anuncios.item_id == item['id'],
                item_id=item['id'],
                titulo=item['title'],
                categoria=item['category_id'],
                preco=item['price'],
                estoque=item['available_quantity'],
                tipo=item['listing_type_id'],
                frete = frete,
                desconto = desc,
                status = 'active',
                fretegratis = valorfrete,
                vendido = item['sold_quantity']

                )

		# Salvar Atributos
        for atributo in item['attributes'] :
            idAnuncio = int(db(Anuncios.item_id == item['id']).select().first()['id'])
            #salva atributos na tabele atributos
            id = Atributos.update_or_insert(Atributos.atributo_id == atributo['id'],
                atributo_id = atributo['id'],
                nome = atributo['name'],
                )
            idAtributo = int(db(Atributos.atributo_id==atributo['id']).select().first()['id'])
            #salvar atributos na tabela anucios_atributos
            Anuncios_Atributos.update_or_insert((Anuncios_Atributos.anuncio == idAnuncio) & (Anuncios_Atributos.atributo == idAtributo),
                anuncio = idAnuncio,
                atributo = idAtributo,
                valor =  atributo['value_name']
                )

		# Salvar Variações
        if item['variations']:
            c=0
            for variacao in item['variations']:
                c =c +1
                query = (Anuncios_Produtos.variacao_id == variacao['id'])
                anunciosProdutos = db(query).select().first()
                try:
                    Anuncios_Produtos[anunciosProdutos['id']] = dict(variacao_id = variacao['id'],imagens_ids = variacao['picture_ids'],quantidade = variacao['available_quantity'] )
                except: 
                    pass
                Anuncios.update_or_insert(Anuncios.item_id == item['id'],qtevar = c)
		

		# Salvar Variações
		
        if item['variations']:
            for variacao in item['variations']:
            
                for atributo in variacao['attribute_combinations']:
                    query = (Anuncios_Produtos.anuncio ==idAnuncio) & (db.produtos.id == Anuncios_Produtos.produto) & (db.produtos.variacao == atributo['value_name'])    
                    anunciosProdutos = db(query).select().first()
                    try:
                        anunciosProdutosId = anunciosProdutos['anuncios_produtos']['id']
                        Anuncios_Produtos[anunciosProdutosId] = dict(variacao_id = variacao['id'],imagens_ids = variacao['picture_ids'],quantidade = variacao['available_quantity'] )
                    except: 
                        pass		

@auth.requires_membership('admin')
def buscar_valor_frete(item_id):
    import json
    valorfrete = 0
    from meli import Meli
    args = "/items/%s/shipping_options/free" %(item_id)
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
    busca = meli.get(args)
    if busca.status_code == 200:
        frete = json.loads(busca.content)
        valorfrete = frete['coverage']['all_country']['list_cost']
    return valorfrete

@auth.requires_membership('admin')
def imagem_upload(idAnuncio):
    #### Buscando as Imagens do Anuncio ####
    import os
    imagensIds = db(Anuncios_Imagens.anuncio == idAnuncio).select()
    imagens = []
    for anuncioImagem in imagensIds:
        if not anuncioImagem.imagem_id:
            imagem = Imagens[anuncioImagem.imagem]
            img = str(imagem.imagem)
            image = os.path.join(request.folder,'uploads', img)
            imagens.append(dict(file=image, id = anuncioImagem['id']))
      
    if session.ACCESS_TOKEN:
        from meli import Meli 
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
        for file in imagens:
            imag = meli.imagem("/pictures", file['file'], {'access_token':session.ACCESS_TOKEN})
            status = 'Anunciado com Sucesso....'         
            import json
            ximg = json.loads(imag.content)    
            Anuncios_Imagens[file['id']] = dict(imagem_id=ximg['id'])
            
    else:
        status = 'Antes Faça o Login....'
        item = ''    
    
    #### Buscando Ids das Imagens do Anuncio ####
    anuncioImagens = db(Anuncios_Imagens.anuncio == idAnuncio).select()
    imagens = []
    for imagem in anuncioImagens:
        if imagem.imagem_id:
            img = imagem.imagem_id
            imagens.append(dict(id=img))

    return imagens

@auth.requires_membership('admin')
def sincronizar_anuncios():
    
    form = FORM.confirm('Sincronizar Anuncios',{'Voltar':URL('default','index')})

    if form.accepted:
        import json
        from meli import Meli
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)

        anuncios = db(Anuncios.id >0).select()
        for anuncio in anuncios:
            xitens = []
            # Cunsulta de itens na Api do mercado livre
            argsItem = "items/%s" %(anuncio.item_id)
            busca = meli.get(argsItem,{'access_token':session.ACCESS_TOKEN})
            
            if busca.status_code == 200:
                itens = json.loads(busca.content)    
                xitens.append(itens)
                try:
                    atualizar_anuncios(xitens)
                except Exception as e:
                    print itens               

        response.flash = 'Anuncios Atualizado com Sucesso....'

    return dict(form=form)

@auth.requires_membership('admin')
def atualizar_sku():

	if session.ACCESS_TOKEN:
		from meli import Meli 
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

		anuncios = db(Anuncios.item_id != '').select()
		#anuncios = db(Anuncios.item_id == 'MLB1088889262').select()
		for anuncio in anuncios:

			atributos = []
			buscaAtributos = db(Anuncios_Atributos.anuncio == anuncio.id).select()

			for atributo in buscaAtributos:
				atributo_id = Atributos(atributo.atributo).atributo_id
				if atributo_id == "ITEM_CONDITION" and anuncio.item_id:
					pass
				else:
					atributos.append(dict(id=atributo_id, value_name=atributo.valor))

			sku = '%05d' % anuncio.id
			body = dict(attributes=atributos)
			item_args = "items/%s" %(anuncio['item_id'])	
			item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
			if item.status_code != 200:
				print '%s - %s - %s' %(anuncio['item_id'],anuncio['id'] ,item)
			else:
				status = 'Antes Faça o Login....'
	return 

@auth.requires_membership('admin')
def sku():

	anuncios = db(Anuncios.id>0).select()
	for anuncio in anuncios:
		sku = '%05d' % anuncio.id
		query = (Anuncios_Atributos.anuncio == anuncio.id) & (Anuncios_Atributos.atributo == 313)
		Anuncios_Atributos.update_or_insert(query,
											anuncio = anuncio.id,
											atributo = 313,
											valor = sku
											)

@auth.requires_membership('admin')
def sku1():
    #id produto
    anuncios = db(Anuncios.forma != 'Multiplos').select()
    for anuncio in anuncios:
        try:
            idProduto = db(Anuncios_Produtos.anuncio == anuncio.id).select().first()['produto']
            sku = '%05d' %(idProduto)
            query = (Anuncios_Atributos.anuncio == anuncio.id) & (Anuncios_Atributos.atributo == 313)
            Anuncios_Atributos.update_or_insert(query,
                                                anuncio = anuncio.id,
                                                atributo = 313,
                                                valor = sku
                                                )        
        except:
            pass

@auth.requires_membership('admin')
def dadosfiscais(idProduto):

    if session.ACCESS_TOKEN:
        from meli import Meli 
        meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

        produto = db(db.produtos.id == idProduto).select().first()
        sku = '%05d' % idProduto

        if produto.cst == '60':
        	csosn = '500'
        else:
        	csosn = '102'

        tax_information = dict(
        ncm= produto.ncm,
        origin_type= 'reseller',
        origin_detail= produto.origem,
        tax_rule_id= '',
        csosn= csosn,
        cest= '',
        ean= produto.ean, 
        )

        dados_put = dict(
            title= produto.nome,
            type= "single",
            cost= 0,
            tax_information = tax_information,
            )
        dados_post = dict(
            sku= sku,
            title= produto.nome,
            type= "single",
            cost= 0,
            tax_information = tax_information,
            )

        item_args_post = "items/fiscal_information" 
        item_post = meli.post(item_args_post, dados_post, {'access_token':session.ACCESS_TOKEN})
        
        if item_post.status_code != 200:
            item_args_put = "items/fiscal_information/%s" %(sku)
            item_put = meli.put(item_args_put, dados_put, {'access_token':session.ACCESS_TOKEN})
            if item_put.status_code != 200:
                print '%s - %s' %(produto.nome ,item_put)
    else:
        status = 'Antes Faça o Login....'
    return 

@auth.requires_membership('admin')
def vicular_sku():
	if session.ACCESS_TOKEN:
		from meli import Meli 
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
		anuncios = db(Anuncios.forma != 'Multiplos').select(orderby =~ Anuncios.vendido, limitby=(200, 100))
		#anuncios = db(Anuncios.item_id == 'MLB988433434').select()    
		for anuncio in anuncios:
			try:
				idProduto = db(Anuncios_Produtos.anuncio == anuncio.id).select().first()['produto']
				dadosfiscais(idProduto)
				args = "items/fiscal_information/items"
				sku = '%05d' %(idProduto)
				body = dict(sku = sku,
							item_id = anuncio.item_id,
							variation_id = ""
							)
				item_post = meli.post(args, body, {'access_token':session.ACCESS_TOKEN})
			except:
				pass
	return

@auth.requires_membership('admin')
def atualizar_produtos():
	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()
	# Buscar produto banco firebird
	produtos = db(db.produtos.id > 0).select()
	for row in produtos:
		select = "select CODPRO,ORIPRO,CLAFIS,SITDEN FROM PRODUTOS WHERE CODPRO = {}".format(row.id)
		produto = cur.execute(select).fetchone()
		try:
			db.produtos[int(row.id)] = dict(origem=produto[1],ncm=produto[2], cst=produto[3])
		except:
			pass

@auth.requires_membership('admin')
def curva_abc():

    curva = ''

    form = SQLFORM.factory(
        Field('dtInicial','date',requires = data, label='Data Inicial'),
        Field('dtFinal','date',requires = data, label ='Data Final'),
        table_name='curva',
        submit_button='Gerar',
        )
    
    if form.process().accepted:

        dtInicial = form.vars.dtInicial
        dtFinal = form.vars.dtFinal

        sum = Pedidos_Itens.quantidade.sum()
        #(Pedidos.date_created >= '2020-01-01')
        try: 
            query = (Pedidos.date_created >= dtInicial) & (Pedidos.date_created <= dtFinal) & (Pedidos.id == Pedidos_Itens.shipping_id) & (Anuncios.item_id == Pedidos_Itens.item_id)
            abc = db(query).select(Anuncios.titulo, Anuncios.preco, Pedidos_Itens.item_id, sum.with_alias('total'), groupby =  Pedidos_Itens.item_id, orderby =~ sum)
        except:
            curva = ''
        else:
            curva = []
            c = 0
            t = 0
            for r in abc:
                c = c+1
                total = round(float(r.total) * float(r.anuncios.preco), 2)
                t = t + total
                row = dict(
                    id = c,
                    anuncio = r.anuncios.titulo,
                    quantidade = r.total,
                    preco = r.anuncios.preco,
                    total = total,
                    acumulado = t 
                    )
                curva.append(row)
                db(Anuncios.item_id==r.pedidos_itens.item_id).update(vendido=r.total)

    return dict(curva = curva, form = form)

