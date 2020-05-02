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

					if loja == 'Amazon':
						Vinculos.frete.default = 3
						Vinculos.tarifa.default = 11
					if loja == "Magalu":
						Vinculos.frete.default = 0
						Vinculos.tarifa.default = 12

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
	
	produtos = db(Vinculos.id > 0).select()

	produtos_bling = []

	for produto in produtos:
		bling_produto = []
		bling_produto.append(produto.id_bling) # IdProduto
		bling_produto.append(produto.id_loja) # ID na Loja
		bling_produto.append(produto.produto) # Nome
		bling_produto.append(produto.id_produto) # Código
		bling_produto.append(float(produto.preco)) # Preco
		bling_produto.append(float(produto.preco_promocional)) # PrecoPromocional
		bling_produto.append(0) # ID do Fornecedor
		bling_produto.append(0) # ID da Marca	Nome
		bling_produto.append(produto.loja) # Loja (Multilojas)
		produtos_bling.append(bling_produto)

	c = csv.writer(open("vinculos.csv", "wb",),delimiter=';')
	head = ["IdProduto","ID na Loja","Nome","Código","Preco","PrecoPromocional","ID do Fornecedor","ID da Marca	Nome","Loja (Multilojas)"]

	c.writerow(head)
	for row in produtos_bling:
	    c.writerow(row)

	session.flash = 'Arquivo csv gerado com sucesso...!'
	return

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
    query = (Anuncios.status == 'active') 
    
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
		grupo = "com ST" if produto.cst == '60' else "com ST"

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
		bling_produto.append(grupo) # Grupo_de_Produtos
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

	c.writerow(head)
	for row in produtos_bling:
		c.writerow(row)

	session.flash = 'Arquivo csv gerado com sucesso...!'

	return

@auth.requires_membership('admin')
def bling_estoque():

	form = FORM.confirm('Gerar csv',{'Voltar':URL('default','index')})

	if form.accepted:

		head = ['ID Produto','Codigo produto *','GTIN **','Descrição Produto','Deposito (OBRIGATÓRIO)','Balanço (OBRIGATÓRIO)','Valor (OBRIGATÓRIO)','Preço de Custo,Observação','Data']
		estoque_bling = []
		estoque_bling.append(head)
		dt = request.now.strftime('%d/%m/%Y')

		anuncios = db(Anuncios.bling == True).select()
		for anuncio in anuncios:

			est_full = saldo_full(anuncio) if saldo_full(anuncio) > 0 else 0
			estoque =  float(sugerido(anuncio)['estoque']) - float(est_full)
			estoque = estoque if estoque > 0 else 0
			
			idProduto = str(db(Anuncios_Produtos.anuncio == anuncio.id).select().first()['produto']).zfill(5)
			row = []
			row.append('') #ID Produto
			row.append(idProduto) #Codigo produto *
			row.append('') #GTIN **,
			row.append('') #Descrição Produto
			row.append('Geral') #Deposito (OBRIGATÓRIO)
			row.append(float(estoque)) #Balanço (OBRIGATÓRIO)
			row.append(float(anuncio.preco)) #Valor (OBRIGATÓRIO)
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

@auth.requires_membership('admin')
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

@auth.requires_membership('admin')
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

@auth.requires_membership('admin')
def bling_pedidos():

	form = SQLFORM.factory(
	Field('numero','string',label='N. Pedido:'),
	table_name='importarpedido',
	submit_button='Importar',
	)

	if form.process().accepted:

		numero = form.vars.numero
		# Cunsulta de itens na Api do Bling
		pedidos = buscar_pedido(numero)
		salvar_pedidos(pedidos)

	elif form.errors:
		response.flash = 'Erro no Formulário'

	return dict(form=form)

@auth.requires_membership('admin')
def buscar_pedido(numero=None):

	if numero == None:
		url = 'https://bling.com.br/Api/v2/pedidos/json/'
		payload = {'apikey': BLING_SECRET_KEY,"filters":"idSituacao[9]"}

	else:
		url = 'https://bling.com.br/Api/v2/pedido/{}/json/'.format(numero)
		payload = {'apikey': BLING_SECRET_KEY}
	
	try:
		pedidos = requests.get(url, params=payload).json()['retorno']['pedidos']
	except Exception as e:
		pedidos = []

	return pedidos

