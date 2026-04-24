from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services.db_service import DatabaseService
import re

auth_bp = Blueprint('auth', __name__)

def validar_email(email):
    """Valida el formato del email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_telefono(telefono):
    """Valida que el teléfono tenga 10 dígitos (opcional)"""
    if not telefono:
        return True  # Campo opcional
    return re.match(r'^\d{10}$', telefono) is not None

def validar_contraseña(password):
    """Valida que la contraseña tenga al menos 8 caracteres"""
    return len(password) >= 8

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validaciones
        if not email:
            flash('El correo electrónico es requerido', 'error')
            return render_template('login.html')
        
        if not validar_email(email):
            flash('Ingresa un correo electrónico válido (ej: usuario@dominio.com)', 'error')
            return render_template('login.html')
        
        if not password:
            flash('La contraseña es requerida', 'error')
            return render_template('login.html')
        
        # Buscar usuario
        user = DatabaseService.get_user_by_email(email)
        
        if user and DatabaseService.hash_password(password) == user.password_hash:
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_rol'] = user.rol
            session['nutriologo_id'] = user.nutriologo_id
            session['paciente_id'] = user.paciente_id
            
            return redirect(url_for('menu'))
        else:
            flash('Correo o contraseña incorrectos', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apP = request.form.get('apP', '').strip()
        apM = request.form.get('apM', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        sexo = request.form.get('sexo', '')
        edadNac = request.form.get('edadNac', '')
        telefono = request.form.get('telefono', '').strip()
        
        errores = []
        
        # Validación de nombre
        if not nombre:
            errores.append('El nombre es requerido')
        
        # Validación de apellido paterno
        if not apP:
            errores.append('El apellido paterno es requerido')
        
        # Validación de email
        if not email:
            errores.append('El correo electrónico es requerido')
        elif not validar_email(email):
            errores.append('Ingresa un correo electrónico válido (ej: usuario@dominio.com)')
        elif DatabaseService.get_user_by_email(email):
            errores.append('Este correo electrónico ya está registrado')
        
        # Validación de contraseña
        if not password:
            errores.append('La contraseña es requerida')
        elif not validar_contraseña(password):
            errores.append('La contraseña debe tener al menos 8 caracteres')
        
        # Validación de confirmación de contraseña
        if password != confirm_password:
            errores.append('Las contraseñas no coinciden')
        
        # Validación de sexo
        if not sexo:
            errores.append('El sexo es requerido')
        
        # Validación de fecha de nacimiento
        if not edadNac:
            errores.append('La fecha de nacimiento es requerida')
        
        # Validación de teléfono (opcional)
        if telefono and not validar_telefono(telefono):
            errores.append('El teléfono debe tener 10 dígitos')
        
        # Si hay errores, mostrarlos
        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('register.html', 
                                 nombre=nombre, apP=apP, apM=apM, 
                                 email=email, telefono=telefono, sexo=sexo)
        
        # Obtener el primer nutriólogo disponible
        nutriologo = DatabaseService.get_primer_nutriologo()
        
        if not nutriologo:
            flash('Error en el sistema. Contacte al administrador.', 'error')
            return render_template('register.html')
        
        # Crear paciente
        paciente_id = DatabaseService.create_paciente(
            nombre, apP, apM, sexo, edadNac, telefono, nutriologo['idNutriologo']
        )
        
        # Crear usuario
        DatabaseService.create_usuario(email, password, 'paciente', None, paciente_id)
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('auth.login'))