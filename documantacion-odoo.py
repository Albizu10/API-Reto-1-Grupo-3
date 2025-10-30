from flask import Flask
import xmlrpc.client , json
url = "http://odoogroup.duckdns.org"
db = "edu-TechSolutions"
username = 'ikmssaid24@lhusurbil.eus'
# el password funciona con la contraseña y con el api key no se cual usar
password = "usuario"
tokenV="6fe8f86668652832c00a9478053385fc5112588f"


common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print("version de odoo: ",common.version())

# realizamos el login
uid = common.authenticate(db, username, password, {})
print("User ID (uid): ", uid)

#ejemplo verificacion del login
if uid:
    print("Autenticacion completada con exito...")
else:
    print("Error, la autenticacion ha fallado")




# aqui usamos el '/xmlrpc/2/object' y no el '/xmlrpc/2/common' como antes
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

#metodo 'search'

#la tabla de contactos de la base de datos es 'res.partner' y usamos el metodo 'search'
contactosID= models.execute_kw(db, uid, password, 'res.partner', 'search', [[]])
#print("ID de Todos los contactos(sin filtrar): ",contactosID )

# usamos el offset para indicar la posicion en la que empieza y el limit para el limite de datos a sacar
contactosID= models.execute_kw(db, uid, password, 'res.partner', 'search', [[]], {"offset": 11, "limit" : 5})
#print("ID del 11 al 15: ",contactosID )

# filtramos para que solo aparezcan las companias con ['is_company', '=', True] (los filtros van entre las terceras llaves)
companiasID = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])
#print("Id las Companias: ",companiasID)

# otro ejemplo con el email 
contactoPorEmailID = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['email', '=', "toni.jimenez23@example.com"]]])
#print("Id del contacto: ",contactoPorEmailID)




#metodo 'search_count'

# retorna la cantidad de contactos
contactosCant=models.execute_kw(db, uid, password, 'res.partner', 'search_count', [[]])
#print("Cantidad de contactos: ", contactosCant)




#metodo 'read'

#le paso los id
contactos= models.execute_kw(db, uid, password, 'res.partner', 'read', [contactosID])
#print("Info de los contactos: ", json.dumps(contactos, indent=4))
# el json.dumps es para dar forma al json y no se vea todo junto

# especifico que campos quiero
contactos= models.execute_kw(db, uid, password, 'res.partner', 'read', [contactosID], {'fields': ['name', 'country_id', 'comment']})
#print("Info de los contactos: ", json.dumps(contactos, indent=4))




#metodo 'search_read'

#busca y retorna el name, country_id y comment de todas las companias
companias= models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[['is_company', '=', True]]], {'fields': ['name', 'country_id', 'comment']})
#print("Info de las companias: ", json.dumps(companias, indent=4))




#metodo 'create'

nuevoContacto={
'name': "Nuevo Contacto",
'email': "nuevoemail@email.com"
}

# para añadir un nuevo contacto
#nuevoContactoID= models.execute_kw(db, uid, password, 'res.partner', 'create', [nuevoContacto])
#print("ID del nuevo contacto: ", nuevoContactoID )




#metodo write

id=67
# aniadir o modificar el campo de uno o mas contactos
#models.execute_kw(db, uid, password, 'res.partner', 'write', [[id], {'phone': "1234567849"}])




#metodo unlink

# elimina uno o mas contactos
#models.execute_kw(db, uid, password, 'res.partner', 'unlink', [[id]])
