from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from services.report_service import ReportService
from services.db_service import DatabaseService
import io
import pandas as pd

report_bp = Blueprint('report', __name__, url_prefix='/reportes')

@report_bp.route('/')
def index():
    """Página principal de reportes"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('report/index.html')

@report_bp.route('/exportar/pacientes')
def exportar_pacientes():
    """Exportar todos los pacientes del nutriólogo"""
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        flash('No autorizado', 'error')
        return redirect(url_for('report.index'))
    
    pacientes = DatabaseService.get_pacientes(nutriologo_id=session.get('nutriologo_id'))
    
    if not pacientes:
        flash('No hay pacientes para exportar', 'warning')
        return redirect(url_for('report.index'))
    
    return ReportService.export_pacientes_to_excel(pacientes)

@report_bp.route('/exportar/consultas/<int:paciente_id>')
def exportar_consultas(paciente_id):
    """Exportar consultas de un paciente específico"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    paciente = DatabaseService.get_paciente_by_id(paciente_id)
    
    # Verificar permisos
    if session.get('user_rol') == 'nutriologo' and paciente.nutriologo_id != session.get('nutriologo_id'):
        flash('No autorizado', 'error')
        return redirect(url_for('report.index'))
    
    if session.get('user_rol') == 'paciente' and session.get('paciente_id') != paciente_id:
        flash('No autorizado', 'error')
        return redirect(url_for('report.index'))
    
    consultas = DatabaseService.get_consultas_by_paciente(paciente_id)
    
    if not consultas:
        flash('No hay consultas para exportar', 'warning')
        return redirect(url_for('pacientes.detalle', id=paciente_id))
    
    return ReportService.export_consultas_to_excel(consultas, paciente.nombre_completo)

@report_bp.route('/exportar/resumen')
def exportar_resumen():
    """Exportar resumen completo del nutriólogo"""
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        flash('No autorizado', 'error')
        return redirect(url_for('report.index'))
    
    from services.statistics_service import StatisticsService
    
    pacientes = DatabaseService.get_pacientes(nutriologo_id=session.get('nutriologo_id'))
    estadisticas = StatisticsService.get_nutritionist_statistics(session.get('nutriologo_id'))
    
    if not pacientes:
        flash('No hay datos para exportar', 'warning')
        return redirect(url_for('report.index'))
    
    return ReportService.export_resumen_nutriologo_to_excel(pacientes, estadisticas)

@report_bp.route('/importar/pacientes', methods=['GET', 'POST'])
def importar_pacientes():
    """Importar pacientes desde Excel"""
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        flash('No autorizado', 'error')
        return redirect(url_for('report.index'))
    
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        file = request.files['archivo']
        
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            flash('Formato no válido. Use archivos .xlsx o .xls', 'error')
            return redirect(request.url)
        
        # Procesar importación
        resultado = ReportService.import_pacientes_from_excel(file, session.get('nutriologo_id'))
        
        if 'error' in resultado:
            flash(resultado['error'], 'error')
        else:
            flash(f"Importación completada: {resultado['importados']} de {resultado['total']} pacientes importados", 'success')
            
            if resultado['errores']:
                for error in resultado['errores'][:5]:  # Mostrar solo primeros 5 errores
                    flash(f"Error fila {error['fila']}: {error['error']}", 'warning')
    
    return render_template('report/importar_pacientes.html')
 

@report_bp.route('/importar/consultas/<int:paciente_id>', methods=['GET', 'POST'])
def importar_consultas(paciente_id):
    """Importar consultas desde Excel para un paciente"""
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        flash('No autorizado', 'error')
        return redirect(url_for('report.index'))
    
    paciente = DatabaseService.get_paciente_by_id(paciente_id)
    
    if not paciente or paciente.nutriologo_id != session.get('nutriologo_id'):
        flash('Paciente no encontrado', 'error')
        return redirect(url_for('report.index'))
    
    if request.method == 'POST':
        if 'archivo' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        file = request.files['archivo']
        
        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            flash('Formato no válido. Use archivos .xlsx o .xls', 'error')
            return redirect(request.url)
        
        # Guardar nutriologo_id en variable local para pasarlo al servicio
        nutriologo_id = session.get('nutriologo_id')
        
        # Llamar al servicio con los parámetros correctos
        resultado = ReportService.import_consultas_from_excel(file, paciente_id, nutriologo_id)
        
        if 'error' in resultado:
            flash(resultado['error'], 'error')
        else:
            flash(f"Importación completada: {resultado['importados']} de {resultado['total']} consultas importadas", 'success')
            
            if resultado['errores']:
                for error in resultado['errores'][:5]:
                    flash(f"Error fila {error['fila']}: {error['error']}", 'warning')
            
            return redirect(url_for('pacientes.detalle', id=paciente_id))
    
    return render_template('report/importar_consultas.html', paciente=paciente)

@report_bp.route('/plantilla/pacientes')
def plantilla_pacientes():
    """Descargar plantilla para importar pacientes"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    import pandas as pd
    import io
    
    # Crear plantilla
    data = {
        'Nombre': ['Ejemplo'],
        'Apellido Paterno': ['Pérez'],
        'Apellido Materno': ['García'],
        'Sexo': ['M'],
        'Fecha Nacimiento': ['01/01/1990'],
        'Teléfono': ['555-1234567']
    }
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Pacientes', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name='plantilla_pacientes.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@report_bp.route('/plantilla/consultas')
def plantilla_consultas():
    """Descargar plantilla para importar consultas"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    import pandas as pd
    import io
    
    # Crear plantilla
    data = {
        'Fecha': ['01/01/2024'],
        'Hora Entrada': ['10:00'],
        'Hora Salida': ['11:00'],
        'Descripción': ['Consulta de seguimiento'],
        'Peso (kg)': [70.5],
        'Estatura (m)': [1.75],
        'Diagnóstico': ['Paciente con buen progreso']
    }
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Consultas', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name='plantilla_consultas.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )