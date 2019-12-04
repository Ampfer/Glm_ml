# -*- coding: utf-8 -*-
def produtos_atualizar():
    produtos = db(Produtos.familia != None).select()
    for produto in produtos:
        print produto
        Familias_Produtos.update_or_insert(Familias_Produtos.familia==produto.familia and Familias_Produtos.produto == produto.id,
            familia=produto.familia,
            produto= produto.id)
    
def empresa():
    idEmpresa = db(Empresa.id == 1).select().first() or "0"

    if idEmpresa == "0":
        formEmpresa = SQLFORM(Empresa,field_id='id', _id='formEmpresa')

    else:
        formEmpresa = SQLFORM(Empresa,idEmpresa,_id='idEmpresa',field_id='id')

    if formEmpresa.process().accepted:
        response.flash = 'Salvo com Sucesso!'
        redirect(URL('empresa', args=formEmpresa.vars.id))

    elif formEmpresa.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formEmpresa=formEmpresa)

def clientes():
    fields = (Clientes.id,Clientes.nome)
    formClientes = grid(Clientes,formname="formClienteCompras",fields=fields)
            
    formClientes = DIV(formClientes, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('cliente'))
    elif request.args(-3) == 'edit':
       idCliente = request.args(-1)
       redirect(URL('cliente', args=idCliente ))

    return locals()

def cliente():

    idCliente = request.args(0) or "0"

    if idCliente == "0":
        formCliente = SQLFORM(Clientes,field_id='id', _id='formCliente')

        btnNovo=btnExcluir=btnVoltar = ''
        formClienteCompras = "Primeiro Cadastre um Cliente"
    else:
        formClienteCompras = " "
        formCliente = SQLFORM(Clientes,idCliente,_id='formCliente',field_id='id')

        btnExcluir = excluir("#")
        btnNovo = novo("cliente")

    btnVoltar = voltar("clientes")

    if formCliente.process().accepted:
        response.flash = 'Cliente Salvo com Sucesso!'
        redirect(URL('cliente', args=formCliente.vars.id))

    elif formCliente.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formCliente=formCliente,btnExcluir=btnExcluir, btnVoltar=btnVoltar, btnNovo=btnNovo, formClienteCompras=formClienteCompras)

def marcas():
    def teste(table,id):
        print 'xxx',formMarcas.errors
    formMarcas = grid(Marcas,ondelete = teste)
    if request.args(-2) == 'new':
        redirect(URL('marca'))
    elif request.args(-3) == 'edit':
        idMarca = request.args(-1)
        redirect(URL('marca',args=idMarca))
    return dict(formMarcas=formMarcas)

def marca():
    idMarca = request.args(0) or "0"
    
    import os
   
    if idMarca == "0":       
        formMarca = SQLFORM(Marcas,field_id='id', _id='formMarca', upload=URL('download'))
        btnNovo=btnExcluir=btnVoltar = ''
        imagem = A(IMG(_src=URL('static/images','img_camera_ico_retina.png'),_class="img-thumbnail",
            _width="150",_height="100"),_href=URL('selecionar_imagem'))
        
    else:
        formMarca = SQLFORM(Marcas,idMarca,_id='formMarca',field_id='id', upload=URL('download'))
        btnExcluir = excluir("#")
        btnNovo = novo("marca")
        #url = URL('download',args=[Marcas[idMarca].imagem])
        url = URL('static/imagens',Marcas[idMarca].logo)
        imagem = A(IMG(_src=url,_class="img-thumbnail",_width="150",_height="100"),_href=URL('selecionar_imagem'))


    btnVoltar = voltar("marcas")

    if formMarca.process().accepted:
        response.flash = 'Marca Salva com Sucesso!'
        redirect(URL('marca', args=formMarca.vars.id))

    elif formMarca.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formMarca=formMarca, btnNovo=btnNovo,btnVoltar=btnVoltar,btnExcluir=btnExcluir,imagem=imagem)

def produtos():

    fields = (Produtos.id,Produtos.nome,Produtos.atributo,Produtos.variacao,Produtos.estoque,Produtos.largura, Produtos.altura,Produtos.comprimento, Produtos.peso)
    formProdutos = grid(Produtos,formname="produtos",fields=fields,create=False,deletable=False)
            
    formProdutos = DIV(formProdutos, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('produto'))
    elif request.args(-3) == 'edit':
       idProduto = request.args(-1)
       redirect(URL('produto', args=idProduto))

    return dict(formProdutos=formProdutos)

