import os


class Config:
    # Leer TODAS las claves desde variables de entorno
    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    
    # MySQL Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'gestion_nutricion')
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # YouTube API
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
    
    # Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
    
    # OpenStreetMap
    OSM_USER_AGENT = 'NutriApp/1.0 (contacto@nutriapp.com)'
    OSM_TIMEOUT = 10