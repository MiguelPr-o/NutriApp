from flask import Blueprint, render_template, request, redirect, url_for, session
from services.db_service import DatabaseService

plan_bp = Blueprint('planes', __name__, url_prefix='/planes')

@plan_bp.route('/')
def lista():
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    # Obtener parámetros de búsqueda
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    
    # Obtener todos los pacientes del nutriólogo
    pacientes = DatabaseService.get_pacientes(nutriologo_id=session.get('nutriologo_id'))
    
    # Recopilar todos los planes
    todos_planes = []
    for paciente in pacientes:
        consultas = DatabaseService.get_consultas_by_paciente(paciente.idPaciente)
        for consulta in consultas:
            planes = DatabaseService.get_planes_by_consulta(consulta.idConsulta)
            for plan in planes:
                plan.paciente_nombre = paciente.nombre_completo
                plan.paciente_id = paciente.idPaciente
                plan.consulta_fecha = consulta.fechaConsulta
                todos_planes.append(plan)
    
    # Aplicar filtro SOLO por nombre del paciente
    if search:
        todos_planes = [p for p in todos_planes if 
                       search.lower() in p.paciente_nombre.lower()]
    
    # Ordenar por fecha de inicio (más reciente primero)
    todos_planes.sort(key=lambda x: x.fechaI, reverse=True)
    
    # Paginación
    per_page = 10
    total = len(todos_planes)
    start = (page - 1) * per_page
    end = start + per_page
    planes_pagina = todos_planes[start:end]
    
    return render_template('planes/lista.html', 
                         planes=planes_pagina,
                         page=page,
                         total=total,
                         per_page=per_page,
                         search=search)

@plan_bp.route('/nuevo/<int:consulta_id>', methods=['GET', 'POST'])
def nuevo(consulta_id):
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    consulta = DatabaseService.get_consulta_by_id(consulta_id)
    if not consulta:
        return redirect(url_for('main.menu'))
    
    paciente = DatabaseService.get_paciente_by_id(consulta.paciente_id)
    if paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('main.menu'))
    
    if request.method == 'POST':
        plan_id = DatabaseService.create_plan(
            request.form['descripcion'],
            request.form['kcalD'],
            request.form['fechaI'],
            request.form['fechaF'],
            consulta_id
        )
        return redirect(url_for('consultas.detalle', id=consulta_id))
    
    return render_template('planes/formulario.html', consulta=consulta, titulo='Nuevo Plan Alimenticio')

@plan_bp.route('/<int:id>')
def detalle(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    plan = DatabaseService.get_plan_by_id(id)
    if not plan:
        return redirect(url_for('main.menu'))
    
    consulta = DatabaseService.get_consulta_by_id(plan.consulta_id)
    paciente = DatabaseService.get_paciente_by_id(consulta.paciente_id)
    
    # Verificar permisos
    if session.get('user_rol') == 'nutriologo' and paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('main.menu'))
    
    if session.get('user_rol') == 'paciente' and session.get('paciente_id') != paciente.idPaciente:
        return redirect(url_for('main.menu'))
    
    return render_template('planes/detalle.html', plan=plan, consulta=consulta, paciente=paciente)

@plan_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    plan = DatabaseService.get_plan_by_id(id)
    if not plan:
        return redirect(url_for('main.menu'))
    
    consulta = DatabaseService.get_consulta_by_id(plan.consulta_id)
    paciente = DatabaseService.get_paciente_by_id(consulta.paciente_id)
    
    if paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('main.menu'))
    
    if request.method == 'POST':
        DatabaseService.update_plan(
            id,
            request.form['descripcion'],
            request.form['kcalD'],
            request.form['fechaI'],
            request.form['fechaF']
        )
        return redirect(url_for('planes.detalle', id=id))
    
    return render_template('planes/formulario.html', plan=plan, consulta=consulta, titulo='Editar Plan Alimenticio')

@plan_bp.route('/<int:id>/eliminar', methods=['POST'])
def eliminar(id):
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    plan = DatabaseService.get_plan_by_id(id)
    if plan:
        consulta = DatabaseService.get_consulta_by_id(plan.consulta_id)
        paciente = DatabaseService.get_paciente_by_id(consulta.paciente_id)
        
        if paciente.nutriologo_id == session.get('nutriologo_id'):
            DatabaseService.delete_plan(id)
    
    return redirect(url_for('consultas.detalle', id=plan.consulta_id if plan else 0))