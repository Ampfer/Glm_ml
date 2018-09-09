def vendas():
	import json
	if session.ACCESS_TOKEN:
		from meli import Meli 
		meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)
		body = 'seller=911703094686182'
		busca = meli.get("/orders/search/recent?seller=158428813&sort=date_desc", {'access_token':session.ACCESS_TOKEN})
		if busca.status_code == 200:
			itens = json.loads(busca.content)    
			itens = itens['results']
	else:
		status = 'Antes Faça o Login....'

	return dict(itens=itens)