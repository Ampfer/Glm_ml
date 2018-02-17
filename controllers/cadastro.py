# -*- coding: utf-8 -*-

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

    fields = (Produtos.id,Produtos.nome,Produtos.atributo,Produtos.variacao,Produtos.ean)
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
    else:
        formProduto = SQLFORM(Produtos,idProduto,_id='formProduto',field_id='id')

    btnVoltar = voltar("produtos")
    formProduto.element(_name='nome')['_readonly'] = "readonly"

    if formProduto.process().accepted:
        response.flash = 'Produto Salvo com Sucesso!'
        redirect(URL('produto', args=formProduto.vars.id))

    elif formProduto.errors:
        formProduto.element('#produtos_familia')['_class'] += ' form-control'
        response.flash = 'Erro no Formulário Principal!'

    return dict(formProduto=formProduto,btnVoltar=btnVoltar)

def familias():

    fields = (Familias.id,Familias.nome)
    formFamilias = grid(Familias,formname="familias",fields=fields,deletable=False, orderby= Familias.nome)
    session.teste = False
            
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


    # id Próxima Familia
    query1 = (Familias.nome > Familias[idFamilia].nome)
    #if session.keywords:
    #    query1 = query1 & session.keywords

    rowP = db(query1).select(orderby=Familias.nome).first()
    try:
        idProximo = rowP.id
    except:
        idProximo = idFamilia
        response.flash = 'Último Registro...'    

    # id Familia Anterior
    query2 = (Familias.nome < Familias[idFamilia].nome)
    #query2 = query2 & session.keywords if session.keywords else query2
    rowA = db(query2).select(orderby=~Familias.nome).first()
    try:
        idAnterior = rowA.id 
    except:
        idAnterior = idFamilia
        response.flash = 'Primeiro Registro...'

    
    btnProximo = proximo('familia',idProximo)
    btnAnterior = anterior('familia',idAnterior)
   
    #formFamilia.element(_name='nome')['_readonly'] = "readonly"
    #formFamilia.element(_name='atributos')['_readonly'] = "readonly"

    if formFamilia.process().accepted:
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
        Produtos[idProduto] = dict(familia=session.idFamilia)
    
    #response.js = "$('#janela-modal').modal('hide');$('#familiaprodutos').get(0).reload();"
    #response.js = "web2py_component('%s','familiaprodutos')" %(URL('familia_produtos',args=session.idFamilia))
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
    

       
