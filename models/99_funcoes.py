# -*- coding: utf-8 -*-
 

@auth.requires_membership('admin')
def salvar_estoque_gml(produto):
	estoque = float(produto[1]) - float(produto[2]) - reservado(produto[0])
	estoque = 0 if estoque <0 else estoque

	try:
		db.produtos[int(produto[0])] = dict(estoque = estoque )
	except:
		pass

	anuncio_alterado_produto(produto[0])

	return

@auth.requires_membership('admin')
def atualizar_estoque():
	
	from meli import Meli 
	meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

	anuncios = db(Anuncios.item_id != '' and (Anuncios.alterado == 'S' or Anuncios.forma == 'Multiplos') ).select()

	for anuncio in anuncios:
		if anuncio['item_id']:
			variacao = []
			if anuncio['forma'] == 'Multiplos':
				body = dict(variations=buscar_variacao_estoque(anuncio['id']))
			else:
				body = dict(available_quantity=float(anuncio['estoque']))
			item_args = "items/%s" %(anuncio['item_id'])	
			item = meli.put(item_args, body, {'access_token':session.ACCESS_TOKEN})
			if item.status_code != 200:
				print '%s - %s - %s' %(anuncio['item_id'],anuncio['id'] ,item)
			else:
				Anuncios[anuncio.id] = dict(alterado = 'N')


@auth.requires_membership('admin')
def importar_estoque():
	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()

	select = "select codpro,qntest,(select VENDIDO FROM qtde_vendida(codpro)) from produtos where tabela = 'S'"

	produtos = cur.execute(select).fetchall()

	for produto in produtos:
		salvar_estoque_gml(produto)
		query = "update produtos set estalt = 'N' where codpro = {}".format(int(produto[0]))
		cur.execute(query)
		con.commit()

	con.close()


@auth.requires_membership('admin')
def anuncio_alterado_produto(codpro):
	idsAnuncios = db(Anuncios_Produtos.produto == int(codpro)).select(Anuncios_Produtos.anuncio).as_list()
	ids = [id['anuncio'] for id in idsAnuncios]
	anuncios = db(Anuncios.id.belongs(ids)).select()

	for anuncio in anuncios:
		est_full = saldo_full(anuncio) if saldo_full(anuncio) > 0 else 0
		estoque =  float(sugerido(anuncio)['estoque']) -  float(est_full)
		estoque = estoque if estoque > 0 else 0
		if estoque != anuncio.estoque:
			if est_full > 0:
				Anuncios[anuncio.id] = dict(estoque=estoque)
			else:
				Anuncios[anuncio.id] = dict(estoque=estoque,alterado = 'S')

@auth.requires_membership('admin')
def reservado(produtos_id):
    
    query = (Envios_Full.status == "Reservado") & (Envios_Produtos.envio_id == Envios_Full.id)
    query = query & '(Envios_Produtos.produtos_id == {})'.format(produtos_id)
    produtos= db(query).select()
    soma = 0
    for row in produtos:
        soma += int(row.envios_produtos.quantidade)
    return soma

@auth.requires_membership('admin')
def saldo_full(anuncio): 

    id = int(anuncio.id)

    query = (Envios_Itens.anuncio_id == id) & (Envios_Full.id == Envios_Itens.envio_id) & (Envios_Full.status == "Concluido")
    qt_envio = db(query).select(Envios_Itens.quantidade.sum()).first()[Envios_Itens.quantidade.sum()] or 0
    
    item_id = db(Anuncios.id == id).select(Anuncios.item_id).first()['item_id']
    
    query = (Pedidos.date_created >= '2020-02-01') & (Pedidos.logistica == 'fulfillment') & (Pedidos_Itens.shipping_id == Pedidos.id) & (Pedidos_Itens.status == 'paid') & "(Pedidos_Itens.item_id == '{}')".format(item_id)
    qt_vendida = db(query).select(Pedidos_Itens.quantidade.sum()).first()[Pedidos_Itens.quantidade.sum()] or 0
    
    return float(qt_envio) - float(qt_vendida)


'''
@auth.requires_membership('admin')
def importar_estoque_produto(codpro):

	import fdb
	con = fdb.connect(host=SERVERNAME, database=ERPFDB,user='sysdba', password='masterkey',charset='UTF8')
	cur = con.cursor()
	
	select = "select codpro,qntest,(select VENDIDO FROM qtde_vendida(codpro)) from produtos where codpro={}".format(codpro)
	produto = cur.execute(select).fetchone()

	salvar_estoque_gml(produto)
	query = "update produtos set estalt = 'N' where codpro = {}".format(int(produto[0]))
	cur.execute(query)
	con.commit()

	con.close()

	return
'''