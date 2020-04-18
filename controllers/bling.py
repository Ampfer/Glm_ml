# -*- coding: utf-8 -*-

import csv
import requests

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
					loja = i.replace('"','').strip()
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
	
	session.flash = 'Preços Atualizados com Sucesso.!'
	response.js = "location.reload(true)"

@auth.requires_membership('admin')
def atualizar_desconto():
	
	produtos = db(Vinculos.id > 0).select()
	
	for produto in produtos:

		desconto = 12

		if float(produto.preco_sugerido) > 30:
			desconto = 14
			if float(produto.preco_sugerido) > 60:
				desconto = 16
				if float(produto.preco_sugerido) > 90:
					desconto = 18
					if  float(produto.preco_sugerido) > 120:
						desconto = 20

		Vinculos[int(produto.id)] = dict(desconto=desconto)

		session.flash = 'Descontos Atualizados com Sucesso....!'
		response.js = "location.reload(true)"

@auth.requires_membership('admin')
def exportar_csv():
	c = csv.writer(open("produtos_bling.csv", "wb",),delimiter=';')
	head = ["ID","Codigo","Descricao","Unidade","Classificacao_fiscal","Origem","Preco","Valor_IPI_fixo","Observacoes","Situacao","Estoque","Preco_de_custo","Cod_no_fabricante","Fabricante","Localizacao","Estoque_maximo","Estoque_minimo","Peso_liquido_kg","Peso_bruto_kg","GTIN_EAN","GTIN_EAN_da_ embalagem","Largura_do_ Produto","Altura_do_Produto","Profundidade_do_produto","Data_Validade","Descricao_do_Produto_no_Fornecedor","Descricao_Complementar","Unidade_por_Caixa","Produto_Variacao","Tipo_Producao","Classe_de_enquadramento_do_IPI","Codigo_da_lista_de_servicos","Tipo_do_item","Grupo de Tags/Tags","Tributos","Código Pai","Código Integração","Grupo de Produtos","Marca","CEST","Volumes","Descrição curta","Cross-Docking","URL Imagens Externas","Link Externo","Meses Garantia","Clonar dados do pai","Condição do produto","Frete Grátis","Número FCI","Vídeo"]
	#head = ["Codigo","Descricao","Unidade","Classificacao_fiscal","Origem","Preco","Situacao","Estoque","Localizacao","Peso_liquido_kg","Peso_bruto_kg","GTIN_EAN","Largura_do_ Produto","Altura_do_Produto","Profundidade_do_produto","Produto_Variacao","Código Pai","Marca","CEST","Descrição curta","Meses Garantia","Clonar dados do pai","Condição do produto","Frete Grátis"]
	c.writerow(head)
	for row in produtos_bling:
	    c.writerow(row)

	session.flash = 'Arquivo csv gerado com sucesso...!'

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
		_id='atualizardesconto', 
		_onclick="if (confirm('Deseja Atualizar Descontos ?')) ajax('%s',[], 'formVinculo');" %URL('atualizar_desconto',args=request.vars.keywords)
		)

	btnExportar = A(SPAN(_class="glyphicon glyphicon-cog"), 
		' Gerar csv ', 
		_class="btn btn-default",
		_id='gerarcsv', 
		_onclick="if (confirm('Deseja Gerar aruivo csv ?')) ajax('%s',[], 'formVinculo');" %URL('exportar_csv',args=request.vars.keywords)
		)

	fields = (Vinculos.id_produto,Vinculos.produto, Vinculos.id_bling, Vinculos.id_loja,Vinculos.preco_tabela, Vinculos.desconto,
		      Vinculos.preco_sugerido,Vinculos.preco, Vinculos.preco_promocional, Vinculos.loja)
	gridProdutos = grid(Vinculos,formname="formVinculo",fields=fields,orderby = Vinculos.produto, deletable = False, create = False, alt='300px')

	gridProdutos[0].insert(-1, btnDesconto)
	gridProdutos[0].insert(-1, btnSugerido)
	gridProdutos[0].insert(-1, btnExportar)

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


