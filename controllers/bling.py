# -*- coding: utf-8 -*-

import csv

@auth.requires_membership('admin')
def importar_vinculo():

	form = SQLFORM.factory(Field('csvfile','upload',uploadfield=False,label='Arquivo Vínculos de Produto:',requires=notempty)
		,submit_button='Importar Vínculos')

	if form.process().accepted:
		if request.vars.csvfile != None:
			file =  request.vars.csvfile.file
			head = False
			for linha in file:
				if head:
					a,b,c,d,e,f,g,h,i = linha.split(';')

					id_bling = a.replace('"','')
					id_loja = b.replace('"','')
					id_produto = d.replace('"','')
					produto = c.replace('"','')
					loja = i.replace('"','')
					preco = float(e.replace('"','').replace(',','.'))
					preco_promocional = float(f.replace('"','').replace(',','.'))

					preco_tabela = db.produtos[int(id_produto)].preco

					query = (Vinculos.id_bling == id_bling) & (Vinculos.id_loja == id_loja ) & (Vinculos.id_produto == id_produto) & (Vinculos.loja == loja)

					Vinculos.update_or_insert(query,
						id_bling = id_bling,
						id_loja = id_loja,
						id_produto = id_produto,
						produto = produto,
						loja = loja,
						preco = preco,
						preco_promocional = preco_promocional,
						preco_tabela = preco_tabela
					)
				head = True

	return dict(form=form)

@auth.requires_membership('admin')
def produtos_multilojas():
    fields = (Vinculos.id_produto,Vinculos.produto, Vinculos.id_bling, Vinculos.id_loja, Vinculos.preco, Vinculos.preco_promocional, Vinculos.loja)
    gridProdutos = grid(Vinculos,formname="formVinculo",fields=fields)

    if request.args(-2) == 'new':
       redirect(URL('produtos_multilojas'))
    elif request.args(-3) == 'edit':
       idVinculo = request.args(-1)
       redirect(URL('produto_multiloja', args=idVinculo))

    return dict(gridProdutos=gridProdutos)

@auth.requires_membership('admin')
def produto_multiloja():

    idVinculo = request.args(0) or "0"

    if idVinculo == "0":
        formProduto = SQLFORM(Vinculos,field_id='id', _id='formProduto')

        btnNovo=btnExcluir=btnVoltar = ''
    else:
        formProduto = SQLFORM(Vinculos,idVinculo,_id='formProduto',field_id='id')

        btnExcluir = excluir("#")
        btnNovo = novo("produto_multiloja")

    btnVoltar = voltar("produtos_multilojas")

    if formProduto.process().accepted:
        response.flash = 'Produto Salvo com Sucesso!'
        redirect(URL('produto_multiloja', args=formProduto.vars.id))

    elif formProduto.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formProduto=formProduto,btnExcluir=btnExcluir, btnVoltar=btnVoltar, btnNovo=btnNovo)