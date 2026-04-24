# 🥗 Sistema de Gestión de Nutrición

Plataforma web para nutriólogos y pacientes con seguimiento de consultas, planes alimenticios, mapas de lugares saludables y videos educativos.

## 📋 Tabla de Contenidos
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Requisitos Previos](#requisitos-previos)
- [Instalación Local](#instalación-local)
- [Ejecutar con Docker](#ejecutar-con-docker)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [APIs Integradas](#apis-integradas)
- [Credenciales de Prueba](#credenciales-de-prueba)
- [Capturas de Pantalla](#capturas-de-pantalla)
- [Autor](#autor)

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
| Docker | - | Contenerización |

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
- Docker Desktop (opcional)

## 💻 Instalación Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/nutriapp.git
cd nutriapp
