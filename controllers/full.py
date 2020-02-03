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

        form_itens = ''
        btnExcluir = btnNovo = ''
        
    else:
        form_envio = SQLFORM(Envios_Full,id_envio,_id='form_envio' ,field_id='id')

        form_itens = LOAD(c='full',f='envio_itens',args=[id_envio],
                     content='Aguarde, carregando...',target='itens',ajax=True)

        btnExcluir = excluir("#")
        btnNovo = novo("entrada")

    btnVoltar = voltar('envios_full_lista')

    if form_envio.process().accepted:
        response.flash = 'Salvo com sucesso!'
        redirect(URL('envios_full', args=[form_envio.vars.id]))

    elif form_envio.errors:
        response.flash = 'Erro no Formulário Principal!'
    
    return locals()

def envio_itens():
    
    id_envio = int(request.args(0))

    Envios_Itens.envio_id.default = id_envio
    fields = [Envios_Itens.id,Envios_Itens.anuncio_id,Envios_Itens.quantidade]

    formItens = grid(Envios_Itens.envio_id==id_envio,
                    alt='250px',args=[id_envio],formname = "envioitem",
                    searchable = False, deletable=True,fields=fields
                    )

    btnVoltar = voltar1('itens')

    if formItens.update_form:
        btnExcluir = excluir("#")
    else:
        btnExcluir = ''

    return dict(formItens=formItens,btnExcluir=btnExcluir,btnVoltar=btnVoltar)