@auth.requires_membership('admin')
def exportar_bling():

    fields = (Anuncios.titulo, Anuncios.preco, Anuncios.estoque)
    selectable = lambda ids: bling_csv(ids)
    query = (Anuncios.status == 'active') & (Anuncios.bling != True) 
    
    gridAnuncios = grid(query ,create=False, editable=False,deletable=False,formname="pedidos", alt='250px',
        fields=fields,orderby =~ Anuncios.vendido, selectable=selectable, selectable_submit_button='Exportar Bling',)

    return dict(gridAnuncios = gridAnuncios)

@auth.requires_membership('admin')
def bling_csv(ids):

	anuncios = db(Anuncios.id.belongs(ids)).select()

	produtos_bling = []

	for anuncio in anuncios:

		idProduto = db(Anuncios_Produtos.anuncio == anuncio.id).select().first()['produto']
		produto = db(db.produtos.id == idProduto).select().first()
		descricao = buscar_descricao(idProduto)
		imagens = db(Anuncios_Imagens.anuncio == anuncio.id).select()

		url_imagens = []
		for imagem in imagens:
			img = Imagens[int(imagem.imagem)].imagem
			url_imagens.append('http://18.230.73.54/glm_ml/default/download/{}'.format(img))

		url = ', '.join(url_imagens)

		bling_produto = []
		bling_produto.append('')# Id
		bling_produto.append(str(idProduto).zfill(5)) # codigo
		bling_produto.append(anuncio.titulo) # descrição
		bling_produto.append('un') # unidade
		bling_produto.append(produto.ncm) # Classificacao_fiscal
		bling_produto.append(produto.origem) # Origem
		bling_produto.append(anuncio.preco) # Preco
		bling_produto.append('') #Valor_IPI_fixo
		bling_produto.append('') # Observacoes 
		bling_produto.append('Ativo') # Situacao
		bling_produto.append(anuncio.estoque) # Estoque
		bling_produto.append(0) # Preco_de_custo 
		bling_produto.append(0) # Cod_no_fabricante 
		bling_produto.append(0) # Fabricante  
		bling_produto.append(produto.locpro) # Localizacao
		bling_produto.append(0) # Estoque_maximo
		bling_produto.append(0) # Estoque_minimo
		bling_produto.append(produto.peso) # Peso_liquido_kg
		bling_produto.append(produto.peso) # Peso_bruto_kg
		bling_produto.append(produto.ean) # GTIN_EAN
		bling_produto.append(produto.ean) # GTIN_EAN_da_embalagem
		bling_produto.append(produto.largura) # Largura_do_Produto
		bling_produto.append(produto.altura) # Altura_do_Produto
		bling_produto.append(produto.comprimento) # Profundidade_do_produto
		bling_produto.append('') # Data_Validade = None,
		bling_produto.append('') # Descricao_do_Produto_no_Fornecedor
		bling_produto.append('') # Descricao_Complementar
		bling_produto.append('') # Unidade_por_Caixa
		bling_produto.append('produto') # Produto_Variacao    
		bling_produto.append('Terceiros') # Tipo_Producao 
		bling_produto.append('') # Classe_de_enquadramento_do_IPI
		bling_produto.append('') # Codigo_da_lista_de_servicos
		bling_produto.append('Mercadoria para Revenda') # Tipo_do_item
		bling_produto.append('') # Grupo_de_Tags_Tags
		bling_produto.append(0) # Tributos
		bling_produto.append('') # Codigo_Pai 
		bling_produto.append('') # Codigo_Integracao
		bling_produto.append('') # Grupo_de_Produtos
		bling_produto.append(produto.marca) # Marca
		bling_produto.append('') # CEST 
		bling_produto.append(1) # Volumes
		bling_produto.append(descricao) # Descricao_curta
		bling_produto.append(0) # Cross_Docking
		bling_produto.append(url) # URL_Imagens_Externas
		bling_produto.append('') # Link_Externo
		bling_produto.append(3) # Meses_Garantia
		bling_produto.append('NÃO') # Clonar_dados_do_pai
		bling_produto.append('NOVO') # Condicao_do_produto
		bling_produto.append('NÃO') # Frete_Gratis
		bling_produto.append(0) # Numero_FCI 
		bling_produto.append('') # Video
		bling_produto.append('') # Departamento
		bling_produto.append('Centímetro') # Unidade de Medida

		Anuncios[anuncio.id] = dict(bling = True)
		produtos_bling.append(bling_produto)

	c = csv.writer(open("produtos_bling.csv", "wb",),delimiter=';')

	head = ["ID","Codigo","Descricao","Unidade","Classificacao_fiscal","Origem","Preco","Valor_IPI_fixo","Observacoes","Situacao","Estoque","Preco_de_custo","Cod_no_fabricante","Fabricante","Localizacao","Estoque_maximo","Estoque_minimo","Peso_liquido_kg","Peso_bruto_kg","GTIN_EAN","GTIN_EAN_da_ embalagem","Largura_do_ Produto","Altura_do_Produto","Profundidade_do_produto","Data_Validade","Descricao_do_Produto_no_Fornecedor","Descricao_Complementar","Unidade_por_Caixa","Produto_Variacao","Tipo_Producao","Classe_de_enquadramento_do_IPI","Codigo_da_lista_de_servicos","Tipo_do_item","Grupo de Tags/Tags","Tributos","Código Pai","Código Integração","Grupo de Produtos","Marca","CEST","Volumes","Descrição curta","Cross-Docking","URL Imagens Externas","Link Externo","Meses Garantia","Clonar dados do pai","Condição do produto","Frete Grátis","Número FCI","Vídeo"]

	for row in produtos_bling:
		c.writerow(row)

	session.flash = 'Arquivo csv gerado com sucesso...!'

	return