def produto():
    idProduto = request.args(0) or "0"

    if idProduto == "0":
        formProduto = SQLFORM(Produtos,field_id='id', _id='formProduto')
        formProdutoDescricao  = formProdutoImagem = 'Primeiro Cadastre uma Familia'
    else:
        formProduto = SQLFORM(Produtos,idProduto,_id='formProduto',field_id='id')
        formProdutoDescricao = LOAD(c='cadastro',f='produtos_descricao',args=[idProduto], target='produtosdescricao', ajax=True,)       
        formProdutoImagem = LOAD(c='cadastro', f='produtos_imagens',args=[idProduto], target='produtoimagem', ajax=True)

    btnVoltar = voltar("produtos")
    formProduto.element(_name='nome')['_readonly'] = "readonly"

    if formProduto.process().accepted:
        response.flash = 'Produto Salvo com Sucesso!'
        redirect(URL('produto', args=formProduto.vars.id))

    elif formProduto.errors:
        formProduto.element('#produtos_familia')['_class'] += ' form-control'
        response.flash = 'Erro no Formulário Principal!'

    return dict(formProduto=formProduto,formProdutoDescricao = formProdutoDescricao,
                formProdutoImagem=formProdutoImagem,btnVoltar=btnVoltar)

def produtos_descricao():
    
    idProduto = int(request.args(0))
    idDescricao = Produtos[idProduto].descricao
    if idDescricao == None:
      formDescricao = SQLFORM(Descricoes,field_id='id', _id='formdescricao')
    else:
      formDescricao = SQLFORM(Descricoes,idDescricao,field_id='id', _id='formdescricao')

    if formDescricao.process().accepted:
        response.flash = 'Salvo !'
        Produtos[idProduto] = dict(descricao=int(formDescricao.vars.id))
        response.js = "$('#produtsdescricao').get(0).reload()"

    elif formDescricao.errors:
        response.flash = 'Erro no Formulário !' 

    return dict(formDescricao=formDescricao)

def produtos_imagens():
    idProduto = int(request.args(0))
    formImagem = SQLFORM(Imagens)
    if formImagem.process().accepted:
        Produtos_Imagens[0] = dict(familia=idProduto, imagem = formImagem.vars.id)
        response.flash = 'Salvo !'
    elif formImagem.errors:
        response.flash = 'Erro no Formulário !' 
    query = (Produtos_Imagens.produto == idProduto) & (Produtos_Imagens.imagem==Imagens.id)
    imagens = db(query).select()

    return dict(formImagem=formImagem, imagens=imagens)
    
def remove_imagem_produto():
    idImagem = int(request.args(0))
    del Produtos_Imagens[idImagem]
    response.js = "$('#produtoimagem').get(0).reload()"

def familias():

    fields = (Familias.id,Familias.nome, Familias.catalogo,Familias.web)
    selectable = [('Exportar Familias', lambda ids: redirect(URL('ferramentas','exportar_produtos',vars=dict(ids=ids)))),]            
    formFamilias = grid(Familias,formname="familias",fields=fields,deletable=False, orderby= Familias.nome,selectable=selectable)
    #session.teste = False


    formFamilias = DIV(formFamilias, _class="well")

    if request.args(-2) == 'new':
       redirect(URL('familia'))
       
    elif request.args(-3) == 'edit':
       session.keywords = request.vars.keywords
       idFamilia = request.args(-1)
       redirect(URL('familia', args=idFamilia))

    return dict(formFamilias=formFamilias)