@auth.requires_membership('admin')
def salvar_pedidos(pedidos):

	for pedido in pedidos:

		vendedor = 99
		loja = pedido['pedido']['tipoIntegracao']
		if loja == 'Amazon':
			vendedor = 149
		if loja == 'IntegraCommerce':
			vendedor = 147

		cliente_id = bling_lieto_clientes(pedido['pedido']['cliente'],vendedor)

		venda = {}
		venda['dtpedido'] = pedido['pedido']['data']
		venda['numero'] =  pedido['pedido']['numero']
		venda['pedidoLoja'] = pedido['pedido']['numeroPedidoLoja']
		venda['vendedor'] = vendedor
		venda['cliente'] = cliente_id
		venda['totalprodutos'] = pedido['pedido']['totalprodutos']
		venda['taxa'] = round(float(pedido['pedido']['totalprodutos'])*0.2,2)

		numorc = bling_lieto_orcamentos1(venda)
		
		itens =  pedido['pedido']['itens']
		bling_lieto_orcamentos2(numorc,itens)

		numdoc = bling_lieto_pedidos1(numorc)

		bling_lieto_pedidos2(numdoc,numorc)

	return

@auth.requires_membership('admin')
def bling_lieto_clientes(cliente_bl,vendedor):
	
	cliente = Clientes()

	cnpj = cliente_bl['cnpj'].replace(".","").replace("/","").replace("-","")

	cliente.nomcli = remover_acentos(cliente_bl['nome'][:50]).upper()
	cliente.nomfan = ''
	cliente.fisjur = 'J' if len(cnpj) == 13 else 'F'
	cliente.endcli = remover_acentos(cliente_bl['endereco'])[:50].upper()
	cliente.baicli = remover_acentos(cliente_bl['bairro'])[:35].upper()
	cliente.cidcli = remover_acentos(cliente_bl['cidade'])[:35].upper()
	cliente.estcli = remover_acentos(cliente_bl['uf'][:2]).upper()
	cliente.cepcli = cliente_bl['cep'].replace(".","")
	cliente.emacli = cliente_bl['email'][:40]
	cliente.telcli = cliente_bl['fone']
	cliente.cgccpf = cnpj
	cliente.numcli = cliente_bl['numero']
	cliente.datalt = '{}'.format(request.now.date())
	cliente.coccli = cliente.buscar_coccli(cliente.cidcli)
	cliente.emanfe = cliente_bl['email'][:50]
	cliente.codven = vendedor
	cliente.codcon = 31
	cliente.codcor = 15
	cliente.codtra = 273
	cliente.codtip = 5
	cliente.porcom = 1
	cliente.pdenor = 0
	cliente.regalt = 'S'
	cliente.calsub = 'N'
	cliente.envpdf = 'S'
	cliente.retpis = 'N'
	cliente.retcof = 'N'
	cliente.regesp = ''
	cliente.pdeqnt = 100

	cli = cliente.buscar_cliente_cnpj(cliente.cgccpf)
	
	if cli:
		query = "CGCCPF = '%s'" %(cliente.cgccpf)
		cliente.update(query)
		cliente_id = cli[0]	
	else:
		cliente.codcli = int(cliente.lastId())
		cliente.datcad = '%s' %(request.now.date())
		cliente.insert()
		cliente_id = cliente.codcli

	return cliente_id

