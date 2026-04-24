import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime, timedelta
from services.db_service import DatabaseService

class StatisticsService:
    
    @staticmethod
    def get_patient_evolution(paciente_id):
        """Obtiene la evolución del paciente: peso, IMC, etc."""
        consultas = DatabaseService.get_consultas_by_paciente(paciente_id)
        
        if not consultas:
            return None
        
        # Preparar datos
        fechas = []
        pesos = []
        imcs = []
        estaturas = []
        
        for consulta in consultas:
            if consulta.diagnostico:
                fechas.append(consulta.fechaConsulta)
                pesos.append(consulta.diagnostico.peso)
                imcs.append(consulta.diagnostico.imc)
                estaturas.append(consulta.diagnostico.estatura)
        
        return {
            'fechas': fechas,
            'pesos': pesos,
            'imcs': imcs,
            'estaturas': estaturas
        }
    
    @staticmethod
    def create_weight_chart(data):
        """Crea gráfico de evolución de peso"""
        if not data or not data['fechas']:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data['fechas'],
            y=data['pesos'],
            mode='lines+markers',
            name='Peso (kg)',
            line=dict(color='#28a745', width=3),
            marker=dict(size=8, color='#28a745')
        ))
        
        fig.update_layout(
            title='Evolución del Peso',
            xaxis_title='Fecha',
            yaxis_title='Peso (kg)',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    @staticmethod
    def create_imc_chart(data):
        """Crea gráfico de evolución del IMC"""
        if not data or not data['fechas']:
            return None
        
        # Rangos de IMC para referencia
        imc_ranges = [
            {'y': 18.5, 'name': 'Bajo peso', 'color': '#ffc107'},
            {'y': 25, 'name': 'Normal', 'color': '#28a745'},
            {'y': 30, 'name': 'Sobrepeso', 'color': '#fd7e14'},
            {'y': 40, 'name': 'Obesidad', 'color': '#dc3545'}
        ]
        
        fig = go.Figure()
        
        # Agregar área de referencia
        fig.add_hrect(y0=0, y1=18.5, fillcolor="#ffc107", opacity=0.2, line_width=0)
        fig.add_hrect(y0=18.5, y1=25, fillcolor="#28a745", opacity=0.2, line_width=0)
        fig.add_hrect(y0=25, y1=30, fillcolor="#fd7e14", opacity=0.2, line_width=0)
        fig.add_hrect(y0=30, y1=40, fillcolor="#dc3545", opacity=0.2, line_width=0)
        
        fig.add_trace(go.Scatter(
            x=data['fechas'],
            y=data['imcs'],
            mode='lines+markers',
            name='IMC',
            line=dict(color='#007bff', width=3),
            marker=dict(size=8, color='#007bff')
        ))
        
        fig.update_layout(
            title='Evolución del IMC',
            xaxis_title='Fecha',
            yaxis_title='IMC',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    @staticmethod
    def get_nutritionist_statistics(nutriologo_id):
        """Obtiene estadísticas generales para un nutriólogo"""
        pacientes = DatabaseService.get_pacientes(nutriologo_id)
        total_pacientes = len(pacientes)
        
        # Estadísticas de género
        generos = {'M': 0, 'F': 0, 'O': 0}
        edades = []
        consultas_totales = 0
        
        for paciente in pacientes:
            generos[paciente.sexo] = generos.get(paciente.sexo, 0) + 1
            if paciente.edad:
                edades.append(paciente.edad)
            
            consultas = DatabaseService.get_consultas_by_paciente(paciente.idPaciente)
            consultas_totales += len(consultas)
        
        # Estadísticas de edad
        edad_promedio = sum(edades) / len(edades) if edades else 0
        edad_min = min(edades) if edades else 0
        edad_max = max(edades) if edades else 0
        
        # Distribución por edad
        rangos_edad = {'0-18': 0, '19-30': 0, '31-50': 0, '51+': 0}
        for edad in edades:
            if edad <= 18:
                rangos_edad['0-18'] += 1
            elif edad <= 30:
                rangos_edad['19-30'] += 1
            elif edad <= 50:
                rangos_edad['31-50'] += 1
            else:
                rangos_edad['51+'] += 1
        
        return {
            'total_pacientes': total_pacientes,
            'consultas_totales': consultas_totales,
            'generos': generos,
            'edad_promedio': round(edad_promedio, 1),
            'edad_min': edad_min,
            'edad_max': edad_max,
            'rangos_edad': rangos_edad
        }
    
    @staticmethod
    def create_gender_chart(generos):
        """Crea gráfico de distribución por género"""
        labels = {'M': 'Masculino', 'F': 'Femenino', 'O': 'Otro'}
        
        fig = go.Figure(data=[go.Pie(
            labels=[labels[k] for k in generos.keys() if generos[k] > 0],
            values=[v for v in generos.values() if v > 0],
            hole=0.3,
            marker=dict(colors=['#007bff', '#dc3545', '#6c757d'])
        )])
        
        fig.update_layout(
            title='Distribución por Género',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    @staticmethod
    def create_age_chart(rangos_edad):
        """Crea gráfico de distribución por edad"""
        fig = go.Figure(data=[go.Bar(
            x=list(rangos_edad.keys()),
            y=list(rangos_edad.values()),
            marker_color='#28a745'
        )])
        
        fig.update_layout(
            title='Distribución por Edad',
            xaxis_title='Rango de Edad',
            yaxis_title='Número de Pacientes',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    @staticmethod
    def get_recent_consultations(nutriologo_id, days=30):
        """Obtiene número de consultas por día en los últimos N días"""
        from datetime import date, timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        pacientes = DatabaseService.get_pacientes(nutriologo_id)
        
        # Diccionario para contar consultas por fecha
        consultas_por_dia = {start_date + timedelta(days=i): 0 for i in range(days + 1)}
        
        for paciente in pacientes:
            consultas = DatabaseService.get_consultas_by_paciente(paciente.idPaciente)
            for consulta in consultas:
                if start_date <= consulta.fechaConsulta <= end_date:
                    consultas_por_dia[consulta.fechaConsulta] += 1
        
        return consultas_por_dia
    
    @staticmethod
    def create_consultations_chart(consultas_por_dia):
        """Crea gráfico de consultas por día"""
        fechas = list(consultas_por_dia.keys())
        cantidad = list(consultas_por_dia.values())
        
        fig = go.Figure(data=[go.Scatter(
            x=fechas,
            y=cantidad,
            mode='lines+markers',
            name='Consultas',
            fill='tozeroy',
            line=dict(color='#007bff', width=2),
            marker=dict(size=6, color='#007bff')
        )])
        
        fig.update_layout(
            title='Consultas en los Últimos 30 Días',
            xaxis_title='Fecha',
            yaxis_title='Número de Consultas',
            template='plotly_white'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)