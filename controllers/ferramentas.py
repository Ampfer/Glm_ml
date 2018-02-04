# -*- coding: utf-8 -*-
def importar_produtos():

	form = SQLFORM.factory(Field('csvfile','upload',uploadfield=False,label='Arquivo csv:',requires=notempty)
		,submit_button='Carregar Produtos')

	gridProdutos = file = ''

	#form = FORM(INPUT(_type='file',_name='csvfile'),INPUT(_type='submit',_value='Upload'))
	Importar_Produtos.truncate()
	
	if form.process().accepted:
		if request.vars.csvfile != None:
			Importar_Produtos.import_from_csv_file(request.vars.csvfile.file, delimiter=";")
			gridProdutos = grid(Importar_Produtos,formname="importarprodutos",create=False, editable=False,
				searchable=False,orderby = Importar_Produtos.nome)
			
			btnAtualizar = atualizar('atualiza_produtos','Atualizar Produtos', 'importarprodutos')
			gridProdutos[0].insert(-1, btnAtualizar)
			btnAtualizar["_onclick"] = "return confirm('Confirma a Atualização dos Produtos?');"
			if btnAtualizar:
				atualiza_produtos()
				file = file + 'PRODUTOS ATUALIZADOS COM SUCESSO'

			file = 'Arquivo Carregado: %s' %(request.vars.csvfile.filename)

	elif form.errors:
		response.flash = 'Erro no Formulário'

	return dict(form=form,gridProdutos=gridProdutos,file=file)

def atualiza_produtos():
	rows = db(Importar_Produtos.id > 0).select()
	for row in rows:
		Produtos.update_or_insert(Produtos.id == row.codigo,
                id = row.codigo,
                nome=row.nome,
                estoque=row.estoque
                )
	response.js = "$('#importarprodutos').get(0).reload()"



