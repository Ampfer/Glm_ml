# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
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

def login():
    from meli import Meli
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
    return "<a href='"+meli.auth_url(redirect_URI=REDIRECT_URI)+"'>Login</a>"

def autorize():
    from meli import Meli
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
    if request.vars.code:
        meli.authorize(request.vars.code, REDIRECT_URI)
    ACCESS_TOKEN = meli.access_token
    REFRESH_TOKEN = meli.access_token
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=ACCESS_TOKEN, refresh_token=REFRESH_TOKEN)
    body = {"available_quantity": 30, "price":200 }
    #teste = meli.put("items/MLB919597672", body, {'access_token':ACCESS_TOKEN})
    teste = meli.get("categories/MLB2527")
    response.view='generic_list.csv'
    return teste


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