@auth.requires_membership('admin')
def bling_lieto_orcamentos1(venda):
	orcamentos1 = Orcamentos1()

	# Retorna última Tabela de Preços
	tabela = orcamentos1.tabela()

	codmlb = 'B{}'.format(venda['numero'].zfill(6))

	total = float(venda['totalprodutos'])
	taxa = float(venda['taxa'])

	orcamentos1.codcli = venda['cliente']
	orcamentos1.pedven = venda['pedidoLoja']
	orcamentos1.codmlb = codmlb
	orcamentos1.codtab = str(tabela)
	orcamentos1.codven = venda['vendedor']
	orcamentos1.obsord = ''
	orcamentos1.porcom = (0.02*(total-taxa)/total)*100
	orcamentos1.codemp = 3
	orcamentos1.numorc = 0
	orcamentos1.pedcli = ''
	orcamentos1.pdeped = 0
	orcamentos1.pdeqnt = 0 
	orcamentos1.pdeval = 0 
	orcamentos1.pdepon = 0
	orcamentos1.codcon = 1
	orcamentos1.codcor = 15
	orcamentos1.codtra = 273
	orcamentos1.codred = 0
	orcamentos1.valfre = 0
	orcamentos1.tipfre = 0
	orcamentos1.pedimp = 'N'
	orcamentos1.tiporc = 'P'
	orcamentos1.sitorc = 'A'
	orcamentos1.status = 'PEN'
	orcamentos1.numlot = 0
	orcamentos1.horent = ''

	#numdoc = venda.numdoc or 0
	#orc =  orcamentos1.buscar(numdoc)

	query = "codmlb = '{}'".format(codmlb)
	try:
		numdoc = orcamentos1.select('NUMDOC',query).fetchone()[0]
	except:
		numdoc = None

	if numdoc:
		print 'orcamento ja cadastrado'	
	else:
		lastId = orcamentos1.last_id() # Retorna último Id Tabela ORCAMENTOS1
		numdoc = int(lastId) + 1
		orcamentos1.numdoc = int(lastId) + 1
		orcamentos1.datdoc = venda['dtpedido']
		orcamentos1.datpro = venda['dtpedido']

		orcamentos1.insert()

	return numdoc

@auth.requires_membership('admin')
def bling_lieto_orcamentos2(numdoc,itens):
	
	orcamentos2 = Orcamentos2()

	for item in itens:
		codigo = int(item['item']['codigo'])
		quantidade = item['item']['quantidade']
		preco = float(item['item']['valorunidade'])

		prod = Produtos()
		# Buscar produto banco firebird
		query = "CODPRO = {}".format(codigo)
		produto = prod.select('CODPRO,CODINT,NOMPRO,UNIPRO', query).fetchone()
		# Buscar preco tabela banco firebird
		preco_tabela = float(prod.preco_tabela(produto[0]))
		# calcular porcentagem de desconto do item
		pdepro = round((1-(preco/preco_tabela)) * 100,2)
		# verificar se existe item cadastrado
		query = "NUMDOC = {} AND CODPRO = {}".format(int(numdoc),int(produto[0]))
		
		existe = orcamentos2.select('*',query).fetchone()
	
		orcamentos2.numdoc = int(numdoc)
		orcamentos2.codpro = int(produto[0])
		orcamentos2.codint = str(produto[1])
		orcamentos2.nompro = produto[2].encode('UTF-8').replace("'","")
		orcamentos2.unipro = str(produto[3])
		orcamentos2.qntpro = quantidade
		orcamentos2.pdepro = float(pdepro)
		orcamentos2.preori = 0
		orcamentos2.precus = 0
		orcamentos2.prepro = preco
		orcamentos2.enviar = 'S'
		orcamentos2.tippro = 'VND'
		orcamentos2.qntpre = 1

		if existe:
			orcamentos2.update(query)
		else:
			try:
				orcamentos2.insert()
			except:
				orcamentos2.codpro = 1679
				orcamentos2.nompro = 'PRODUTO NÃO ENCOTRADO'		
				orcamentos2.insert()
	return

