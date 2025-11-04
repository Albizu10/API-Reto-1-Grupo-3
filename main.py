import json, xmlrpc.client
from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS
# valiables globales
url = "http://odoogroup3.duckdns.org"
DB = "edu-TechSolutions"
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

app = Flask(__name__)
app.secret_key = "usuario"
CORS(app, supports_credentials=True, origins=["http://localhost:8100"])
app.config.update(
    SESSION_COOKIE_SAMESITE='None',  # 'None' solo si HTTPS
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True
)
#metodo para mostrar documentacion de la api al inicio
@app.route("/", methods=['GET'])
def api_documentation():
    return render_template("index.html")

@app.route("/login", methods=["POST"])#Metodo para realizar el login y devuelve una cookie
def login():
    data = request.get_json()
    user = data.get("user")
    password = data.get("password")

    uid = common.authenticate(DB, user, password, {})
    if uid:
        session["uid"] = uid
        session["user"] = user
        session["password"] = password
        return jsonify({"mensaje": "Autenticacion exitosa"}), 200
    else:
        return jsonify({"error": "Credenciales invalidas"}), 401


@app.route("/searchID/<string:tabla>", methods=['GET'])#metodo para buscar los id por filtros y tabla
def search_id(tabla):

    if "uid" not in session:#verifica autentificacion
        return jsonify({"error": "Usuario no autenticado"}), 401
    # Leer filtros desde los parametros GET
    filtros_str = request.args.get("filtros")

    # Convertir filtros de texto JSON a lista de Python
    if filtros_str:
        try:
            filtros = json.loads(filtros_str)
            if not isinstance(filtros, list):
                return jsonify({"error": "'filtros' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON invalido en 'filtros'"}), 400
    else:
        filtros = []  # si no hay filtros, busca todos los registros

    try:
        ids = models.execute_kw(DB, session["uid"], session["password"],tabla,'search',[filtros])
        return jsonify({"ids": ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/getCantidad/<string:tabla>", methods=['GET'])
def getCantidad(tabla):# metodo que devuelve la suma total de elementos segun la tabla y filtros

    if "uid" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    filtros_str = request.args.get("filtros")

    if filtros_str:
        try:
            filtros = json.loads(filtros_str)
            if not isinstance(filtros, list):
                return jsonify({"error": "'filtros' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON invalido en 'filtros'"}), 400
    else:
        filtros = []
    try:
        cant = models.execute_kw(DB, session["uid"], session["password"], tabla, 'search_count', [filtros])#devuelve int asi que paso a string
        return str(cant), 200
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/getDatosID/<string:tabla>", methods=['GET'])
def getDatos(tabla):# devuelve los datos de un elemento segun la tabla y el id(s)
    if "uid" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401

    id_str = request.args.get("id")
    campos_str = request.args.get("campos")
    if not id_str:
        return jsonify({"error": "El parametro 'id' es obligatorio."}), 400
    try:
        if id_str.startswith("["):#para cargar los id sean en array o solos
            ids = json.loads(id_str)
        else :
            ids = [int(id_str)]

    except Exception:
        return jsonify({"error": "Formato invalido para 'id'. Debe ser un número o una lista JSON."}), 400

    if campos_str:
        try:
            campos = json.loads(campos_str)
            if not isinstance(campos, list):
                return jsonify({"error": "'campos' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON invalido en 'campos'"}), 400
    else:
        campos = []  # sin campos = todos los disponibles
    try:
        result = models.execute_kw(DB, session["uid"], session["password"], tabla, 'read', [ids], {'fields': campos})
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/getDatosFiltro/<string:tabla>", methods=['GET'])
def getFiltrosYCampos(tabla):# metodo que devuelve los datos segun tabla y con filtros y campos como parametros opcionales
    if "uid" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    campos_str = request.args.get("campos")
    filtros_str = request.args.get("filtros")

    if campos_str:
        try:
            campos = json.loads(campos_str)
            if not isinstance(campos, list):
                return jsonify({"error": "'campos' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON invalido en 'campos'"}), 400
    else:
        campos = []

    if filtros_str:
        try:
            filtros = json.loads(filtros_str)
            if not isinstance(filtros, list):
                return jsonify({"error": "'filtros' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON invalido en 'filtros'"}), 400
    else:
        filtros = []
    try:
        result= models.execute_kw(DB, session["uid"], session["password"], tabla, 'search_read', [filtros], {'fields': campos})
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/nuevo/<string:tabla>", methods=['POST'])
def nuevo(tabla):# metodo para aniadir nuevos elementos con sus atributos a una tabla
    if "uid" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    data = request.get_json()
    if not isinstance(data, dict):
        return {"error": "El parametro debe ser un diccionario."}, 400
    try:
        nuevo_id = models.execute_kw(DB, session["uid"], session["password"], tabla, 'create', [data])
        return jsonify({"id": nuevo_id}), 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/modificar/<string:tabla>/<int:id>", methods=['PUT'])
def modificar(tabla, id):#metodo para modificar los atributos de los elementos de una tabla por id
    if "uid" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return {"error": "El parametro debe ser un diccionario con los cambios."}, 400

    try:
        result = models.execute_kw(DB, session["uid"], session["password"], tabla, 'write', [[id], data])
        if result:
            return {"message": "Operacion exitosa"}, 200
        else:
            return {"error": "No se pudo modificar el registro"}, 400
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/eliminar/<string:tabla>/<int:id>", methods=['DELETE'])
def eliminar(tabla, id):#metodo para eliminar por id
    if "uid" not in session:
        return jsonify({"error": "Usuario no autenticado"}), 401
    try:
        result = models.execute_kw(DB, session["uid"], session["password"], tabla, 'unlink', [[id]])
        if result:
            return {"message": "Registro eliminado exitosamente."}, 200
        else:
            return {"error": "No se pudo eliminar los registros."}, 400
    except Exception as e:
        return {"error": str(e)}, 500



if __name__=="__main__":#iniciar el programa en el puerto 5000
    app.run(debug=True, port=5000)