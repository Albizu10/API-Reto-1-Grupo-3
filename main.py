import json, xmlrpc.client
from flask import Flask, jsonify, request

url = "http://odoo-grupo3.duckdns.org"
DB = "edu-Tech-Solutions"
USR = ""
PASS=""
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
UID= ""

app = Flask(__name__)

@app.route("/login", methods=['POST'])

def login():
    data= request.get_json()
    global USR, PASS, UID
    USR=data.get("user")
    PASS=data.get("password")
    UID = common.authenticate(DB, USR, PASS, {})
    print(UID)
    if UID:
        return jsonify("Autenticacion completada con exito..."), 200
    else:
        return jsonify("Error, la autenticacion ha fallado"), 404

@app.route("/searchID", methods=['GET'])
def getID():
    data = request.get_json()
    tabla = data.get("tabla")
    return models.execute_kw(DB, UID, PASS, tabla, 'search', [[]]), 200

@app.route("/getCantidad", methods=['GET'])
def getCantidad():
    data = request.get_json()
    tabla = data.get("tabla")
    return models.execute_kw(DB, UID, PASS, tabla, 'search_count', [[]])

@app.route("/getDatosID", methods=['GET'])
def getDatos(id):
    data = request.get_json()
    tabla = data.get("tabla")
    id = data.get("id")
    return models.execute_kw(DB, UID, PASS, tabla, 'read', [[id]]), 200



@app.route("/getDatosFiltro", methods=['GET'])
def getFiltrosYCampos():
    data = request.get_json()
    tabla = data.get("tabla")
    campos = data.get("campos")
    filtros = data.get("filtros")
    return models.execute_kw(DB, UID, PASS, tabla, 'search_read', [[filtros]], {'fields': campos}), 200



@app.route("/nuevo", methods=['POST'])
def nuevo():
    data= request.get_json()
    tabla = data.get("tabla")
    nuevo = data.get("nuevo")
    return jsonify(models.execute_kw(DB, UID, PASS, tabla, 'create', [nuevo])), 

@app.route("/modificar", methods=['PUT'])
def modificar():
    data= request.get_json()
    tabla = data.get("tabla")
    id = data.get("id")
    if models.execute_kw(DB, UID, PASS, tabla, 'write', [[id], data]):
        return "Operacion extiosa", 200
    else:
        return "Oops ha habido un error...", 404
    

@app.route("/eliminar/<int:id>", methods=['DELETE'])
def eliminar(id):
    data= request.get_json()
    tabla = data.get("tabla")
    tabla = data.get("id")
    models.execute_kw(DB, UID, PASS, 'res.partner', 'unlink', [[id]])
    return jsonify("Usuario eliminado exitosamente"), 200



if __name__=="__main__":
    app.run(debug=True, port=5000)