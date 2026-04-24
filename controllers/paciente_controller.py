from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.db_service import DatabaseService
import random, string

paciente_bp = Blueprint('pacientes', __name__, url_prefix='/pacientes')

@paciente_bp.route('/')
def lista():
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    # Obtener parámetros de búsqueda
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    
    # Obtener todos los pacientes del nutriólogo
    pacientes = DatabaseService.get_pacientes(nutriologo_id=session.get('nutriologo_id'))
    
    # Aplicar filtro SOLO por nombre
    if search:
        pacientes = [p for p in pacientes if 
                    search.lower() in p.nombre.lower() or 
                    search.lower() in p.apP.lower() or 
                    (p.apM and search.lower() in p.apM.lower())]
    
    # Paginación
    per_page = 10
    total = len(pacientes)
    start = (page - 1) * per_page
    end = start + per_page
    pacientes_pagina = pacientes[start:end]
    
    return render_template('pacientes/lista.html', 
                         pacientes=pacientes_pagina,
                         page=page,
                         total=total,
                         per_page=per_page,
                         search=search)

def generar_password_temp(longitud=8):
    """Genera una contraseña temporal aleatoria"""
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for i in range(longitud))

@paciente_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apP = request.form['apP']
        apM = request.form.get('apM', '')
        sexo = request.form['sexo']
        edadNac = request.form['edadNac']
        telefono = request.form.get('telefono', '')
        email = request.form.get('email', '')  # Campo nuevo: email del paciente
        
        # Validar email
        if not email:
            flash('El email es obligatorio para que el paciente pueda acceder', 'error')
            return render_template('pacientes/formulario.html', titulo='Nuevo Paciente')
        
        # Verificar si el email ya existe
        if DatabaseService.get_user_by_email(email):
            flash('Ya existe un usuario con este email', 'error')
            return render_template('pacientes/formulario.html', titulo='Nuevo Paciente')
        
        # Crear paciente
        paciente_id = DatabaseService.create_paciente(
            nombre, apP, apM, sexo, edadNac, telefono,
            session.get('nutriologo_id')
        )
        
        # Generar contraseña temporal
        password_temp = generar_password_temp()
        
        # Crear usuario para el paciente
        DatabaseService.create_usuario(
            email=email,
            password=password_temp,
            rol='paciente',
            nutriologo_id=None,
            paciente_id=paciente_id
        )
        
        # Mostrar credenciales al nutriólogo
        flash(f'Paciente registrado exitosamente. Credenciales temporales:', 'success')
        flash(f'Email: {email}', 'info')
        flash(f'Contraseña temporal: {password_temp}', 'info')
        flash('El paciente deberá cambiar su contraseña al primer inicio de sesión.', 'warning')
        
        return redirect(url_for('pacientes.detalle', id=paciente_id))
    
    return render_template('pacientes/formulario.html', titulo='Nuevo Paciente')

@paciente_bp.route('/<int:id>')
def detalle(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    paciente = DatabaseService.get_paciente_by_id(id)
    if not paciente:
        return redirect(url_for('pacientes.lista'))
    
    # Verificar permisos
    if session.get('user_rol') == 'nutriologo' and paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('main.menu'))
    
    if session.get('user_rol') == 'paciente' and session.get('paciente_id') != id:
        return redirect(url_for('main.menu'))
    
    consultas = DatabaseService.get_consultas_by_paciente(id)
    
    return render_template('pacientes/detalle.html', paciente=paciente, consultas=consultas)

@paciente_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    paciente = DatabaseService.get_paciente_by_id(id)
    if not paciente or paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('pacientes.lista'))
    
    if request.method == 'POST':
        DatabaseService.update_paciente(
            id,
            request.form['nombre'],
            request.form['apP'],
            request.form.get('apM', ''),
            request.form['sexo'],
            request.form['edadNac'],
            request.form.get('telefono', '')
        )
        return redirect(url_for('pacientes.detalle', id=id))
    
    return render_template('pacientes/formulario.html', paciente=paciente, titulo='Editar Paciente')

@paciente_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar(id):
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    paciente = DatabaseService.get_paciente_by_id(id)
    if paciente and paciente.nutriologo_id == session.get('nutriologo_id'):
        DatabaseService.delete_paciente(id)
    
    return redirect(url_for('pacientes.lista'))