def bling_estoque():

	form = FORM.confirm('Gerar csv',{'Voltar':URL('default','index')})

	if form.accepted:

		head = ['ID Produto','Codigo produto *','GTIN **','Descrição Produto','Deposito (OBRIGATÓRIO)','Balanço (OBRIGATÓRIO)','Valor (OBRIGATÓRIO)','Preço de Custo,Observação','Data']
		estoque_bling = []
		estoque_bling.append(head)
		dt = request.now.strftime('%d/%m/%Y')

		anuncios = db(Anuncios.bling == True).select()
		for anuncio in anuncios:
			#print anuncio.titulo
			idProduto = str(db(Anuncios_Produtos.anuncio == anuncio.id).select().first()['produto']).zfill(5)
			row = []
			row.append('') #ID Produto
			row.append(idProduto) #Codigo produto *
			row.append('') #GTIN **,
			row.append('') #Descrição Produto
			row.append('Geral') #Deposito (OBRIGATÓRIO)
			row.append(anuncio.estoque) #Balanço (OBRIGATÓRIO)
			row.append(anuncio.preco) #Valor (OBRIGATÓRIO)
			row.append(0) #Preço de Custo
			row.append('') #Observação
			row.append(dt) #Data

			estoque_bling.append(row)

		import csv
		c = csv.writer(open("estoque_bling.csv", "wb",),delimiter=';')
		for row in estoque_bling:
			c.writerow(row)

			session.flash = 'Arquivo csv gerado com sucesso...!'

	return dict(form=form)


def categorias_bling():
	import json
	url = 'https://bling.com.br/Api/v2/categorias/json/'
	payload = {'apikey': BLING_SECRET_KEY}

	categorias = requests.get(url, params=payload).json()['retorno']['categorias']

	for categoria in categorias:
		Categorias_Bling.update_or_insert(Categorias_Bling.id == categoria['categoria']['id'],
			id=categoria['categoria']['id'],
			categoria = categoria['categoria']['descricao'],
  			pai_id = categoria['categoria']['idCategoriaPai']
			)

	return 

def categorias_bling_post():

	xml = """
	<?xml version="1.0" encoding="UTF-8"?>
	<categorias>
	  <categoria>
	    <descricao>{}</descricao>
	    <idcategoriapai>0</idcategoriapai>
	  </categoria>
	</categorias>
	""".format('Animais')

	url = 'https://bling.com.br/Api/v2/categoria/json/'
	payload = {'apikey': BLING_SECRET_KEY,'xml' : xml}

	categoria = requests.post(url, params=payload)

	return categoria