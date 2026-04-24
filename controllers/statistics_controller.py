from flask import Blueprint, render_template, jsonify, session, redirect, url_for
from services.statistics_service import StatisticsService
from services.db_service import DatabaseService

statistics_bp = Blueprint('statistics', __name__, url_prefix='/estadisticas')

@statistics_bp.route('/')
def index():
    """Página principal de estadísticas"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('statistics/index.html')

@statistics_bp.route('/nutriologo')
def nutritionist_stats():
    """Estadísticas para nutriólogo"""
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    return render_template('statistics/nutritionist.html')

@statistics_bp.route('/paciente/<int:paciente_id>')
def patient_stats(paciente_id):
    """Estadísticas de un paciente específico"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    paciente = DatabaseService.get_paciente_by_id(paciente_id)
    
    # Verificar permisos
    if session.get('user_rol') == 'nutriologo' and paciente.nutriologo_id != session.get('nutriologo_id'):
        return redirect(url_for('main.dashboard'))
    
    if session.get('user_rol') == 'paciente' and session.get('paciente_id') != paciente_id:
        return redirect(url_for('main.dashboard'))
    
    return render_template('statistics/patient.html', paciente=paciente)

@statistics_bp.route('/api/patient-evolution/<int:paciente_id>')
def api_patient_evolution(paciente_id):
    """API para obtener evolución del paciente"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = StatisticsService.get_patient_evolution(paciente_id)
    
    if not data or not data['fechas']:
        return jsonify({'error': 'No hay datos suficientes'}), 404
    
    return jsonify({
        'success': True,
        'pesos': data['pesos'],
        'imcs': data['imcs'],
        'fechas': [f.strftime('%Y-%m-%d') for f in data['fechas']]
    })

@statistics_bp.route('/api/weight-chart/<int:paciente_id>')
def api_weight_chart(paciente_id):
    """API para obtener gráfico de peso"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = StatisticsService.get_patient_evolution(paciente_id)
    chart = StatisticsService.create_weight_chart(data)
    
    if not chart:
        return jsonify({'error': 'No hay datos suficientes'}), 404
    
    return jsonify({'success': True, 'chart': chart})

@statistics_bp.route('/api/imc-chart/<int:paciente_id>')
def api_imc_chart(paciente_id):
    """API para obtener gráfico de IMC"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = StatisticsService.get_patient_evolution(paciente_id)
    chart = StatisticsService.create_imc_chart(data)
    
    if not chart:
        return jsonify({'error': 'No hay datos suficientes'}), 404
    
    return jsonify({'success': True, 'chart': chart})

@statistics_bp.route('/api/nutritionist-stats')
def api_nutritionist_stats():
    """API para obtener estadísticas del nutriólogo"""
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return jsonify({'error': 'No autorizado'}), 401
    
    stats = StatisticsService.get_nutritionist_statistics(session.get('nutriologo_id'))
    gender_chart = StatisticsService.create_gender_chart(stats['generos'])
    age_chart = StatisticsService.create_age_chart(stats['rangos_edad'])
    
    # Obtener consultas recientes
    consultas = StatisticsService.get_recent_consultations(session.get('nutriologo_id'))
    consultations_chart = StatisticsService.create_consultations_chart(consultas)
    
    return jsonify({
        'success': True,
        'stats': stats,
        'gender_chart': gender_chart,
        'age_chart': age_chart,
        'consultations_chart': consultations_chart
    })