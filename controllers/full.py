def envios_full_lista():

    grid_envios = grid(Envios_Full,formname="lista_envios",orderby=~Envios_Full.data_envio)

    if request.args(-2) == 'new':
       redirect(URL('envios_full'))
    elif request.args(-3) == 'edit':
       idd = request.args(-1)
       redirect(URL('envios_full', args=idd ))

    return dict(grid_envios=grid_envios)

def envios_full():
    id_envio = request.args(0) or "0"

    if id_envio == "0":
        Envios_Full.data_envio.default= request.now.date()

        form_envio = SQLFORM(Envios_Full,field_id='id',_id='form_envio')

        form_itens = form_produtos = ''
        btnExcluir = btnNovo = ''
        
    else:
        form_envio = SQLFORM(Envios_Full,id_envio,_id='form_envio' ,field_id='id')

        form_itens = LOAD(c='full',f='envio_itens',args=[id_envio],
                     content='Aguarde, carregando...',target='itens',ajax=True)
        form_produtos = LOAD(c='full',f='envio_produtos',args=[id_envio],
             content='Aguarde, carregando...',target='produtos',ajax=True)

        btnExcluir = excluir("#")
        btnNovo = novo("envios_full")

    btnVoltar = voltar('envios_full_lista')

    if form_envio.process().accepted:
        if form_envio.vars.status == 'Concluido':
            anuncios = db(Envios_Itens.envio_id == form_envio.vars.id).select()
            for row in anuncios:
                Anuncios[int(row.anuncio_id)] = dict(localizacao = 'FULL')

        response.flash = 'Salvo com sucesso!'
        redirect(URL('envios_full', args=[form_envio.vars.id]))

    elif form_envio.errors:
        response.flash = 'Erro no Formulário Principal!'
    
    return locals()

def envio_itens():
    
    id_envio = int(request.args(0))

    Envios_Itens.envio_id.default = id_envio
    fields = [Envios_Itens.id,Envios_Itens.anuncio_id,Envios_Itens.quantidade]

    def salva_produto(form):

        produtos = db(Anuncios_Produtos.anuncio == form.vars.anuncio_id).select()
        for produto in produtos:
            query = (Envios_Produtos.envio_id == request.args[0]) & (Envios_Produtos.produtos_id == produto['produto'])
            Envios_Produtos.update_or_insert(query,
                envio_id = request.args[0],
                produtos_id = produto['produto'],
                quantidade = form.vars.quantidade
                )
        return

    def validacao(form):

        query = (Envios_Itens.envio_id == request.args[0]) & (Envios_Itens.anuncio_id == form.vars.anuncio_id) 
        existe = db(query).select()
        if existe and request.args[1] == 'new':
            form.errors = True
            response.flash = 'Anuncio já exite....!'
        return

    formItens = grid(Envios_Itens.envio_id==id_envio,
                    alt='250px',args=[id_envio],formname = "anuncios",
                    searchable = False, deletable=True,fields=fields, oncreate = salva_produto,
                    onupdate =salva_produto, onvalidation=validacao,maxtextlength=100
                    )

    btnVoltar = voltar1('itens')
    btnPesquisar = pesquisar('full','pesquisar_anuncio','Pesquisar Anuncio')

    if formItens.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return dict(formItens=formItens,btnExcluir=btnExcluir,btnVoltar=btnVoltar,btnPesquisar=btnPesquisar)

def pesquisar_anuncio():
    fields = [Anuncios.id,Anuncios.titulo,Anuncios.tipo,Anuncios.localizacao]
    links=[dict(header='Selecionar',
                body=lambda row: A(TAG.button(I(_class='glyphicon glyphicon-edit')),
               _href='#', _onclick="selecionar(%s);" %row.id))]

    ##pesq =grid(Anuncios,csv=False,details=False,maxtextlength=50,fields=fields,orderby=Anuncios.titulo,
    #   paginate=5,create=False,editable=False,deletable=False,links=links)
    pesq =grid(Anuncios,maxtextlength=100,fields=fields,orderby=Anuncios.titulo,
                        create=False,editable=False,deletable=False,links=links,alt='300px')

    return locals()

def envio_produtos():
    id_envio = int(request.args(0))
    
    formProdutos = grid(Envios_Produtos.envio_id==id_envio,
                    alt='250px',args=[id_envio],formname = "produtos",
                    searchable = False, deletable=False, editable = False, create = False)

    return dict(formProdutos = formProdutos)

def anuncios_full():

    Anuncios.full_glm = Field.Virtual('full_glm',lambda row: saldo_full(row.anuncios), label='Estoque Full')

    fields = [Anuncios.id,Anuncios.titulo,Anuncios.localizacao, Anuncios.estoque, Anuncios.full_glm]
    
    gridAnunciosFull = grid(Anuncios.localizacao == 'FULL',
                    alt='250px',args=[id],formname = "anunciosfull",maxtextlength=100,fields=fields,
                    searchable = True, deletable=False, editable = False, create = False,)

    return dict(gridAnunciosFull=gridAnunciosFull)

def saldo_full(anuncio):

    id = int(anuncio.id)

    query = (Envios_Itens.anuncio_id == id) & (Envios_Full.id == Envios_Itens.envio_id) & (Envios_Full.status == "Concluido")
    qt_envio = db(query).select(Envios_Itens.quantidade.sum()).first()[Envios_Itens.quantidade.sum()] or 0
    
    item_id = db(Anuncios.id == id).select(Anuncios.item_id).first()['item_id']
    print item_id
    
    query = (Pedidos.date_created >= '2020-02-01') & (Pedidos.logistica == 'fulfillment') & (Pedidos_Itens.shipping_id == Pedidos.id) & "(Pedidos_Itens.item_id == '{}')".format(item_id)
    qt_vendida = db(query).select(Pedidos_Itens.quantidade.sum()).first()[Pedidos_Itens.quantidade.sum()] or 0
    
    return float(qt_envio) - float(qt_vendida)

