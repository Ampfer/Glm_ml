# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    session.ACCESS_TOKEN = Empresa[1].token1
    session.REFRESH_TOKEN = Empresa[1].token2
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    #meli.authorize(request.query.get('code'), REDIRECT_URI)
    #teste = meli.get("users/275977425").json()
    #response.flash = T("Hello World")
    #return dict(message=T('Welcome to web2py!'))
    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


def login():
    print session.ACCESS_TOKEN
    from meli import Meli
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
    return "<a href='"+meli.auth_url(redirect_URI=REDIRECT_URI)+"'> Click para Fazer Login na conta do Mercado Livre </a>"

def autorize():
    from meli import Meli
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
    if request.vars.code:
        meli.authorize(request.vars.code, REDIRECT_URI)
    session.ACCESS_TOKEN = meli.access_token
    session.REFRESH_TOKEN = meli.access_token
    Empresa[1] = dict(token1 = session.ACCESS_TOKEN, token2=session.REFRESH_TOKEN)
    #meli = Meli(client_id=CLIENT_ID,client_secret=session.CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
    return meli.access_token



