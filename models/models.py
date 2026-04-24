from datetime import datetime

class Nutriologo:
    def __init__(self):
        self.idNutriologo = None
        self.nombre = None
        self.apP = None
        self.apM = None
        self.correoElec = None
        self.telefono = None
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apP} {self.apM or ''}".strip()

class Paciente:
    def __init__(self):
        self.idPaciente = None
        self.nombre = None
        self.apP = None
        self.apM = None
        self.sexo = None
        self.edadNac = None
        self.telefono = None
        self.nutriologo_id = None
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apP} {self.apM or ''}".strip()
    
    @property
    def edad(self):
        if self.edadNac:
            hoy = datetime.now().date()
            return hoy.year - self.edadNac.year - ((hoy.month, hoy.day) < (self.edadNac.month, self.edadNac.day))
        return None

class Consulta:
    def __init__(self):
        self.idConsulta = None
        self.fechaConsulta = None
        self.horaE = None
        self.horaS = None
        self.descripcion = None
        self.paciente_id = None
        self.diagnostico = None  # Se asignará después

class Diagnostico:
    def __init__(self):
        self.idDiagnostico = None
        self.peso = None
        self.estatura = None
        self.imc = None
        self.descripcion = None
        self.consulta_id = None
        self.nutriologo_id = None

class PlanAlimenticio:
    def __init__(self):
        self.idPlanA = None
        self.descripcion = None
        self.kcalD = None
        self.fechaI = None
        self.fechaF = None
        self.consulta_id = None
    
    @property
    def activo(self):
        if self.fechaI and self.fechaF:
            hoy = datetime.now().date()
            return self.fechaI <= hoy <= self.fechaF
        return False

class Usuario:
    def __init__(self):
        self.id = None
        self.email = None
        self.password_hash = None
        self.rol = None
        self.nutriologo_id = None
        self.paciente_id = None
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
class Pago:
    def __init__(self):
        self.id = None
        self.usuario_id = None
        self.paciente_id = None
        self.monto = None
        self.moneda = 'MXN'
        self.concepto = None
        self.estado = None  # 'pending', 'completed', 'failed', 'refunded'
        self.paypal_order_id = None
        self.paypal_payer_id = None
        self.fecha_creacion = None
        self.fecha_completado = None
    
    @property
    def monto_formateado(self):
        return f"${self.monto:.2f} {self.moneda}"