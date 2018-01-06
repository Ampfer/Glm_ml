# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------

response.logo = A(B('web', SPAN(2), 'py'), XML('&trade;&nbsp;'),
                  _class="navbar-brand", _href="http://www.web2py.com/",
                  _id="web2py-logo")
response.title = request.application.replace('_', ' ').title()
response.subtitle = ''

# ----------------------------------------------------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# ----------------------------------------------------------------------------------------------------------------------
response.meta.author = myconf.get('app.author')
response.meta.description = myconf.get('app.description')
response.meta.keywords = myconf.get('app.keywords')
response.meta.generator = myconf.get('app.generator')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [
(T('Home'), False, URL(request.application,'default','index'), [])
]

response.menu+=[
    (T('Arquivos'), False, URL(request.application,'default','index'), [
    ('Empresa', False, URL(r=request, c='cadastro', f='empresa')),
    ('Cliente', False, URL(r=request, c='cadastro', f='clientes')),
    ('Marcas', False, URL(r=request, c='cadastro', f='marcas')),
    ('Familia de Produtos', False, URL(r=request, c='cadastro', f='familias')),
    ('Produtos', False, URL(r=request, c='cadastro', f='produtos')),
    ])]
response.menu+=[
    (T('Anuncio'), False, URL(request.application,'default','index'), [
    ('Categoria', False, URL(r=request, c='anuncio', f='categorias')),
    ('Anuncio', False, URL(r=request, c='anuncio', f='anuncios')),
    ])]
response.menu+=[
    (T('Vendas'), False, URL(request.application,'default','index'), [
    ('Vendas', False, URL(r=request, c='vendas', f='vendas')),
    ])]
response.menu+=[
    (T('Ferramentas'), False, URL(request.application,'default','index'), [
    ('Atualizar Estoque', False, URL(r=request, c='ferramentas', f='estoque')),
    ('Atualizar Preço', False, URL(r=request, c='ferramentas', f='preco')),
    ])]
response.menu+=[
    (T('Login ML'), False, URL(request.application,'default','login'),
    )]

DEVELOPMENT_MENU = True

if "auth" in locals():
    auth.wikimenu()
