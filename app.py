from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import Config
# En app.py, después de los otros imports


# Después de registrar los otros blueprints

# Importar servicios
from services.db_service import DatabaseService, init_db

# Importar blueprints
from controllers.auth_controller import auth_bp
from controllers.paciente_controller import paciente_bp
from controllers.consulta_controller import consulta_bp
from controllers.osm_controller import osm_bp
from controllers.statistics_controller import statistics_bp
from controllers.report_controller import report_bp
from controllers.payment_controller import payment_bp
from controllers.messenger_controller import messenger_bp
from controllers.plan_controller import plan_bp
from controllers.youtube_controller import youtube_bp


app = Flask(__name__, template_folder="templates")
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Inicializar MySQL
mysql = MySQL(app)

app.mysql = mysql 

# Inicializar el servicio de base de datos con la instancia de MySQL
init_db(mysql)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(paciente_bp)
app.register_blueprint(consulta_bp)
app.register_blueprint(plan_bp)
app.register_blueprint(youtube_bp)
app.register_blueprint(osm_bp)
app.register_blueprint(statistics_bp)
app.register_blueprint(report_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(messenger_bp)



# ==================== RUTAS PRINCIPALES ====================

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("menu"))
    return redirect(url_for("auth.login"))

@app.route("/menu")
def menu():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    if session.get("user_rol") == "nutriologo":
        # Obtener estadísticas para nutriólogo
        pacientes = DatabaseService.get_pacientes(nutriologo_id=session.get("nutriologo_id"))
        total_pacientes = len(pacientes)
        
        # Contar consultas de hoy
        from datetime import date
        consultas_hoy = 0
        for p in pacientes:
            consultas = DatabaseService.get_consultas_by_paciente(p.idPaciente)
            for c in consultas:
                if c.fechaConsulta == date.today():
                    consultas_hoy += 1
        
        return render_template("menu.html", 
                             rol="nutriologo",
                             total_pacientes=total_pacientes,
                             consultas_hoy=consultas_hoy)
    else:
        # Datos para paciente
        paciente = DatabaseService.get_paciente_by_id(session.get("paciente_id"))
        consultas = DatabaseService.get_consultas_by_paciente(session.get("paciente_id"))
        
        # Buscar plan activo
        plan_activo = None
        for c in consultas:
            planes = DatabaseService.get_planes_by_consulta(c.idConsulta)
            for p in planes:
                if p.activo:
                    plan_activo = p
                    break
            if plan_activo:
                break
        
        return render_template("menu.html",
                             rol="paciente",
                             paciente=paciente,
                             consultas=consultas[:5],
                             plan_activo=plan_activo)

# ==================== API REST ====================

@app.route('/api/paciente', methods=['GET'])
def get_pacientes_api():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pacientes") 
    datos = cursor.fetchall()
    cursor.close()
    return jsonify(datos)

@app.route('/api/paciente/<int:id>', methods=['GET'])
def get_paciente_api(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE idPaciente = %s", (id,))
    fila = cursor.fetchone()
    cursor.close()
    
    if fila:
        return jsonify(fila)
    return jsonify({"mensaje": "Paciente no encontrado"}), 404

@app.route('/api/paciente', methods=['POST'])
def add_paciente_api():
    data = request.get_json()
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO pacientes (nombre, apP, apM, sexo, edadNac, telefono, nutriologo_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data['nombre'], data['apP'], data['apM'], data['sexo'], data['edadNac'], data['telefono'], data.get('nutriologo_id', 1))
    )
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Paciente agregado correctamente"}), 201

@app.route('/api/paciente/<int:id>', methods=['PUT'])
def update_paciente_api(id):
    data = request.get_json()
    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE pacientes SET nombre=%s, apP=%s, apM=%s, sexo=%s, edadNac=%s, telefono=%s WHERE idPaciente=%s",
        (data['nombre'], data['apP'], data['apM'], data['sexo'], data['edadNac'], data['telefono'], id)
    )
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Paciente actualizado correctamente"})

@app.route('/api/paciente/<int:id>', methods=['DELETE'])
def delete_paciente_api(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM pacientes WHERE idPaciente=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"mensaje": "Paciente eliminado correctamente"})

if __name__ == "__main__":
    app.run(debug=False)