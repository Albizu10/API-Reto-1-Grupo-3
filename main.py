import json, xmlrpc.client
from flask import Flask, Response, jsonify, request
# valiables globales
url = "http://odoo-grupo3.duckdns.org"
DB = "edu-Tech-Solutions"
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
    <html>
    <head>
        <title>Documentación API Odoo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f8f8f8; color: #333; }
            h1, h2 { color: #005A9C; }
            pre { background: #eee; padding: 10px; border-radius: 5px; }
            .endpoint { background: #fff; margin-bottom: 20px; padding: 15px; border-radius: 8px; box-shadow: 1px 1px 6px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <h1>Documentación API Odoo</h1>
        <p>Esta API expone los siguientes endpoints para interactuar con Odoo vía XML-RPC:</p>

        <div class="endpoint">
            <h2>/login [POST]</h2>
            <p>Autenticar usuario y obtener sesión.</p>
            <pre>JSON Body: {"user": "nombre", "password": "clave"}</pre>
        </div>

        <div class="endpoint">
            <h2>/searchID [POST]</h2>
            <p>Obtener IDs según filtros en un modelo.</p>
            <pre>JSON Body: {"tabla": "res.partner", "filtros": [["is_company", "=", true]]}</pre>
        </div>

        <div class="endpoint">
            <h2>/getCantidad [POST]</h2>
            <p>Obtener cantidad de registros que cumplen filtro.</p>
            <pre>JSON Body: {"tabla": "res.partner", "filtros": [["active", "=", true]]}</pre>
        </div>

        <div class="endpoint">
            <h2>/getDatosID [POST]</h2>
            <p>Obtener datos de registros dado ID o lista de IDs.</p>
            <pre>JSON Body: {"tabla": "res.partner", "id": [3,4], "campos": ["name", "email"]}</pre>
        </div>

        <div class="endpoint">
            <h2>/getDatosFiltro [POST]</h2>
            <p>Obtener datos según filtros y campos.</p>
            <pre>JSON Body: {"tabla": "res.partner", "filtros": [["country_id", "=", 21]], "campos": ["name", "phone"]}</pre>
        </div>

        <div class="endpoint">
            <h2>/nuevo [POST]</h2>
            <p>Crear un nuevo registro.</p>
            <pre>JSON Body: {"tabla": "res.partner", "nuevo": {"name": "Empresa X", "email": "contacto@empresa.com"}}</pre>
        </div>

        <div class="endpoint">
            <h2>/modificar [PUT]</h2>
            <p>Modificar registros por ID(s).</p>
            <pre>JSON Body: {"tabla": "res.partner", "id": 5, "modificaciones": {"phone": "123456789"}}</pre>
        </div>

        <div class="endpoint">
            <h2>/eliminar [DELETE]</h2>
            <p>Eliminar registro(s) por ID(s).</p>
            <pre>JSON Body: {"tabla": "res.partner", "id": [10,11]}</pre>
        </div>

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

@app.route("/searchID", methods=['POST'])
def getID():# metodo que recibe un json y devuelve los id segun filtro y tabla
    data = request.get_json() or {}
    tabla = data.get("tabla")
    filtros = data.get("filtros")
    
    if not tabla:
        return {"error": "El parametro 'tabla' es obligatorio."}, 400
    try:
        if filtros==None:
            ids = models.execute_kw(DB, UID, PASS, tabla, 'search', [[]])
        else:
            ids = models.execute_kw(DB, UID, PASS, tabla, 'search', [filtros])
        return {"ids": ids}, 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/getCantidad", methods=['POST'])
def getCantidad():# metodo que devuelve la suma total de elementos segun la tabla y filtros
    data = request.get_json()
    tabla = data.get("tabla")
    filtros = data.get("filtros")
    if not tabla:
        return {"error": "El parametro 'tabla' es obligatorio."}, 400
    try:
        if filtros==None:
            cant = models.execute_kw(DB, UID, PASS, tabla, 'search_count', [[]])
        else:
            cant = models.execute_kw(DB, UID, PASS, tabla, 'search_count', [filtros])
        return {"Cantidad":cant}, 200
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/getDatosID", methods=['POST'])
def getDatos():# metodo que devuelve los datos de una tabla segun el id y los campos a mostrar
    data = request.get_json()
    tabla = data.get("tabla")
    id = data.get("id")
    campos = data.get("campos", [])  # campos opcional, puede quedar vacío por defecto para mostrar todos
    
    if not tabla:
        return {"error": "El parametro 'tabla' es obligatorio."}, 400
    if not id:
        return {"error": "El parametro 'id' es obligatorio."}, 400
    try:
        if isinstance(id, list):# devuelve true si es una lista
            ids = id 
        else:
            ids = [id]
        result = models.execute_kw(DB, UID, PASS, tabla, 'read', [ids], {'fields': campos})
        return {"result": result}, 200
    except Exception as e:
        return {"error": str(e)}, 500



@app.route("/getDatosFiltro", methods=['POST'])
def getFiltrosYCampos():
    data = request.get_json()
    tabla = data.get("tabla")
    campos = data.get("campos", [])
    filtros = data.get("filtros")
    if not tabla:
        return {"error": "El parametro 'tabla' es obligatorio."}, 400
    try:
        if filtros==None:
            result = models.execute_kw(DB, UID, PASS, tabla, 'search_read', [[]], {'fields': campos})
        else:
            result= models.execute_kw(DB, UID, PASS, tabla, 'search_read', [filtros], {'fields': campos})
        return result, 200
    except Exception as e:
        return {"error": str(e)}, 500



@app.route("/nuevo", methods=['POST'])
def nuevo():
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
def modificar():
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
def eliminar():
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