from flask import Blueprint, render_template, request, jsonify
from services.youtube_service import YouTubeService

youtube_bp = Blueprint('youtube', __name__, url_prefix='/youtube')

# Temas predeterminados de nutrición
TEMAS_NUTRICION = [
    {'id': 'alimentacion-saludable', 'nombre': 'Alimentación Saludable', 'icono': ''},
    {'id': 'proteinas', 'nombre': 'Proteínas y Musculación', 'icono': ''},
    {'id': 'vitaminas', 'nombre': 'Vitaminas y Minerales', 'icono': ''},
    {'id': 'dietas', 'nombre': 'Dietas Populares', 'icono': ''},
    {'id': 'recetas', 'nombre': 'Recetas Saludables', 'icono': ''},
    {'id': 'ejercicio', 'nombre': 'Ejercicio y Nutrición', 'icono': ''},
    {'id': 'perder-peso', 'nombre': 'Cómo Perder Peso', 'icono': ''},
    {'id': 'ganar-masa', 'nombre': 'Ganar Masa Muscular', 'icono': ''},
    {'id': 'alimentos', 'nombre': 'Superalimentos', 'icono': ''},
    {'id': 'hidratacion', 'nombre': 'Hidratación', 'icono': ''},
]

@youtube_bp.route('/')
def index():
    """Página principal de YouTube con temas predeterminados"""
    return render_template('youtube/index.html', temas=TEMAS_NUTRICION)

@youtube_bp.route('/buscar')
def buscar():
    """Página de búsqueda de videos"""
    query = request.args.get('q', '')
    if query:
        videos = YouTubeService.search_videos(f"nutrición {query}", max_results=12)
    else:
        # Videos predeterminados de nutrición
        videos = YouTubeService.search_videos("consejos nutrición saludable", max_results=12)
    
    return render_template('youtube/buscar.html', videos=videos, query=query)

@youtube_bp.route('/tema/<tema_id>')
def tema(tema_id):
    """Muestra videos de un tema específico"""
    # Mapear IDs a consultas de búsqueda
    temas_query = {
        'alimentacion-saludable': 'alimentación saludable consejos',
        'proteinas': 'proteínas alimentos para músculos',
        'vitaminas': 'vitaminas y minerales para la salud',
        'dietas': 'dietas saludables para bajar de peso',
        'recetas': 'recetas saludables y nutritivas',
        'ejercicio': 'ejercicio y nutrición para principiantes',
        'perder-peso': 'cómo perder peso saludablemente',
        'ganar-masa': 'cómo ganar masa muscular rápidamente',
        'alimentos': 'superalimentos para la salud',
        'hidratacion': 'importancia de la hidratación'
    }
    
    # Encontrar el tema seleccionado
    tema_seleccionado = next((t for t in TEMAS_NUTRICION if t['id'] == tema_id), None)
    
    if not tema_seleccionado:
        return render_template('youtube/index.html', temas=TEMAS_NUTRICION, error="Tema no encontrado")
    
    query = temas_query.get(tema_id, tema_seleccionado['nombre'])
    videos = YouTubeService.search_videos(query, max_results=15)
    
    return render_template('youtube/tema.html', tema=tema_seleccionado, videos=videos)

@youtube_bp.route('/video/<video_id>')
def video(video_id):
    """Muestra un video específico"""
    video = YouTubeService.get_video_details(video_id)
    if not video:
        return render_template('youtube/index.html', temas=TEMAS_NUTRICION, error="Video no encontrado")
    
    # Videos relacionados
    relacionados = YouTubeService.search_videos(video['titulo'], max_results=6)
    
    return render_template('youtube/video.html', video=video, relacionados=relacionados)

@youtube_bp.route('/api/buscar', methods=['GET'])
def api_buscar():
    """API endpoint para búsqueda AJAX"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Se requiere un término de búsqueda'}), 400
    
    videos = YouTubeService.search_videos(query, max_results=10)
    return jsonify({'videos': videos})