def familia():

    idFamilia = request.args(0) or "0"
    img = "%s.png" %(str(db(Familias.id>0).select().last()['id']+1).zfill(4))
    Familias.imagem.default = img
    Familias.catalogo.default = 'S'
    Familias.web.default = 'S'

    if idFamilia == "0":
        formFamilia = SQLFORM(Familias,field_id='id', _id='formFamilia')
        formFamiliaDescricao = formFamiliaProdutos = formFamiliaImagem = 'Primeiro Cadastre uma Familia'
        url= URL('static/images','img_camera_ico_retina.png')
        imagem = A(IMG(_src=url,_class="img-responsive",
            _width="180",_height="180"))
    else:
        formFamilia = SQLFORM(Familias,idFamilia,_id='formFamilia',field_id='id',)
        formFamiliaDescricao = LOAD(c='cadastro',f='familias_descricao',args=[idFamilia], target='familiasdescricao', ajax=True,)
        formFamiliaProdutos = LOAD(c='cadastro', f='familia_produtos',args=[idFamilia], target='familiaprodutos', ajax=True)
        formFamiliaImagem = LOAD(c='cadastro', f='familias_imagens',args=[idFamilia], target='familiaimagem', ajax=True)
        url = URL('static/imagens',Familias[idFamilia].imagem)

        imagem = A(IMG(_src=url,_class="img-responsive"),)
    
    btnVoltar = voltar("familias")
    btnProximo=btnAnterior=''

    if formFamilia.process().accepted:
        import os
        image = os.path.join(request.folder,'static','imagens', formFamilia.vars.imagem)
        if db(Familias_Imagens.familia==idFamilia).count() == 0:
            try:
                id = Imagens.insert(imagem = open(image,'rb'))
                Familias_Imagens[0] = dict(familia=idFamilia, imagem = id)
            except:
                pass

        
        response.flash = 'familia Salvo com Sucesso!'
        redirect(URL('familia', args=formFamilia.vars.id))

    elif formFamilia.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(url=url,formFamilia=formFamilia,formFamiliaProdutos=formFamiliaProdutos, formFamiliaDescricao=formFamiliaDescricao,
        formFamiliaImagem=formFamiliaImagem,btnVoltar=btnVoltar,imagem=imagem,btnProximo=btnProximo, btnAnterior=btnAnterior)

def familias_descricao():
    
    idFamilia = int(request.args(0))
    idDescricao = Familias[idFamilia].descricao
    if idDescricao == None:
      formDescricao = SQLFORM(Descricoes,field_id='id', _id='formdescricao')
    else:
      formDescricao = SQLFORM(Descricoes,idDescricao,field_id='id', _id='formdescricao')

    if formDescricao.process().accepted:
        response.flash = 'Salvo !'
        Familias[idFamilia] = dict(descricao=int(formDescricao.vars.id))
        response.js = "$('#familiasdescricao').get(0).reload()"

    elif formDescricao.errors:
        response.flash = 'Erro no Formulário !' 

    return dict(formDescricao=formDescricao)
'''
def familia_produtos():

    session.idFamilia = int(request.args(0))

    btnAdicionar = adicionar('cadastro','selecionar_produtos',' Adicionar Produtos')
      
    query = (Produtos.familia == session.idFamilia)
    fields= [Produtos.id,Produtos.nome,Produtos.preco, Produtos.estoque]
    links = [lambda row: A('remover',_onclick="return confirm('Deseja Remover Produto ?');",callback=URL('cadastro', 'remove_produto', args=[row.id]))]
    formProdutos = grid(query,orderby=Produtos.nome,args=[session.idFamilia],fields=fields,
                             create=False,editable=False,deletable = False,searchable=False,
                             links=links,formname="familiaprodutos")
    
    return dict(btnAdicionar=btnAdicionar,formProdutos=formProdutos)
'''
def familia_produtos():

    session.idFamilia = int(request.args(0))

    btnAdicionar = adicionar('cadastro','selecionar_produtos',' Adicionar Produtos')

    links=[dict(header='Editar',
                body=lambda row: A(TAG.button(I(_class='glyphicon glyphicon-edit')),
               _href=URL('produto',args=row.id)))] 

    query = (Familias_Produtos.familia == session.idFamilia) & (Produtos.id == Familias_Produtos.produto)
    fields= [Produtos.id,Produtos.nome,Produtos.atributo,Produtos.variacao,Produtos.preco, Produtos.estoque]
    #links = [lambda row: A('remover',_onclick="return confirm('Deseja Remover Produto ?');",callback=URL('cadastro', 'remove_produto', args=[row.id]))]
    formProdutos = grid(db(query),orderby=Produtos.nome,args=[session.idFamilia],fields=fields,
                             create=False,editable=False,deletable = True,searchable=False,
                             formname="familiaprodutos",links=links)

    
    return dict(btnAdicionar=btnAdicionar,formProdutos=formProdutos)

