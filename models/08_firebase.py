import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

def firebase():
	try:
		credencial = os.path.join(request.folder,'private','amplog-48beb-firebase-adminsdk-y38tk-b7d589a8b7.json')
		cred = credentials.Certificate(credencial)
		firebase_admin.initialize_app(cred)
		return firestore.client()
	except:
		pass

def produto_firebase_set(produto):
	db = firebase()
	idProduto = str(produto['codpro']).zfill(6)
	doc_ref = db.collection('produtos').document(idProduto).set(produto)
	return idProduto

