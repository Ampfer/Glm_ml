# -*- coding: utf-8 -*-

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import re
import requests
import json
from urllib import urlencode

FIREBASE_API_ROOT_URL = 'https://us-central1-amplog-48beb.cloudfunctions.net/api'

def atualiza_produto_firebase():
	produtos = Produtos()
	fields = "codpro, nompro, codbar, pesbru, locpro"
	query = "codgru = 1 and tabela = 'S' and codpro = 81"
	results = produtos.select(fields,query).fetchone()
	produto = dict(
		codpro = results[0],
		nompro = results[1],
		codbar = results[2],
		pesbru = float(results[3]),
		locpro = results[4] 
	)

	response = post("/produtos",body=produto)
	
	if response.status_code == 200:
		resposta = json.loads(response.content)
		print resposta

	#produto_firebase_set(produto)

def buscar_produtos_firebase():
	response = get("/produtos")
	
	if response.status_code == 200:
		resposta = json.loads(response.content)
	return response


def post(path, body=None, params={}):
    headers = {'Accept': 'application/json', 'Content-type':'application/json'}
    uri = make_path(path)
    if body:
        body = json.dumps(body)

    response = requests.post(uri, data=body, params=urlencode(params), headers=headers)
    return response

def get(path, params={}):
	params = dict(codbar=7898901274209)
	headers = {'Accept': 'application/json', 'Content-type':'application/json','x-format-new':'true'}
	uri = make_path(path,params=params)
	response = requests.get(uri, params=urlencode(params), headers=headers)
	return response


def make_path(path, params={}):        
	if not (re.search("^http", path)):
	    if not (re.search("^\/", path)):
	        path = "/" + path
	    path = FIREBASE_API_ROOT_URL + path
	if params:
	    path = path + "?" + urlencode(params)
	
	print path
	return path