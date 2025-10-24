from flask import Flask, jsonify, request

app = Flask(__name__)
usuarios=[]
@app.route("/pepe", methods=['GET'])

def hello_world():
    nombre = request.args.get('nombre', 'Desconocido')
    edad = request.args.get('edad', 1, type=int)
    return f"{nombre} {edad}"
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
    
@app.route("/put/<int:id>", methods=['PUT'] )

def cambiar(id):
    try:
        nombre= request.args.get("nombre")
        usuarios[id].nombre=nombre
        return jsonify(f"Cambio relizado exitosamenta{usuarios[id]}"), 200
    except IndexError:
        return jsonify({"mensaje": "Recurso no encontrado"}), 404

if __name__=="__main__":
    app.run(debug=True, port=5000)