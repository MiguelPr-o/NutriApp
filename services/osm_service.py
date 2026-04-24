import requests
from flask import current_app
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import random

class OSMService:
    
    @staticmethod
    def get_geocoder():
        """Obtiene un objeto geocodificador de Nominatim"""
        user_agent = current_app.config.get('OSM_USER_AGENT', 'NutriApp/1.0')
        timeout = current_app.config.get('OSM_TIMEOUT', 10)
        
        geolocator = Nominatim(
            user_agent=user_agent,
            timeout=timeout
        )
        return geolocator
    
    @staticmethod
    def geocode_address(address):
        """Convierte una dirección en coordenadas (lat, lon) usando Nominatim"""
        try:
            geolocator = OSMService.get_geocoder()
            location = geolocator.geocode(address)
            
            if location:
                return {
                    'lat': location.latitude,
                    'lon': location.longitude,
                    'direccion_completa': location.address,
                    'raw': location.raw
                }
            return None
        except Exception as e:
            print(f"Error en geocodificación: {e}")
            return None
    
    @staticmethod
    def reverse_geocode(lat, lon):
        """Convierte coordenadas en una dirección"""
        try:
            geolocator = OSMService.get_geocoder()
            location = geolocator.reverse(f"{lat}, {lon}")
            
            if location:
                return {
                    'direccion': location.address,
                    'raw': location.raw
                }
            return None
        except Exception as e:
            print(f"Error en reverse geocoding: {e}")
            return None
    
    @staticmethod
    def calculate_distance(point1, point2):
        """Calcula la distancia entre dos puntos (lat, lon) en kilómetros"""
        try:
            distance = geodesic(point1, point2).kilometers
            return round(distance, 2)
        except Exception as e:
            print(f"Error calculando distancia: {e}")
            return None
    
    @staticmethod
    def search_nearby_places_v2(lat, lon, place_type=None, radius=2000, limit=30):
        """
        Versión mejorada de búsqueda de lugares cercanos
        Con múltiples estrategias y tags alternativos
        """
        # Estrategia 1: Tags principales
        main_tags = {
            'restaurante': ['amenity=restaurant', 'amenity=fast_food'],
            'cafe': ['amenity=cafe'],
            'gimnasio': ['leisure=fitness_centre', 'sport=gym', 'leisure=sports_centre'],
            'parque': ['leisure=park', 'leisure=garden', 'landuse=grass', 'leisure=nature_reserve'],
            'supermercado': ['shop=supermarket', 'shop=convenience', 'shop=groceries'],
            'farmacia': ['amenity=pharmacy', 'shop=chemist'],
            'clinica': ['amenity=clinic', 'healthcare=clinic', 'amenity=doctors', 'healthcare=doctor'],
            'tienda_organica': ['shop=health_food', 'shop=organic', 'shop=greengrocer'],
            'yoga': ['amenity=yoga_studio', 'sport=yoga', 'leisure=yoga'],
            'piscina': ['leisure=swimming_pool', 'sport=swimming'],
            'hospital': ['amenity=hospital', 'healthcare=hospital']
        }
        
        # Estrategia 2: Tags alternativos más amplios
        broad_tags = {
            'restaurante': 'amenity=restaurant OR amenity=fast_food OR amenity=cafe OR shop=bakery',
            'gimnasio': 'leisure=fitness_centre OR sport=gym OR leisure=sports_centre OR amenity=gym',
            'parque': 'leisure=park OR leisure=garden OR landuse=grass OR leisure=nature_reserve OR landuse=recreation_ground',
            'supermercado': 'shop=supermarket OR shop=convenience OR shop=groceries OR shop=general',
            'farmacia': 'amenity=pharmacy OR shop=chemist OR healthcare=pharmacy',
            'clinica': 'amenity=clinic OR healthcare=clinic OR amenity=doctors OR healthcare=doctor OR healthcare=healthcare'
        }
        
        # Seleccionar tags según el tipo
        if place_type in main_tags:
            tags_to_try = main_tags[place_type]
        elif place_type in broad_tags:
            tags_to_try = [broad_tags[place_type]]
        else:
            tags_to_try = [f'amenity={place_type}'] if place_type else []
        
        overpass_url = "https://overpass-api.de/api/interpreter"
        all_places = []
        seen_ids = set()
        
        for tag in tags_to_try:
            try:
                # Intentar primero con radio pequeño
                for current_radius in [radius, radius * 2, radius * 3]:
                    if len(all_places) >= limit:
                        break
                    
                    overpass_query = f"""
                    [out:json][timeout:25];
                    (
                      node[{tag}](around:{current_radius},{lat},{lon});
                      way[{tag}](around:{current_radius},{lat},{lon});
                    );
                    out body center;
                    """
                    
                    response = requests.post(overpass_url, data=overpass_query, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        elements = data.get('elements', [])
                        
                        for element in elements[:limit]:
                            if element['id'] in seen_ids:
                                continue
                            seen_ids.add(element['id'])
                            
                            if element['type'] == 'node':
                                place_lat = element['lat']
                                place_lon = element['lon']
                            else:
                                if 'center' in element:
                                    place_lat = element['center']['lat']
                                    place_lon = element['center']['lon']
                                else:
                                    continue
                            
                            distance = OSMService.calculate_distance(
                                (lat, lon), 
                                (place_lat, place_lon)
                            )
                            
                            tags = element.get('tags', {})
                            all_places.append({
                                'id': element['id'],
                                'nombre': tags.get('name', 'Sin nombre'),
                                'direccion': tags.get('addr:full', tags.get('addr:street', '')),
                                'lat': place_lat,
                                'lon': place_lon,
                                'distancia': distance,
                                'telefono': tags.get('phone', ''),
                                'horario': tags.get('opening_hours', ''),
                                'website': tags.get('website', ''),
                                'categoria': place_type
                            })
                            
                    if len(all_places) >= limit:
                        break
                        
            except Exception as e:
                print(f"Error con tag {tag}: {e}")
                continue
        
        # Ordenar por distancia
        all_places.sort(key=lambda x: x['distancia'] if x['distancia'] else 9999)
        return all_places[:limit]
    
    @staticmethod
    def search_all_categories(lat, lon, radius=2000):
        """
        Busca todas las categorías de lugares saludables a la vez
        """
        categories = ['restaurante', 'cafe', 'gimnasio', 'parque', 
                      'supermercado', 'farmacia', 'clinica', 'tienda_organica']
        
        all_places = []
        for category in categories:
            places = OSMService.search_nearby_places_v2(lat, lon, category, radius, limit=10)
            all_places.extend(places)
        
        # Eliminar duplicados
        seen = set()
        unique_places = []
        for place in all_places:
            if place['id'] not in seen:
                seen.add(place['id'])
                unique_places.append(place)
        
        unique_places.sort(key=lambda x: x['distancia'] if x['distancia'] else 9999)
        return unique_places[:30]
    
    @staticmethod
    def search_by_name(lat, lon, query, radius=3000):
        """
        Busca lugares por nombre usando Nominatim primero y luego Overpass
        """
        # Primero intentar con Nominatim
        try:
            geolocator = OSMService.get_geocoder()
            locations = geolocator.geocode(query, exactly_one=False, limit=5)
            
            results = []
            if locations:
                for loc in locations:
                    if loc:
                        distance = OSMService.calculate_distance(
                            (lat, lon), 
                            (loc.latitude, loc.longitude)
                        )
                        if distance and distance <= radius / 1000:
                            results.append({
                                'id': loc.raw.get('place_id'),
                                'nombre': loc.raw.get('display_name', '').split(',')[0],
                                'direccion': loc.address,
                                'lat': loc.latitude,
                                'lon': loc.longitude,
                                'distancia': distance,
                                'categoria': 'busqueda'
                            })
                return results
        except Exception as e:
            print(f"Error en búsqueda por nombre: {e}")
        
        # Si no hay resultados, buscar en Overpass
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["name"~"{query}"](around:{radius},{lat},{lon});
          way["name"~"{query}"](around:{radius},{lat},{lon});
        );
        out body center;
        """
        
        try:
            overpass_url = "https://overpass-api.de/api/interpreter"
            response = requests.post(overpass_url, data=overpass_query, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for element in data.get('elements', [])[:10]:
                    if element['type'] == 'node':
                        place_lat = element['lat']
                        place_lon = element['lon']
                    else:
                        if 'center' in element:
                            place_lat = element['center']['lat']
                            place_lon = element['center']['lon']
                        else:
                            continue
                    
                    distance = OSMService.calculate_distance((lat, lon), (place_lat, place_lon))
                    tags = element.get('tags', {})
                    
                    results.append({
                        'id': element['id'],
                        'nombre': tags.get('name', 'Sin nombre'),
                        'direccion': tags.get('addr:full', tags.get('addr:street', '')),
                        'lat': place_lat,
                        'lon': place_lon,
                        'distancia': distance,
                        'categoria': 'busqueda'
                    })
                
                return results
        except Exception as e:
            print(f"Error en búsqueda Overpass por nombre: {e}")
        
        return []
    
    @staticmethod
    def search_all_categories_fast(lat, lon, radius=2000):
        """
        Busca TODAS las categorías en UNA SOLA consulta (mucho más rápido)
        """
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Consulta que busca todas las categorías a la vez
        overpass_query = f"""
        [out:json][timeout:25];
        (
        node["amenity"="restaurant"](around:{radius},{lat},{lon});
        node["amenity"="cafe"](around:{radius},{lat},{lon});
        node["leisure"="fitness_centre"](around:{radius},{lat},{lon});
        node["leisure"="park"](around:{radius},{lat},{lon});
        node["shop"="supermarket"](around:{radius},{lat},{lon});
        node["shop"="health_food"](around:{radius},{lat},{lon});
        node["amenity"="pharmacy"](around:{radius},{lat},{lon});
        node["amenity"="clinic"](around:{radius},{lat},{lon});
        node["healthcare"="clinic"](around:{radius},{lat},{lon});
        );
        out body center;
        """
        
        try:
            response = requests.post(overpass_url, data=overpass_query, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Mapeo de categorías
            categoria_map = {
                'restaurant': 'restaurante',
                'cafe': 'cafe',
                'fitness_centre': 'gimnasio',
                'park': 'parque',
                'supermarket': 'supermercado',
                'health_food': 'tienda_organica',
                'pharmacy': 'farmacia',
                'clinic': 'clinica'
            }
            
            places = []
            for element in data.get('elements', []):
                tags = element.get('tags', {})
                
                # Determinar categoría
                categoria = None
                for key, value in tags.items():
                    if key == 'amenity' and value in categoria_map:
                        categoria = categoria_map[value]
                        break
                    elif key == 'leisure' and value in categoria_map:
                        categoria = categoria_map[value]
                        break
                    elif key == 'shop' and value in categoria_map:
                        categoria = categoria_map[value]
                        break
                    elif key == 'healthcare' and value in categoria_map:
                        categoria = categoria_map[value]
                        break
                
                if not categoria:
                    continue
                
                # Obtener coordenadas
                if element['type'] == 'node':
                    place_lat = element['lat']
                    place_lon = element['lon']
                else:
                    if 'center' in element:
                        place_lat = element['center']['lat']
                        place_lon = element['center']['lon']
                    else:
                        continue
                
                distance = OSMService.calculate_distance((lat, lon), (place_lat, place_lon))
                
                places.append({
                    'id': element['id'],
                    'nombre': tags.get('name', 'Sin nombre'),
                    'direccion': tags.get('addr:street', ''),
                    'lat': place_lat,
                    'lon': place_lon,
                    'distancia': distance,
                    'telefono': tags.get('phone', ''),
                    'categoria': categoria
                })
            
            places.sort(key=lambda x: x['distancia'] if x['distancia'] else 9999)
            return places
            
        except Exception as e:
            print(f"Error en búsqueda rápida: {e}")
            return []