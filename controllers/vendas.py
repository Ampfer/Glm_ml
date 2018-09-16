def vendas():
	import json
	from datetime import datetime
	
	if session.ACCESS_TOKEN:
		from meli import Meli 
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
		busca = meli.get("/orders/search/recent?seller=158428813&sort=date_desc", {'access_token':session.ACCESS_TOKEN})
		if busca.status_code == 200:
			itens = json.loads(busca.content)    
			itens = itens['results']

	for item in itens:

		body = "/shipments/%s" %(item['shipping']['id'])
		busca = meli.get(body, {'access_token':session.ACCESS_TOKEN})

		if busca.status_code == 200:
			shipping = json.loads(busca.content)
			
			Clientes.update_or_insert(Clientes.id == item['buyer']['id'],
                id = item['buyer']['id'],
                nome = "%s %s" %(item['buyer']['first_name'],item['buyer']['last_name']),
                cnpj_cpf = item['buyer']['billing_info']['doc_number'],
                tipo = item['buyer']['billing_info']['doc_type'],
                endereco = shipping['destination']['shipping_address']['address_line'], 
                bairro = shipping['destination']['shipping_address']['neighborhood']['name'],
                cidade = shipping['destination']['shipping_address']['city']['name'],
                estado = shipping['destination']['shipping_address']['state']['name'],
                cep = shipping['destination']['shipping_address']['zip_code'],
                fone = "%s %s" %(item['buyer']['phone']['area_code'] or '',item['buyer']['phone']['number'] or ''),
                email = item['buyer']['email'],
                apelido = item['buyer']['nickname'],
                )
			
			Pedidos.update_or_insert(Pedidos.id == item['shipping']['id'],
				id = item['shipping']['id'],
				buyer_id = item['buyer']['id'],
				#date_created = (item['date_created'][:10],'%Y-%m-%d')
				)

			Pedidos_Itens.update_or_insert(Pedidos_Itens.id == item['id'],
				id = item['id'],
				shipping_id = item['shipping']['id'],
				item = item['order_items'][0]['item']['title'],
				item_id = item['order_items'][0]['item']['id'],
				quantidade =  item['order_items'][0]['quantity'],
				valor = item['order_items'][0]['unit_price'],
				taxa = 0,
				frete = 0, 
				)

	else:
		status = 'Antes Faça o Login....'

	return dict(itens=itens)