# 🥗 Sistema de Gestión de Nutrición

Plataforma web para nutriólogos y pacientes con seguimiento de consultas, planes alimenticios, mapas de lugares saludables y videos educativos.

## 🚀 Características

### Para Nutriólogos
- ✅ Registro y gestión de pacientes
- ✅ Creación de consultas y diagnósticos
- ✅ Asignación de planes alimenticios personalizados
- ✅ Visualización de estadísticas y gráficos de evolución
- ✅ Exportación de reportes a Excel
- ✅ Búsqueda de pacientes por nombre

### Para Pacientes
- ✅ Visualización de su historial de consultas
- ✅ Seguimiento de evolución de peso e IMC
- ✅ Acceso a planes alimenticios activos
- ✅ Exportación de su historial a Excel

### Funcionalidades Generales
- 🗺️ Mapas interactivos con OpenStreetMap
- 🎬 Videos educativos de nutrición (YouTube API)
- 📊 Gráficos interactivos de evolución (Plotly)
- 🛒 Tienda integrada con Stripe (pagos)

## 🛠️ Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.10 | Backend |
| Flask | 2.3 | Framework web |
| MySQL | 8.0 | Base de datos |
| SQLite | - | Base de datos para Docker |
| Bootstrap | 5.1 | Frontend |
| Leaflet.js | 1.9 | Mapas |
| Plotly | 5.18 | Gráficos |

## 🔌 APIs Integradas

| API | Función |
|-----|---------|
| YouTube Data API v3 | Videos educativos de nutrición |
| OpenStreetMap + Nominatim | Mapas y geolocalización |
| Overpass API | Búsqueda de lugares cercanos |
| Stripe API | Procesamiento de pagos |

## 📋 Requisitos Previos

- Python 3.10 o superior
- MySQL 8.0 (para desarrollo local)

## 📁 Estructura del Proyecto

nutriapp/
│
├── app.py                    # Punto de entrada
├── config.py                 # Configuración
├── requirements.txt          # Dependencias
├── Dockerfile                # Configuración Docker
├── docker-compose.yml        # Orquestación
│
├── controllers/              # Controladores (rutas)
│   ├── auth_controller.py
│   ├── paciente_controller.py
│   ├── consulta_controller.py
│   ├── plan_controller.py
│   ├── youtube_controller.py
│   ├── osm_controller.py
│   ├── statistics_controller.py
│   ├── report_controller.py
│   └── payment_controller.py
│
├── services/                 # Servicios (lógica)
│   ├── db_service.py
│   ├── youtube_service.py
│   ├── osm_service.py
│   ├── statistics_service.py
│   ├── report_service.py
│   └── payment_service.py
│
├── models/                   # Modelos de datos
│   └── models.py
│
├── templates/                # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── menu.html
│   ├── pacientes/
│   ├── consultas/
│   ├── planes/
│   ├── youtube/
│   ├── osm/
│   ├── statistics/
│   └── report/
│
└── static/                   # Archivos estáticos
