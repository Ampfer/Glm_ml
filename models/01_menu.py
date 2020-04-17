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
    ('Atributos', False, URL(r=request, c='cadastro', f='atributos')),
    ])]
response.menu+=[
    (T('Anuncio'), False, URL(request.application,'default','index'), [
    ('Categoria', False, URL(r=request, c='anuncio', f='categorias')),
    ('Anuncio', False, URL(r=request, c='anuncio', f='anuncios')),
    ('Importar Anuncios', False, URL(r=request, c='anuncio', f='importar_anuncios')),
    ('Sincronizar Anuncios', False, URL(r=request, c='anuncio', f='sincronizar_anuncios')),
    ('Curva Abc', False, URL(r=request, c='anuncio', f='curva_abc')),
    ('Exportar Bling', False, URL(r=request, c='ferramentas', f='exportar_bling')),
    ])]
response.menu+=[
    (T('Vendas'), False, URL(request.application,'default','index'), [
    ('Importar Vendas', False, URL(r=request, c='vendas', f='importar_vendas')),
    ('Exportar Vendas', False, URL(r=request, c='lieto', f='exportar_vendas')),
    ('Vendas Canceladas', False, URL(r=request, c='vendas', f='pedidos_cancelados')),
    ('Atualizar Status', False, URL(r=request, c='vendas', f='atualizar_status')),
    ])]
response.menu+=[
    (T('Ferramentas'), False, URL(request.application,'default','index'), [
    ('Importar Estoque', False, URL(r=request, c='ferramentas', f='importar_estoque')),
    ('Atualizar Estoque', False, URL(r=request, c='ferramentas', f='atualizar_estoque')),
    ('Importar Produtos', False, URL(r=request, c='ferramentas', f='importar_produtos')),
    ('Sincronizar Produtos', False, URL(r=request, c='ferramentas', f='sincronizar_produtos')),
    ('Zerar Estoque', False, URL(r=request, c='ferramentas', f='zerar_estoque')),
    ('Atualizar Preços', False, URL(r=request, c='ferramentas', f='atualizar_preco')),
    ('Estoque Bling', False, URL(r=request, c='ferramentas', f='bling_estoque')),
    ])]
response.menu+=[
    (T('Lieto'), False, URL(request.application,'default','index'), [
    ('Cobrança Bradesco', False, URL(r=request, c='lieto', f='cobranca')),
    ('Gerar Pedidos', False, URL(r=request, c='lieto', f='pedidos')),
    ('Receber', False, URL(r=request, c='lieto', f='receber')),
    ('Importar Notas', False, URL(r=request, c='lieto', f='importar_nota')),
    ])]
response.menu+=[
    (T('Full'), False, URL(request.application,'default','index'), [
    ('Vendas Full', False, URL(r=request, c='lieto', f='vendas_full')),
    ('Envios Full', False, URL(r=request, c='full', f='envios_full_lista')),
    ('Anuncios Full', False, URL(r=request, c='full', f='anuncios_full')),
    ('Pedidos', False, URL(r=request, c='full', f='pedidos_full')),
    ])]
response.menu+=[
    (T('Bling'), False, URL(request.application,'default','index'), [
    ('Produtos Multilojas', False, URL(r=request, c='bling', f='produtos_multilojas')),
    ('Importar Produtos Multilojas', False, URL(r=request, c='bling', f='importar_vinculo')),
    ])]
response.menu+=[
    (T('Login ML'), False, URL(request.application,'default','login'),
    )]

DEVELOPMENT_MENU = True

if "auth" in locals():
    auth.wikimenu()
