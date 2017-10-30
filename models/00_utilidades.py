def voltar(url):
    return A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",_href=URL(url))

def voltar1(target):
    return A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                 _onClick="jQuery(%s).get(0).reload()" %(target))
def voltar2():
    return A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                 _onClick="history.back()")
def excluir(url):
    return A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger", _href=url)
def novo(url):
    return A(SPAN(_class="glyphicon glyphicon-plus"), ' Novo ', _class="btn btn-info",_href=URL(url))
def proximo(url,id):
    return A(' Proximo ', SPAN(_class="glyphicon glyphicon-chevron-right"),  _class="btn btn-info",_href=URL(url,args=id))    
def anterior(url,id):
    return A(SPAN(_class="glyphicon glyphicon-chevron-left"), ' Anterior ', _class="btn btn-info",_href=URL(url,args=id))    
def pesquisar(controle,funcao,titulo):
    return A(SPAN(_class="btn btn-default glyphicon glyphicon-search"),'',_type="button",_id='pesquisar',
    _onclick="show_modal('%s','%s');" %(URL(controle,funcao,vars={'reload_div':'map'}),titulo))
def email(idcompra):
    return A(SPAN(_class="glyphicon glyphicon-file"),' Email',_class="btn btn-info",_id='email',
    _onclick="show_modal('%s','%s');" %(URL('pagar','enviarEmail',vars=dict(reload_div='map',id_compra=idcompra)),'Enviar Email de Pedido de Compra'))
def pdf(url,idpagar):
    return A(SPAN(_class="glyphicon glyphicon-file"), ' PDF ', _class="btn btn-info",_href=URL(url,vars=dict(id_pagar=idpagar)),_target = "_blank" )

def adicionar(controle,funcao,titulo):
    return A(SPAN(_class="glyphicon glyphicon-plus"),titulo,_class="btn btn-default",_id='adcionar',
    _onclick="show_modal('%s','%s');" %(URL(controle,funcao,vars={'reload_div':'map'}),titulo))

def grid(query,maxtextlength=50,**kwargs):
    
    grid = SQLFORM.grid(query,
                        user_signature=False,
                        showbuttontext=False,
                        csv=None,
                        maxtextlength=maxtextlength,
                        details=False,
                        paginate=100,
                        **kwargs)
    try:
        grid.element('.web2py_grid .web2py_table .web2py_htmltable')['_style'] = 'overflow: scroll; height:300px;'
    except Exception as e:
        pass   
    
    return grid

def lista_arquivos_imagem(caminho):
    """
    Retorna lista de arquivos de imagens encontrados no caminho espeficicado
    :param caminho: caminho para procurar imagens
    :return: lista de arquivos
    """
    import os
    arquivos = os.listdir(caminho)
    arquivos_tmp = []
    for file_name in arquivos:
            arquivos_tmp.append(file_name)

    image_extensions = ['bmp', 'pbm', 'pgm', 'ppm', 'sr', 'ras', 'jpeg', 'jpg', 'jpe', 'jp2', 'tiff', 'tif', 'png']
    # filtar somente os arquivos que contenham as extensões de imagens compatíves com opencv
    arquivos = ['%s%s.%s' % f for f in arquivos_tmp if f[2] in image_extensions]
    return arquivos
