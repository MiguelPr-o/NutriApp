from flask import Blueprint, render_template, request, jsonify, session, current_app, redirect, url_for, flash
from services.osm_service import OSMService

osm_bp = Blueprint('osm', __name__, url_prefix='/osm')

@osm_bp.route('/')
def index():
    """Página principal de mapas con OpenStreetMap"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('osm/index.html')

@osm_bp.route('/buscar')
def buscar():
    """Página de búsqueda de lugares"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('osm/buscar.html')

@osm_bp.route('/api/geocode', methods=['POST'])
def api_geocode():
    """API endpoint para geocodificar direcciones"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    address = data.get('address')
    
    if not address:
        return jsonify({'error': 'Se requiere dirección'}), 400
    
    result = OSMService.geocode_address(address)
    
    if result:
        return jsonify({'success': True, 'result': result})
    else:
        return jsonify({'error': 'No se pudo geocodificar la dirección'}), 400

@osm_bp.route('/api/reverse', methods=['POST'])
def api_reverse():
    """API endpoint para reverse geocoding"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    
    if not lat or not lon:
        return jsonify({'error': 'Se requieren latitud y longitud'}), 400
    
    result = OSMService.reverse_geocode(lat, lon)
    
    if result:
        return jsonify({'success': True, 'result': result})
    else:
        return jsonify({'error': 'No se pudo obtener la dirección'}), 400

@osm_bp.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint para buscar lugares por texto"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    query = data.get('query')
    limit = data.get('limit', 10)
    
    if not query:
        return jsonify({'error': 'Se requiere término de búsqueda'}), 400
    
    results = OSMService.search_places(query, limit)
    
    return jsonify({'success': True, 'results': results})

@osm_bp.route('/api/nearby', methods=['POST'])
def api_nearby():
    """API endpoint para buscar lugares cercanos usando Overpass API"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    place_type = data.get('place_type')
    radius = data.get('radius', 1000)
    
    if not lat or not lon:
        return jsonify({'error': 'Se requieren latitud y longitud'}), 400
    
    results = OSMService.search_nearby_places(lat, lon, place_type, radius)
    
    return jsonify({'success': True, 'results': results})

@osm_bp.route('/api/distance', methods=['POST'])
def api_distance():
    """API endpoint para calcular distancia entre dos puntos"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    lat1 = data.get('lat1')
    lon1 = data.get('lon1')
    lat2 = data.get('lat2')
    lon2 = data.get('lon2')
    
    if None in (lat1, lon1, lat2, lon2):
        return jsonify({'error': 'Se requieren coordenadas para ambos puntos'}), 400
    
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = OSMService.calculate_distance(point1, point2)
    
    return jsonify({'success': True, 'distance_km': distance})

@osm_bp.route('/consultorios')
def consultorios():
    """Página de consultorios en el mapa"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Obtener consultorios de la base de datos usando current_app
    cursor = current_app.mysql.connection.cursor()
    cursor.execute("SELECT * FROM consultorios WHERE activo = 1")
    consultorios = cursor.fetchall()
    cursor.close()
    
    return render_template('osm/consultorios.html', consultorios=consultorios)

@osm_bp.route('/lugares-saludables')
def lugares_saludables():
    """Página de lugares saludables cercanos"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('osm/lugares_saludables.html')

@osm_bp.route('/registrar-consultorio', methods=['GET', 'POST'])
def registrar_consultorio():
    """Registrar un nuevo consultorio (solo nutriólogos)"""
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form.get('telefono')
        horario = request.form.get('horario')
        
        # Geocodificar dirección para obtener coordenadas
        geocoded = OSMService.geocode_address(direccion)
        
        if not geocoded:
            flash('No se pudo geocodificar la dirección. Verifica que sea correcta.', 'error')
            return render_template('osm/registrar_consultorio.html')
        
        cursor = current_app.mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO consultorios (nutriologo_id, nombre, direccion, latitud, longitud, telefono, horario)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], nombre, geocoded['direccion_completa'],
              geocoded['lat'], geocoded['lon'], telefono, horario))
        current_app.mysql.connection.commit()
        cursor.close()
        
        flash('Consultorio registrado exitosamente', 'success')
        return redirect(url_for('osm.consultorios'))
    
    return render_template('osm/registrar_consultorio.html')


@osm_bp.route('/api/nearby-v2', methods=['POST'])
def api_nearby_v2():
    """API endpoint mejorado para buscar lugares cercanos"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    place_type = data.get('place_type')
    radius = data.get('radius', 2000)
    
    if not lat or not lon:
        return jsonify({'error': 'Se requieren latitud y longitud'}), 400
    
    if place_type == 'todos':
        results = OSMService.search_all_categories(lat, lon, radius)
    else:
        results = OSMService.search_nearby_places_v2(lat, lon, place_type, radius)
    
    return jsonify({'success': True, 'results': results})

@osm_bp.route('/api/search-by-name', methods=['POST'])
def api_search_by_name():
    """API endpoint para buscar lugares por nombre"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    query = data.get('query')
    radius = data.get('radius', 3000)
    
    if not lat or not lon:
        return jsonify({'error': 'Se requieren latitud y longitud'}), 400
    
    if not query:
        return jsonify({'error': 'Se requiere término de búsqueda'}), 400
    
    results = OSMService.search_by_name(lat, lon, query, radius)
    
    return jsonify({'success': True, 'results': results})

@osm_bp.route('/api/all-categories', methods=['POST'])
def api_all_categories():
    """API endpoint para buscar todas las categorías a la vez"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    radius = data.get('radius', 2000)
    
    if not lat or not lon:
        return jsonify({'error': 'Se requieren latitud y longitud'}), 400
    
    results = OSMService.search_all_categories(lat, lon, radius)
    
    return jsonify({'success': True, 'results': results})