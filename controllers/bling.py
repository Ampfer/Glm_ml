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
def atualizar_sugerido():
	produtos = db(Vinculos.id > 0).select()
	for produto in produtos:
		Vinculos[int(produto.id)] = dict(preco=produto.preco_sugerido, preco_promocional=produto.preco_sugerido)
	response.js = "location.reload(true)"

@auth.requires_membership('admin')
def atualizar_desconto():
	produtos = db(Vinculos.id > 0).select()
	for produto in produtos:
		if produto.sugerido > 30:
			desconto = 14
		elif produto.sugerido > 60:
			desconto = 16
		elif produto.sugerido > 90:
			desconto = 18
		elif produto.sugerido > 120:
			desconto = 20
		else:
			desconto = 12
		Vinculos[int(produto.id)] = dict(desconto=desconto)
		
	response.js = "location.reload(true)"

@auth.requires_membership('admin')
def produtos_multilojas():

	btnSugerido = A(SPAN(_class="glyphicon glyphicon-cog"), 
		' Atualizar Sugerido ', 
		_class="btn btn-default",
		_id='atualizarsugerido', 
		_onclick="if (confirm('Deseja Atualizar Preços com Sugeridos ?')) ajax('%s',[], 'formVinculo');" %URL('atualizar_sugerido',args=request.vars.keywords)
		)

	btnDesconto = A(SPAN(_class="glyphicon glyphicon-cog"), 
		' Atualizar Descontos ', 
		_class="btn btn-default",
		_id='atualizarsugerido', 
		_onclick="if (confirm('Deseja Atualizar Descontos ?')) ajax('%s',[], 'formVinculo');" %URL('atualizar_desconto',args=request.vars.keywords)
		)

	fields = (Vinculos.id_produto,Vinculos.produto, Vinculos.id_bling, Vinculos.id_loja,Vinculos.preco_tabela, Vinculos.desconto,
		      Vinculos.preco_sugerido,Vinculos.preco, Vinculos.preco_promocional, Vinculos.loja)
	gridProdutos = grid(Vinculos,formname="formVinculo",fields=fields,orderby = Vinculos.produto, deletable = False, create = False, alt='300px')

	gridProdutos[0].insert(-1, btnSugerido)
	gridProdutos[0].insert(-1, btnDesconto)

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
        sug = Vinculos[idVinculo].preco_sugerido

        btnExcluir = excluir("#")
        btnNovo = novo("produto_multiloja")

    btnVoltar = voltar("produtos_multilojas")

    def validar(form):
    	if form.vars.preco_promocional > form.vars.preco or float(form.vars.preco_promocional) < float(form.vars.preco)*0.9:
    		form.errors.preco_promocional = 'Preço Promocional não permitido'

    if formProduto.process(onvalidation=validar).accepted:
        response.flash = 'Produto Salvo com Sucesso!'
        redirect(URL('produto_multiloja', args=formProduto.vars.id))

    elif formProduto.errors:
        response.flash = 'Erro no Formulário Principal!'

    return dict(formProduto=formProduto, btnVoltar=btnVoltar, sug=sug)