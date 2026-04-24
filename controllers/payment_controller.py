from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from services.payment_service import PaymentService
from services.db_service import DatabaseService
from datetime import datetime

payment_bp = Blueprint('payment', __name__, url_prefix='/pagos')

# Planes disponibles
PLANES_NUTRICION = [
    {
        'id': 'plan_basico',
        'nombre': 'Plan Nutricional Básico',
        'precio': 299.00,
        'descripcion': 'Plan alimenticio personalizado + 1 consulta de seguimiento',
        'icono': 'bi-star'
    },
    {
        'id': 'plan_premium',
        'nombre': 'Plan Nutricional Premium',
        'precio': 599.00,
        'descripcion': 'Plan personalizado + 3 consultas + seguimiento mensual',
        'icono': 'bi-gem'
    },
    {
        'id': 'plan_recetario',
        'nombre': 'Recetario Digital',
        'precio': 149.00,
        'descripcion': '50+ recetas saludables descargables',
        'icono': 'bi-book'
    }
]

@payment_bp.route('/')
def index():
    """Página principal de pagos"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('payment/index.html', planes=PLANES_NUTRICION)

@payment_bp.route('/checkout/<plan_id>')
def checkout(plan_id):
    """Página de checkout para un plan específico"""
    if 'user_id' not in session:
        flash('Debes iniciar sesión para realizar una compra', 'warning')
        return redirect(url_for('auth.login'))
    
    # Buscar el plan seleccionado
    plan = next((p for p in PLANES_NUTRICION if p['id'] == plan_id), None)
    if not plan:
        flash('Plan no encontrado', 'error')
        return redirect(url_for('payment.index'))
    
    # Obtener la clave pública de Stripe
    stripe_public_key = current_app.config.get('STRIPE_PUBLIC_KEY', '')
    
    return render_template('payment/checkout.html', 
                         plan=plan, 
                         stripe_public_key=stripe_public_key)

@payment_bp.route('/api/create-checkout-session', methods=['POST'])
def api_create_checkout_session():
    """API para crear sesión de checkout"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    plan_id = data.get('plan_id')
    
    plan = next((p for p in PLANES_NUTRICION if p['id'] == plan_id), None)
    if not plan:
        return jsonify({'error': 'Plan no encontrado'}), 404
    
    checkout_session = PaymentService.create_checkout_session(
        plan_nombre=plan['nombre'],
        plan_precio=plan['precio'],
        plan_descripcion=plan['descripcion']
    )
    
    if checkout_session:
        return jsonify({
            'success': True,
            'session_id': checkout_session.id,
            'url': checkout_session.url
        })
    else:
        return jsonify({'error': 'Error al crear sesión de pago'}), 500

@payment_bp.route('/success')
def success():
    """Página de éxito después del pago"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    session_id = request.args.get('session_id')
    
    if session_id:
        payment_intent = PaymentService.get_payment_intent(session_id)
        if payment_intent:
            # Aquí puedes guardar la transacción en tu base de datos
            # Por ejemplo, registrar que el usuario compró un plan
            flash('¡Pago completado exitosamente!', 'success')
        else:
            flash('Pago verificado correctamente', 'success')
    else:
        flash('Gracias por tu compra', 'success')
    
    return render_template('payment/success.html')

@payment_bp.route('/cancel')
def cancel():
    """Página de cancelación"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    flash('El pago fue cancelado', 'warning')
    return render_template('payment/cancel.html')

@payment_bp.route('/historial')
def historial():
    """Historial de pagos del usuario"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Obtener transacciones del usuario desde tu BD
    # Por ahora, mostramos mensaje
    return render_template('payment/historial.html')