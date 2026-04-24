from flask import Blueprint, render_template, request, jsonify, session, current_app, redirect, url_for
from services.db_service import DatabaseService
from services.paypal_service import PayPalService
from models.models import Pago
import json
from datetime import datetime

paypal_bp = Blueprint('paypal', __name__, url_prefix='/paypal')

@paypal_bp.route('/checkout')
def checkout():
    """Página de checkout para realizar un pago"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Obtener parámetros (pueden venir de la página anterior)
    monto = request.args.get('monto', 99.99, type=float)
    concepto = request.args.get('concepto', 'Consulta de nutrición')
    
    return render_template('paypal/checkout.html', 
                         paypal_client_id=current_app.config['PAYPAL_CLIENT_ID'],
                         monto=monto,
                         concepto=concepto,
                         moneda='MXN')

@paypal_bp.route('/api/create-order', methods=['POST'])
def api_create_order():
    """API endpoint para crear orden de pago"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    monto = data.get('monto', 99.99)
    concepto = data.get('concepto', 'Pago en NutriApp')
    
    # Crear orden en PayPal
    order = PayPalService.create_order(monto, 'MXN', concepto)
    
    if order and 'id' in order:
        # Guardar en base de datos local (pendiente)
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO pagos (usuario_id, monto, moneda, concepto, estado, paypal_order_id, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], monto, 'MXN', concepto, 'pending', order['id'], datetime.now()))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'order_id': order['id'],
            'paypal_order': order
        })
    else:
        return jsonify({'error': 'No se pudo crear la orden'}), 500

@paypal_bp.route('/api/capture-order', methods=['POST'])
def api_capture_order():
    """API endpoint para capturar pago después de aprobación"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({'error': 'Order ID requerido'}), 400
    
    # Capturar pago en PayPal
    captured = PayPalService.capture_order(order_id)
    
    if captured and captured.get('status') == 'COMPLETED':
        # Actualizar base de datos local
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE pagos 
            SET estado = 'completed', fecha_completado = %s
            WHERE paypal_order_id = %s
        """, (datetime.now(), order_id))
        mysql.connection.commit()
        
        # Obtener ID del pago
        cursor.execute("SELECT id FROM pagos WHERE paypal_order_id = %s", (order_id,))
        pago_id = cursor.fetchone()
        cursor.close()
        
        return jsonify({
            'success': True,
            'status': 'COMPLETED',
            'pago_id': pago_id['id'] if pago_id else None,
            'details': captured
        })
    else:
        return jsonify({'error': 'No se pudo capturar el pago'}), 500

@paypal_bp.route('/confirm')
def confirm():
    """Página de confirmación de pago exitoso"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    token = request.args.get('token')
    payer_id = request.args.get('PayerID')
    
    return render_template('paypal/confirm.html', token=token, payer_id=payer_id)

@paypal_bp.route('/cancel')
def cancel():
    """Página de cancelación de pago"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('paypal/cancel.html')

@paypal_bp.route('/historial')
def historial():
    """Historial de pagos del usuario"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT * FROM pagos 
        WHERE usuario_id = %s 
        ORDER BY fecha_creacion DESC
    """, (session['user_id'],))
    pagos_data = cursor.fetchall()
    cursor.close()
    
    return render_template('paypal/historial.html', pagos=pagos_data)

# ==================== WEBHOOKS (para confirmaciones asíncronas) ====================

@paypal_bp.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para recibir webhooks de PayPal"""
    # Verificar firma del webhook (importante para seguridad)
    webhook_id = current_app.config.get('PAYPAL_WEBHOOK_ID', '')
    
    # Obtener headers y body
    headers = request.headers
    body = request.get_data(as_text=True)
    
    # Aquí deberías verificar la firma del webhook
    # Por simplicidad, omitimos la verificación en este ejemplo
    
    event_data = request.get_json()
    event_type = event_data.get('event_type')
    
    print(f"Webhook recibido: {event_type}")
    
    # Procesar según tipo de evento
    if event_type == 'PAYMENT.CAPTURE.COMPLETED':
        resource = event_data.get('resource', {})
        order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
        
        # Actualizar estado del pago
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE pagos 
            SET estado = 'completed', fecha_completado = %s
            WHERE paypal_order_id = %s
        """, (datetime.now(), order_id))
        mysql.connection.commit()
        cursor.close()
        
        print(f"Pago completado para orden: {order_id}")
    
    elif event_type == 'PAYMENT.CAPTURE.DENIED':
        # Manejar pago denegado
        resource = event_data.get('resource', {})
        order_id = resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id')
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE pagos SET estado = 'failed' WHERE paypal_order_id = %s
        """, (order_id,))
        mysql.connection.commit()
        cursor.close()
    
    # Siempre responder 200 OK a PayPal
    return jsonify({'received': True}), 200