@auth.requires_membership('admin')
def bling_lieto_pedidos1(numorc):
	pedidos1 = Pedidos1()
	orcamentos1 = Orcamentos1()
	orcamentos2 = Orcamentos2()
	numdoc = (numorc*100) + 01
	
	# Buscar Orcamento
	fields = "codcli,numorc,pedcli,pedven,pdeped,pdeqnt,pdeval,pdepon,codtab,codven,porcom,codcon,codcor,codtra,codred,valfre,tipfre,datdoc,datpro,codmlb"
	query = " numdoc = {}".format(numorc)
	orcamento = orcamentos1.select(fields,query).fetchone()

	# total do orçamento 
	query = 'numdoc = {}'.format(numorc)
	total_itens = orcamentos2.select('sum(qntpro*prepro)',query).fetchone()[0]
	total = float(total_itens) + float(orcamento[15])
	
	pedidos1.numdoc = numdoc
	pedidos1.codcli = orcamento[0]
	pedidos1.numorc = numorc
	pedidos1.pedcli = orcamento[2]
	pedidos1.pedven = orcamento[3]
	pedidos1.pdeped = orcamento[4]
	pedidos1.pdeqnt = orcamento[5]
	pedidos1.pdeval = orcamento[6]
	pedidos1.pdepon = orcamento[7]
	pedidos1.codtab = orcamento[8]
	pedidos1.codven = orcamento[9]
	pedidos1.porcom = orcamento[10]
	pedidos1.codcon = orcamento[11]
	pedidos1.codcor = orcamento[12]
	pedidos1.codtra = orcamento[13]
	pedidos1.codred = orcamento[14]
	pedidos1.valfre = orcamento[15]
	pedidos1.tipfre = orcamento[16]
	pedidos1.datdoc = str(orcamento[17])
	pedidos1.datpro = str(orcamento[18])
	pedidos1.codmlb = str(orcamento[19])
	pedidos1.totped = total
	pedidos1.conimp = ''
	pedidos1.codemp = 3
	pedidos1.qntvol = 1
	pedidos1.espvol = 'VOLUMES'
	pedidos1.marvol = ''
	pedidos1.numvol = 0
	pedidos1.pesbru = 0
	pedidos1.pesliq = 0
	pedidos1.valsub = 0
	pedidos1.numnot = 0
	pedidos1.obsped = ''
	pedidos1.obsord = ''
	pedidos1.conimp = '0N' 
	pedidos1.pedsub = 0
	pedidos1.fretra = 0
	pedidos1.pedimp = 'N'

	query = 'numdoc = {}'.format(numdoc)
	pedido = pedidos1.select('*',query).fetchone()

	if pedido:
		print 'pedido ja cadastrado'	
		#query = "NUMDOC = '%s'" %(numdoc)
		#pedidos1.update(query)
	else:
		pedidos1.insert()
		
		#Atualiza Tabela Orcamento 1
		query = "NUMDOC = '%s'" %(int(numorc))
		orcamentos1.pedimp = 'S'
		orcamentos1.sitorc = 'E'
		orcamentos1.update(query)

	return numdoc

@auth.requires_membership('admin')
def bling_lieto_pedidos2(numdoc,numorc):

	pedidos2 = Pedidos2()
	orcamentos2 = Orcamentos2()
	produtos = Produtos()

	# buscar itens do orçamento
	fields = 'codpro,codint,nompro,unipro,qntpro,pdepro,precus,preori,prepro,tippro'
	query = 'NUMDOC = {}'.format(numorc)
	itens = orcamentos2.select(fields,query).fetchall()
	total_peso = 0
	for item in itens:

		pedidos2.numdoc = numdoc
		pedidos2.codpro = item[0]
		pedidos2.codint = item[1]
		pedidos2.nompro = item[2]
		pedidos2.unipro = item[3]
		pedidos2.qntpro = item[4]
		pedidos2.pdepro = item[5]
		pedidos2.precus = item[6]
		pedidos2.preori = item[7]
		pedidos2.prepro = item[8]
		pedidos2.tippro = item[9]

		# buscar peso na tabela de produtos
		query = 'CODPRO = {}'.format(item[0])
		peso = float(produtos.select('pesbru',query).fetchone()[0])

		total_peso = total_peso + peso

		query = 'NUMDOC = {} AND CODPRO = {}'.format(numdoc,item[0])
		existe = pedidos2.select('*',query).fetchone()
		if existe:
			pedidos2.update(query)
		else:
			pedidos2.insert()

	#Atualiza pesos na tabela pedidos1
	pedidos1 = Pedidos1()
	pedidos1.pesliq = total_peso
	pedidos1.pesbru = total_peso + 0.100
	query = 'NUMDOC = {}'.format(numdoc)
	pedidos1.update(query)
	
	return
