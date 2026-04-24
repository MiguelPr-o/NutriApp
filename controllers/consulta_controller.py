from flask import Blueprint, render_template, request, redirect, url_for, session
from services.db_service import DatabaseService
from models.models import Diagnostico

consulta_bp = Blueprint('consultas', __name__, url_prefix='/consultas')

@consulta_bp.route('/nueva/<int:paciente_id>', methods=['GET', 'POST'])
def nueva(paciente_id):
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    paciente = DatabaseService.get_paciente_by_id(paciente_id)
    if not paciente or paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('pacientes.lista'))
    
    if request.method == 'POST':
        # Crear consulta
        consulta_id = DatabaseService.create_consulta(
            request.form['fechaConsulta'],
            request.form['horaE'],
            request.form['horaS'],
            request.form['descripcion'],
            paciente_id
        )
        
        # Calcular IMC
        peso = float(request.form['peso'])
        estatura = float(request.form['estatura'])
        imc = round(peso / (estatura ** 2), 2)
        
        # Crear diagnóstico
        DatabaseService.create_diagnostico(
            peso,
            estatura,
            imc,
            request.form['diagnostico_desc'],
            consulta_id,
            session.get('nutriologo_id')
        )
        
        return redirect(url_for('pacientes.detalle', id=paciente_id))
    
    return render_template('consultas/nueva.html', paciente=paciente)

@consulta_bp.route('/<int:id>')
def detalle(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    consulta = DatabaseService.get_consulta_by_id(id)
    if not consulta:
        return redirect(url_for('main.menu'))
    
    paciente = DatabaseService.get_paciente_by_id(consulta.paciente_id)
    
    # Verificar permisos
    if session.get('user_rol') == 'nutriologo' and paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('main.menu'))
    
    if session.get('user_rol') == 'paciente' and session.get('paciente_id') != paciente.idPaciente:
        return redirect(url_for('main.menu'))
    
    planes = DatabaseService.get_planes_by_consulta(id)
    
    return render_template('consultas/detalle.html', consulta=consulta, planes=planes)

@consulta_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    consulta = DatabaseService.get_consulta_by_id(id)
    if not consulta:
        return redirect(url_for('main.menu'))
    
    paciente = DatabaseService.get_paciente_by_id(consulta.paciente_id)
    if paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('main.menu'))
    
    if request.method == 'POST':
        # Actualizar consulta
        DatabaseService.update_consulta(
            id,
            request.form['fechaConsulta'],
            request.form['horaE'],
            request.form['horaS'],
            request.form['descripcion']
        )
        
        # Actualizar diagnóstico
        if consulta.diagnostico:
            peso = float(request.form['peso'])
            estatura = float(request.form['estatura'])
            imc = round(peso / (estatura ** 2), 2)
            
            DatabaseService.update_diagnostico(
                consulta.diagnostico.idDiagnostico,
                peso,
                estatura,
                imc,
                request.form['diagnostico_desc']
            )
        
        return redirect(url_for('consultas.detalle', id=id))
    
    return render_template('consultas/nueva.html', consulta=consulta, paciente=paciente, editar=True)