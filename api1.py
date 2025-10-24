from flask import Flask
import xmlrpc.client 
url = "http://odoogroup3.duckdns.org"
db = "edu-Tech-Solutions"
username = 'odoo'
password = "usuario"
token="6fe8f86668652832c00a9478053385fc5112588f"

@app
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print(common.version())
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
models.execute_kw(db, uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])