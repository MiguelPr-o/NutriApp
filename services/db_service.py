import MySQLdb
from flask_mysqldb import MySQL
from models.models import Nutriologo, Paciente, Consulta, Diagnostico, PlanAlimenticio, Usuario
from datetime import datetime, time, timedelta
import hashlib

# Variable global para MySQL (se inicializará en app.py)
mysql = None

def init_db(mysql_instance):
    global mysql
    mysql = mysql_instance

class DatabaseService:
    
    # ==================== UTILIDADES ====================
    @staticmethod
    def hash_password(password):
        """Devuelve la misma contraseña (para compatibilidad con texto plano)"""
        return password
    
    @staticmethod
    def _convert_timedelta_to_time(td):
        """Convierte un timedelta a objeto time"""
        if td is None:
            return None
        if isinstance(td, timedelta) or hasattr(td, 'seconds'):
            hours = td.seconds // 3600
            minutes = (td.seconds % 3600) // 60
            return time(hour=hours, minute=minutes)
        return td
    
    # ==================== NUTRIOLOGOS ====================
    @staticmethod
    def get_primer_nutriologo():
        """Obtiene el primer nutriólogo disponible"""
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT idNutriologo, nombre, apP, apM, correoElec, telefono FROM nutriologos LIMIT 1")
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                print(f"Nutriólogo encontrado: {result}")
                return {
                    'idNutriologo': result['idNutriologo'],
                    'nombre': result['nombre'],
                    'apP': result['apP'],
                    'apM': result['apM'],
                    'correoElec': result['correoElec'],
                    'telefono': result['telefono']
                }
            return None
        except Exception as e:
            print(f"Error en get_primer_nutriologo: {e}")
            return None
         
    @staticmethod
    def get_nutriologo_by_email(email):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT idNutriologo, nombre, apP, apM, correoElec, telefono FROM nutriologos WHERE correoElec = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return {
                'idNutriologo': result['idNutriologo'],
                'nombre': result['nombre'],
                'apP': result['apP'],
                'apM': result['apM'],
                'correoElec': result['correoElec'],
                'telefono': result['telefono']
            }
        return None
    
    @staticmethod
    def create_nutriologo(nombre, apP, apM, correoElec, telefono):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO nutriologos (nombre, apP, apM, correoElec, telefono)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apP, apM, correoElec, telefono))
        mysql.connection.commit()
        nutriologo_id = cursor.lastrowid
        cursor.close()
        return nutriologo_id
    
    # ==================== USUARIOS ====================
    @staticmethod
    def get_user_by_email(email):
        print(f"=== Buscando usuario por email: '{email}' ===")
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id, email, password, rol, nutriologo_id, paciente_id FROM usuarios WHERE email = %s", (email,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                print(f"Usuario encontrado en DB:")
                print(f"  Tipo de resultado: {type(result)}")
                print(f"  Resultado completo: {result}")
                
                user = Usuario()
                user.id = result['id']
                user.email = result['email']
                user.password_hash = result['password']
                user.rol = result['rol']
                user.nutriologo_id = result['nutriologo_id']
                user.paciente_id = result['paciente_id']
                
                print(f"  Usuario creado: id={user.id}, email={user.email}, rol={user.rol}")
                return user
            else:
                print(f"No se encontró usuario con email: '{email}'")
                return None
        except Exception as e:
            print(f"Error en get_user_by_email: {e}")
            import traceback
            traceback.print_exc()
            return None

    @staticmethod
    def create_usuario(email, password, rol, nutriologo_id=None, paciente_id=None):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO usuarios (email, password, rol, nutriologo_id, paciente_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, password, rol, nutriologo_id, paciente_id))
        mysql.connection.commit()
        user_id = cursor.lastrowid
        cursor.close()
        return user_id
    
    # ==================== PACIENTES ====================
    @staticmethod
    def get_pacientes(nutriologo_id=None, search=None):
        cursor = mysql.connection.cursor()
        query = "SELECT idPaciente, nombre, apP, apM, sexo, edadNac, telefono, nutriologo_id FROM pacientes"
        params = []
        
        if nutriologo_id:
            query += " WHERE nutriologo_id = %s"
            params.append(nutriologo_id)
            
            if search:
                query += " AND (nombre LIKE %s OR apP LIKE %s OR telefono LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
        elif search:
            query += " WHERE nombre LIKE %s OR apP LIKE %s OR telefono LIKE %s"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        query += " ORDER BY apP, nombre"
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        
        pacientes = []
        for row in results:
            paciente = Paciente()
            paciente.idPaciente = row['idPaciente']
            paciente.nombre = row['nombre']
            paciente.apP = row['apP']
            paciente.apM = row['apM']
            paciente.sexo = row['sexo']
            paciente.edadNac = row['edadNac']
            paciente.telefono = row['telefono']
            paciente.nutriologo_id = row['nutriologo_id']
            pacientes.append(paciente)
        
        return pacientes
    
    @staticmethod
    def get_paciente_by_id(id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT idPaciente, nombre, apP, apM, sexo, edadNac, telefono, nutriologo_id 
            FROM pacientes 
            WHERE idPaciente = %s
        """, (id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            paciente = Paciente()
            paciente.idPaciente = result['idPaciente']
            paciente.nombre = result['nombre']
            paciente.apP = result['apP']
            paciente.apM = result['apM']
            paciente.sexo = result['sexo']
            paciente.edadNac = result['edadNac']
            paciente.telefono = result['telefono']
            paciente.nutriologo_id = result['nutriologo_id']
            return paciente
        return None
    
    @staticmethod
    def create_paciente(nombre, apP, apM, sexo, edadNac, telefono, nutriologo_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO pacientes (nombre, apP, apM, sexo, edadNac, telefono, nutriologo_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, apP, apM, sexo, edadNac, telefono, nutriologo_id))
        mysql.connection.commit()
        paciente_id = cursor.lastrowid
        cursor.close()
        return paciente_id
    
    @staticmethod
    def update_paciente(id, nombre, apP, apM, sexo, edadNac, telefono):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE pacientes 
            SET nombre = %s, apP = %s, apM = %s, sexo = %s, edadNac = %s, telefono = %s
            WHERE idPaciente = %s
        """, (nombre, apP, apM, sexo, edadNac, telefono, id))
        mysql.connection.commit()
        cursor.close()
    
    @staticmethod
    def delete_paciente(id):
        cursor = mysql.connection.cursor()
        # Primero eliminar usuario asociado
        cursor.execute("DELETE FROM usuarios WHERE paciente_id = %s", (id,))
        # Luego eliminar paciente
        cursor.execute("DELETE FROM pacientes WHERE idPaciente = %s", (id,))
        mysql.connection.commit()
        cursor.close()
    
    # ==================== CONSULTAS ====================
    @staticmethod
    def get_consultas_by_paciente(paciente_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT idConsulta, fechaConsulta, horaE, horaS, descripcion, paciente_id
            FROM consultas 
            WHERE paciente_id = %s
            ORDER BY fechaConsulta DESC, horaE DESC
        """, (paciente_id,))
        results = cursor.fetchall()
        cursor.close()
        
        consultas = []
        for row in results:
            consulta = Consulta()
            consulta.idConsulta = row['idConsulta']
            consulta.fechaConsulta = row['fechaConsulta']
            consulta.horaE = DatabaseService._convert_timedelta_to_time(row['horaE'])
            consulta.horaS = DatabaseService._convert_timedelta_to_time(row['horaS'])
            consulta.descripcion = row['descripcion']
            consulta.paciente_id = row['paciente_id']
            
            # Obtener diagnóstico de esta consulta
            consulta.diagnostico = DatabaseService.get_diagnostico_by_consulta(consulta.idConsulta)
            consultas.append(consulta)
        
        return consultas
    
    @staticmethod
    def get_consulta_by_id(id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT idConsulta, fechaConsulta, horaE, horaS, descripcion, paciente_id
            FROM consultas 
            WHERE idConsulta = %s
        """, (id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            consulta = Consulta()
            consulta.idConsulta = result['idConsulta']
            consulta.fechaConsulta = result['fechaConsulta']
            consulta.horaE = DatabaseService._convert_timedelta_to_time(result['horaE'])
            consulta.horaS = DatabaseService._convert_timedelta_to_time(result['horaS'])
            consulta.descripcion = result['descripcion']
            consulta.paciente_id = result['paciente_id']
            
            # Obtener diagnóstico
            consulta.diagnostico = DatabaseService.get_diagnostico_by_consulta(consulta.idConsulta)
            return consulta
        return None
    
    @staticmethod
    def create_consulta(fechaConsulta, horaE, horaS, descripcion, paciente_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO consultas (fechaConsulta, horaE, horaS, descripcion, paciente_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (fechaConsulta, horaE, horaS, descripcion, paciente_id))
        mysql.connection.commit()
        consulta_id = cursor.lastrowid
        cursor.close()
        return consulta_id
    
    @staticmethod
    def update_consulta(id, fechaConsulta, horaE, horaS, descripcion):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE consultas 
            SET fechaConsulta = %s, horaE = %s, horaS = %s, descripcion = %s
            WHERE idConsulta = %s
        """, (fechaConsulta, horaE, horaS, descripcion, id))
        mysql.connection.commit()
        cursor.close()
    
    # ==================== DIAGNOSTICOS ====================
    @staticmethod
    def get_diagnostico_by_consulta(consulta_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT idDiagnostico, peso, estatura, imc, descripcion, consulta_id, nutriologo_id
            FROM diagnosticos 
            WHERE consulta_id = %s
        """, (consulta_id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            diagnostico = Diagnostico()
            diagnostico.idDiagnostico = result['idDiagnostico']
            diagnostico.peso = result['peso']
            diagnostico.estatura = result['estatura']
            diagnostico.imc = result['imc']
            diagnostico.descripcion = result['descripcion']
            diagnostico.consulta_id = result['consulta_id']
            diagnostico.nutriologo_id = result['nutriologo_id']
            return diagnostico
        return None
    
    @staticmethod
    def create_diagnostico(peso, estatura, imc, descripcion, consulta_id, nutriologo_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO diagnosticos (peso, estatura, imc, descripcion, consulta_id, nutriologo_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (peso, estatura, imc, descripcion, consulta_id, nutriologo_id))
        mysql.connection.commit()
        diagnostico_id = cursor.lastrowid
        cursor.close()
        return diagnostico_id
    
    @staticmethod
    def update_diagnostico(id, peso, estatura, imc, descripcion):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE diagnosticos 
            SET peso = %s, estatura = %s, imc = %s, descripcion = %s
            WHERE idDiagnostico = %s
        """, (peso, estatura, imc, descripcion, id))
        mysql.connection.commit()
        cursor.close()
    
    # ==================== PLANES ALIMENTICIOS ====================
    @staticmethod
    def get_planes_by_consulta(consulta_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT idPlanA, descripcion, kcalD, fechaI, fechaF, consulta_id
            FROM planes_alimenticios 
            WHERE consulta_id = %s
            ORDER BY fechaI DESC
        """, (consulta_id,))
        results = cursor.fetchall()
        cursor.close()
        
        planes = []
        for row in results:
            plan = PlanAlimenticio()
            plan.idPlanA = row['idPlanA']
            plan.descripcion = row['descripcion']
            plan.kcalD = row['kcalD']
            plan.fechaI = row['fechaI']
            plan.fechaF = row['fechaF']
            plan.consulta_id = row['consulta_id']
            planes.append(plan)
        
        return planes
    
    @staticmethod
    def get_plan_by_id(id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT idPlanA, descripcion, kcalD, fechaI, fechaF, consulta_id
            FROM planes_alimenticios 
            WHERE idPlanA = %s
        """, (id,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            plan = PlanAlimenticio()
            plan.idPlanA = result['idPlanA']
            plan.descripcion = result['descripcion']
            plan.kcalD = result['kcalD']
            plan.fechaI = result['fechaI']
            plan.fechaF = result['fechaF']
            plan.consulta_id = result['consulta_id']
            return plan
        return None
    
    @staticmethod
    def create_plan(descripcion, kcalD, fechaI, fechaF, consulta_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO planes_alimenticios (descripcion, kcalD, fechaI, fechaF, consulta_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (descripcion, kcalD, fechaI, fechaF, consulta_id))
        mysql.connection.commit()
        plan_id = cursor.lastrowid
        cursor.close()
        return plan_id
    
    @staticmethod
    def update_plan(id, descripcion, kcalD, fechaI, fechaF):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE planes_alimenticios 
            SET descripcion = %s, kcalD = %s, fechaI = %s, fechaF = %s
            WHERE idPlanA = %s
        """, (descripcion, kcalD, fechaI, fechaF, id))
        mysql.connection.commit()
        cursor.close()
    
    @staticmethod
    def delete_plan(id):
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM planes_alimenticios WHERE idPlanA = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        
    @staticmethod
    def get_paciente_by_psid(psid):
        """Obtiene paciente por su PSID de Messenger"""
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE messenger_psid = %s", (psid,))
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            return Paciente.from_dict(result)
        return None

    @staticmethod
    def update_paciente_psid(paciente_id, psid):
        """Actualiza el PSID de Messenger de un paciente"""
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE pacientes SET messenger_psid = %s WHERE idPaciente = %s", (psid, paciente_id))
        mysql.connection.commit()
        cursor.close()