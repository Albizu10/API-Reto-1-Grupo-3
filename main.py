import json, xmlrpc.client
from flask import Flask, Response, jsonify, request
# valiables globales
url = "http://odoogroup.duckdns.org"
DB = "edu-TechSolutions"
#estas se asignan al relizar el login
USR = ""
PASS=""
UID= ""
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

app = Flask(__name__)
#metodo para mostrar documentacion de la api al inicio
@app.route("/", methods=['GET'])
def api_documentation():
    html_doc = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Documentación API Odoo Flask</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background: #f8f8f8;
                color: #333;
            }
            h1, h2 {
                color: #005A9C;
            }
            pre {
                background: #eee;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .endpoint {
                background: #fff;
                margin-bottom: 20px;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 1px 1px 6px rgba(0,0,0,0.1);
            }
            .method {
                font-weight: bold;
                background: #005A9C;
                color: white;
                padding: 3px 8px;
                border-radius: 5px;
                font-size: 0.9em;
            }
            footer {
                text-align: center;
                margin-top: 40px;
                color: #777;
            }
        </style>
    </head>
    <body>
        <h1>📘 Documentación API Odoo Flask</h1>
        <p>Esta API permite interactuar con una base de datos Odoo a través de XML-RPC.</p>

        <div class="endpoint">
            <h2>/login <span class="method">POST</span></h2>
            <p>Autentica un usuario y guarda la sesión (UID).</p>
            <pre>{
  "user": "usuario@ejemplo.com",
  "password": "tu_contraseña"
}</pre>
        </div>

        <div class="endpoint">
            <h2>/searchID/&lt;tabla&gt; <span class="method">GET</span></h2>
            <p>Devuelve los IDs de registros que cumplen los filtros.</p>
            <pre>?filtros=[["campo","=","valor"]]</pre>
            <p><b>Ejemplo:</b> /searchID/res.partner?filtros=[["is_company","=",true]]</p>
        </div>

        <div class="endpoint">
            <h2>/getCantidad/&lt;tabla&gt; <span class="method">GET</span></h2>
            <p>Devuelve la cantidad total de registros según los filtros aplicados.</p>
            <pre>?filtros=[["active","=",true]]</pre>
            <p><b>Ejemplo:</b> /getCantidad/res.partner?filtros=[["active","=",true]]</p>
        </div>

        <div class="endpoint">
            <h2>/getDatosID/&lt;tabla&gt; <span class="method">GET</span></h2>
            <p>Obtiene los datos de uno o varios registros a partir de sus IDs.</p>
            <pre>?id=[1,2,3]&campos=["name","email"]</pre>
            <p><b>Ejemplo:</b> /getDatosID/res.partner?id=[3]&campos=["name","email"]</p>
        </div>

        <div class="endpoint">
            <h2>/getDatosFiltro/&lt;tabla&gt; <span class="method">GET</span></h2>
            <p>Devuelve los registros que cumplan los filtros y campos indicados.</p>
            <pre>?filtros=[["country_id","=",21]]&campos=["name","phone"]</pre>
            <p><b>Ejemplo:</b> /getDatosFiltro/res.partner?filtros=[["country_id","=",21]]&campos=["name","phone"]</p>
        </div>

        <div class="endpoint">
            <h2>/nuevo <span class="method">POST</span></h2>
            <p>Crea un nuevo registro en una tabla.</p>
            <pre>{
  "tabla": "res.partner",
  "nuevo": {"name": "Empresa X", "email": "contacto@empresa.com"}
}</pre>
        </div>

        <div class="endpoint">
            <h2>/modificar <span class="method">PUT</span></h2>
            <p>Modifica los registros existentes según ID(s).</p>
            <pre>{
  "tabla": "res.partner",
  "id": [5],
  "modificaciones": {"phone": "123456789"}
}</pre>
        </div>

        <div class="endpoint">
            <h2>/eliminar <span class="method">DELETE</span></h2>
            <p>Elimina uno o varios registros de una tabla.</p>
            <pre>{
  "tabla": "res.partner",
  "id": [10,11]
}</pre>
        </div>

        <footer>
            <hr>
            <p>© 2025 Edu Tech Solutions - API Grupo 3</p>
        </footer>
    </body>
    </html>
    """
    return Response(html_doc, mimetype='text/html')




@app.route("/login", methods=['POST'])

def login():
    data= request.get_json()
    global USR, PASS, UID # esto es para que coja las globales sino no se asignan
    USR=data.get("user")
    PASS=data.get("password")
    UID = common.authenticate(DB, USR, PASS, {})
    print(UID)
    if UID:
        return jsonify("Autenticacion completada con exito..."), 200
    else:
        return jsonify("Error, la autenticacion ha fallado"), 404


@app.route("/searchID/<string:tabla>", methods=['GET'])
def search_id(tabla):
    # Leer filtros desde los parametros GET
    filtros_str = request.args.get("filtros")

    # Convertir filtros de texto JSON a lista de Python
    if filtros_str:
        try:
            filtros = json.loads(filtros_str)
            if not isinstance(filtros, list):
                return jsonify({"error": "'filtros' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON inválido en 'filtros'"}), 400
    else:
        filtros = []  # si no hay filtros, busca todos los registros

    try:
        ids = models.execute_kw(DB, UID, PASS,tabla,'search',[filtros])
        return jsonify({"ids": ids}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/getCantidad/<string:tabla>", methods=['GET'])
def getCantidad(tabla):# metodo que devuelve la suma total de elementos segun la tabla y filtros
    filtros_str = request.args.get("filtros")

    if filtros_str:
        try:
            filtros = json.loads(filtros_str)
            if not isinstance(filtros, list):
                return jsonify({"error": "'filtros' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON inválido en 'filtros'"}), 400
    else:
        filtros = []
    try:
        cant = models.execute_kw(DB, UID, PASS, tabla, 'search_count', [filtros])
        return str(cant), 200
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/getDatosID/<string:tabla>", methods=['GET'])
def getDatos(tabla):# devuelve los datos de un elemento segun la tabla y el id(s)
    id_str = request.args.get("id")
    campos_str = request.args.get("campos")
    if not id_str:
        return jsonify({"error": "El parámetro 'id' es obligatorio."}), 400
    try:
        if id_str.startswith("["):
            ids = json.loads(id_str) 
        else :
            ids = [int(id_str)]

    except Exception:
        return jsonify({"error": "Formato inválido para 'id'. Debe ser un número o una lista JSON."}), 400
    
    if campos_str:
        try:
            campos = json.loads(campos_str)
            if not isinstance(campos, list):
                return jsonify({"error": "'campos' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON inválido en 'campos'"}), 400
    else:
        campos = []  # sin campos = todos los disponibles
    try:
        result = models.execute_kw(DB, UID, PASS, tabla, 'read', [ids], {'fields': campos})
        return jsonify({"result": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/getDatosFiltro/<string:tabla>", methods=['GET'])
def getFiltrosYCampos(tabla):# metodo que devuelve los datos segun tabla y con filtros y campos como parametros opcionales
    campos_str = request.args.get("campos")
    filtros_str = request.args.get("filtros")

    if campos_str:
        try:
            campos = json.loads(campos_str)
            if not isinstance(campos, list):
                return jsonify({"error": "'campos' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON inválido en 'campos'"}), 400
    else:
        campos = []

    if filtros_str:
        try:
            filtros = json.loads(filtros_str)
            if not isinstance(filtros, list):
                return jsonify({"error": "'filtros' debe ser una lista"}), 400
        except Exception:
            return jsonify({"error": "Formato JSON inválido en 'filtros'"}), 400
    else:
        filtros = []
    try:
        result= models.execute_kw(DB, UID, PASS, tabla, 'search_read', [filtros], {'fields': campos})
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/nuevo", methods=['POST'])
def nuevo():# metodo para aniadir nuevos elementos con sus atributos
    data = request.get_json()
    tabla = data.get("tabla")
    nuevo = data.get("nuevo")# un objeto json para atributos del nuevo elemento
    if not tabla:
        return {"error": "El parametro 'tabla' es obligatorio."}, 400
    if not isinstance(nuevo, dict):
        return {"error": "El parametro 'nuevo' debe ser un diccionario."}, 400
    try:
        nuevo_id = models.execute_kw(DB, UID, PASS, tabla, 'create', [nuevo])
        return jsonify({"id": nuevo_id}), 200
    except Exception as e:
        return {"error": str(e)}, 500 

@app.route("/modificar", methods=['PUT'])
def modificar():#metodo para modificar los atributos de los elementos de una tabla con id(s) 
    data = request.get_json()
    tabla = data.get("tabla")
    id = data.get("id")
    modificaciones = data.get("modificaciones")

    if not tabla:
        return {"error": "El parametro 'tabla' es obligatorio."}, 400
    if not id:
        return {"error": "El parametro 'id' es obligatorio."}, 400
    if not modificaciones or not isinstance(modificaciones, dict):
        return {"error": "El parametro 'modificaciones' debe ser un diccionario con los cambios."}, 400

    try:
        if isinstance(id, list):
            ids = id 
        else:
            ids = [id]
        result = models.execute_kw(DB, UID, PASS, tabla, 'write', [ids, modificaciones])
        if result:
            return {"message": "Operacion exitosa"}, 200
        else:
            return {"error": "No se pudo modificar el registro"}, 400
    except Exception as e:
        return {"error": str(e)}, 500
    

@app.route("/eliminar", methods=['DELETE'])
def eliminar():#metodo para eliminar por id
    data = request.get_json()
    tabla = data.get("tabla")
    id = data.get("id")

    if not tabla:
        return {"error": "El parametro 'tabla' es obligatorio."}, 400
    if not id:
        return {"error": "El parametro 'id' es obligatorio."}, 400

    try:
        if isinstance(id, list):
            ids = id 
        else:
            ids = [id]
        success = models.execute_kw(DB, UID, PASS, tabla, 'unlink', [ids])
        if success:
            return {"message": "Registro eliminado exitosamente."}, 200
        else:
            return {"error": "No se pudo eliminar los registros."}, 400
    except Exception as e:
        return {"error": str(e)}, 500



if __name__=="__main__":
    app.run(debug=True, port=5000)