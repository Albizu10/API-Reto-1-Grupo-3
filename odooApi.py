import xmlrpc.client , json

url = "http://odoo-grupo3.duckdns.org"
db = "edu-Tech-Solutions"
username = None
password=None
common=None
models = None
uid=None


def login(usuario, contr):
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    username=usuario
    password=contr
    uid = common.authenticate(db, username, password, {})
    if uid:
        print("Autenticacion completada con exito...")
        return True
    else:
        print("Error, la autenticacion ha fallado")
        return False

def buscarId(tabla, filtro=None):
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    if filtro==None:
        return models.execute_kw(db, uid, password, tabla, 'search', [[]])
    else:
        return models.execute_kw(db, uid, password, tabla, 'search', [[filtro]])

def cantidad(tabla, filtro=None):
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    if filtro==None:
        return models.execute_kw(db, uid, password, tabla, 'search_count', [[]])
    else:
        return models.execute_kw(db, uid, password, tabla, 'search_count', [[filtro]])
    
def leerDatosPorId(tabla, ids, campos=None):
    if campos==None:
        return models.execute_kw(db, uid, password, tabla, 'read', [ids])
    else:
        return models.execute_kw(db, uid, password, tabla, 'read', [ids], {'fields': campos})
    
def leerDatosPorFiltro(tabla, filtro=None, campos=None):
    if filtro != None and campos != None:
        return models.execute_kw(db, uid, password, tabla, 'search_read', [[filtro]], {'fields': campos})
    elif filtro==None and campos != None:
        return models.execute_kw(db, uid, password, tabla, 'search_read', [[]], {'fields': campos})
    elif filtro!=None and campos == None:
        return models.execute_kw(db, uid, password, tabla, 'search_read', [[filtro]])
    else:
        return models.execute_kw(db, uid, password, tabla, 'search_read', [[]])
    
def aniadir(tabla, nuevo):
    return models.execute_kw(db, uid, password, tabla, 'create', [nuevo])

def modificar(tabla, ids, datos):
    models.execute_kw(db, uid, password, tabla, 'write', [[ids], datos])

def eliminar(tabla, ids):
    models.execute_kw(db, uid, password, tabla, 'unlink', [[ids]])

def embellecer(datos):
    return json.dumps(datos, indent=4)

login("ikmssaid24@lhusurbil.eus", "usuario")
buscarId('res.partner')