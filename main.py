from types import SimpleNamespace
import odooApi, json
from flask import Flask, jsonify, request


app = Flask(__name__)
usuarios=[]

@app.route("/login", methods=['POST'])

def login():
    data =request.get_json()
    if odooApi.login(data[0], data[1]):
        return jsonify({"Exito": "Autentificacion realizada exitosamente"}), 200
    else:
        return jsonify({"mensaje": "Recurso no encontrado"}), 404

@app.route("/get", methods=['GET'])

def hello_world():
    
    odooApi.buscarId(tabla='res.partner',filtro=f)
    return "exito"

@app.route("/add", methods=['POST'])

def addUsuarios():
    data= request.get_json()

    for i in data:
        nombre= i.get("nombre", "Desconocido")
        edad= i.get("edad")
        usuarios.append({"nombre": nombre, "edad": edad})
    return jsonify({"mensaje":f"hola, {nombre}", "registros":usuarios})

@app.route("/delete/<int:id>", methods=['DELETE'] )

def eliminar(id):
    try:
        return jsonify(usuarios.pop(id)), 200
    except IndexError:
        return jsonify({"mensaje": "Recurso no encontrado"}), 404

if __name__=="__main__":
    app.run(debug=True, port=5000)