def selecionar_produtos():

    fields = [Produtos.id,Produtos.nome]

    selectable = [('Adcionar Produtos', lambda ids: redirect(URL('adiciona_produto',vars=dict(ids=ids)))),]

    formPesquisa = grid(Produtos,50,fields=fields,orderby=Produtos.nome,create=False,editable=False,
                deletable=False,selectable=selectable,formname="pesquisa")

    return dict(formPesquisa=formPesquisa)

def adiciona_produto():

    if type(request.vars.ids) is list:
        ids = request.vars.ids
    else:
        ids = []
        ids.append(request.vars.ids)

    for idProduto in ids:
        Familias_Produtos.update_or_insert(Familias_Produtos.familia==session.idFamilia and Familias_Produtos.produto == idProduto,
            familia=session.idFamilia,
            produto=idProduto)

#    for idProduto in ids:
#        Produtos[idProduto] = dict(familia=session.idFamilia)
    
    redirect(request.env.http_web2py_component_location,client_side=True)    
   
def remove_produto():
    idProduto = int(request.args(0))
    Produtos[idProduto] = dict(familia=None)
    response.js = "$('#familiaProdutos').get(0).reload()"

def familias_imagens():
    idFamilia = int(request.args(0))
    formImagem = SQLFORM(Imagens)
    if formImagem.process().accepted:
        Familias_Imagens[0] = dict(familia=idFamilia, imagem = formImagem.vars.id)
        response.flash = 'Salvo !'
    elif formImagem.errors:
        response.flash = 'Erro no Formulário !' 
    query = (Familias_Imagens.familia == idFamilia) & (Familias_Imagens.imagem==Imagens.id)
    imagens = db(query).select()

    return dict(formImagem=formImagem, imagens=imagens)
    
def remove_imagem():
    idImagem = int(request.args(0))
    del Familias_Imagens[idImagem]
    response.js = "$('#familiaimagem').get(0).reload()"

def selecionar_imagem():
    import os
    caminho = os.path.join('applications','glm_ml', 'static','imagens')
    arquivos = os.listdir(caminho)
    return dict(arquivos=arquivos, caminho=caminho)

def atributos():
    fields = (Atributos.atributo_id, Atributos.nome,)
    formAtributos = grid(Atributos, formname = 'categoriaatributos',)
    return dict(formAtributos=formAtributos)

def nome_imagem():
    rows = db(Familias.marca == 37).select()
    for row in rows:
        img = str(row.imagem)
        imagem = img.replace('web','').replace('png','jpg')
        Familias[row.id] = dict(imagem = imagem)

def atualiza_imagem():
    import os
    rows = db(Familias.id > 0).select()
    for row in rows:
        image = os.path.join(request.folder,'static','imagens', row.imagem)
        if db(Familias_Imagens.familia==row.id).count() == 0:
            try:
                id = Imagens.insert(imagem = open(image,'rb'))
                Familias_Imagens[0] = dict(familia=row.id, imagem = id)
            except:
                pass
       
def importar_imagem_produto():
    produtos = db(Produtos.id >0).select(orderby=Produtos.id)

    for produto in produtos:
        anuncio = db(Anuncios_Produtos.produto == produto.id).select().first()
        if anuncio:
            anuncioId = anuncio['anuncio']
            imagens = db(Anuncios_Imagens.anuncio == anuncioId).select()
            for imagem in imagens:
                print produto.id, anuncioId, imagem.id
                query = (Produtos_Imagens.produto==produto.id) & (Produtos_Imagens.imagem == imagem.imagem)
                Produtos_Imagens.update_or_insert(
                    query ,
                    produto = produto.id, 
                    imagem = imagem.imagem)

def importar_descricao_produtos():

    produtos = db(Produtos.id >0).select(orderby=Produtos.id)

    for produto in produtos:
        anuncio = db(Anuncios_Produtos.produto == produto.id).select().first()
        if anuncio:
            anuncioId = anuncio['anuncio']
            descricaoId = db(Anuncios.id == anuncioId).select().first()['descricao']
            if descricaoId:
                Produtos[produto.id] = dict(descricao = descricaoId)
            else:
                familiaId = db(Anuncios.id == anuncioId).select().first()['familia']
                descricaoId = db(Familias.id == familiaId).select().first()['descricao']
                descricao = Descricoes[descricaoId].descricao
                if Produtos[produto.id].descricao:
                    pass
                else:
                    id = Descricoes.insert(descricao=descricao)
                    Produtos[produto.id] = dict(descricao = id)
