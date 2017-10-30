# -*- coding: utf-8 -*-

def selecionar_produtos():
    fields = [Produtos.id,Produtos.nome]

    selectable = [('Adcionar Produtos', lambda ids:
    								   redirect(URL('cadastro','adiciona_produto',vars=dict(ids=ids,url="#"))))]

    formPesquisa = grid(Produtos,50,fields=fields,orderby=Produtos.nome,create=False,editable=False,
                deletable=False,selectable=selectable)

    return dict(formPesquisa=formPesquisa)