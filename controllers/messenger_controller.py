from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, current_app
from services.messenger_service import MessengerService
from services.db_service import DatabaseService
import json
import hashlib
import hmac

messenger_bp = Blueprint('messenger', __name__, url_prefix='/messenger')

VERIFY_TOKEN = "nutriapp_verify_123"  # Mismo que configuraste en Facebook

def verify_signature(payload, signature):
    """
    Verifica que la petición viene de Facebook
    """
    if not signature:
        return False
    
    expected_signature = hmac.new(
        bytes(current_app.config['MESSENGER_APP_SECRET'], 'utf-8'),
        msg=payload,
        digestmod=hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(f"sha1={expected_signature}", signature)

@messenger_bp.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Verificación del webhook (GET)
    """
    verify_token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if verify_token == VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

@messenger_bp.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Recibe mensajes de Messenger (POST)
    """
    # Verificar firma (opcional pero recomendado)
    signature = request.headers.get('X-Hub-Signature')
    payload = request.get_data()
    
    # if not verify_signature(payload, signature):
    #     return "Invalid signature", 403
    
    data = request.get_json()
    
    for entry in data.get('entry', []):
        for messaging_event in entry.get('messaging', []):
            sender_id = messaging_event.get('sender', {}).get('id')
            
            # Procesar mensaje de texto
            if messaging_event.get('message'):
                message_text = messaging_event['message'].get('text', '')
                
                if message_text:
                    # Buscar paciente por PSID
                    paciente = DatabaseService.get_paciente_by_psid(sender_id)
                    
                    if paciente:
                        # Aquí puedes guardar el mensaje en tu base de datos
                        print(f"Mensaje de {paciente.nombre}: {message_text}")
                        
                        # Respuesta automática (puedes personalizarla)
                        respuesta = procesar_mensaje(message_text, paciente)
                        MessengerService.send_text_message(sender_id, respuesta)
                    
                    else:
                        # Usuario no registrado, mensaje de bienvenida
                        MessengerService.send_text_message(
                            sender_id, 
                            "¡Hola! Soy el asistente de NutriApp. Por favor, contacta a tu nutriólogo para registrarte."
                        )
            
            # Procesar postback (respuestas rápidas)
            elif messaging_event.get('postback'):
                payload = messaging_event['postback'].get('payload', '')
                # Aquí manejas respuestas de botones
                pass
    
    return "OK", 200

def procesar_mensaje(mensaje, paciente):
    """
    Procesa el mensaje y genera una respuesta
    """
    mensaje = mensaje.lower().strip()
    
    # Respuestas automáticas según palabras clave
    if "hola" in mensaje or "buenas" in mensaje:
        return f"¡Hola {paciente.nombre}! ¿En qué puedo ayudarte?"
    
    elif "cita" in mensaje or "consulta" in mensaje:
        return "Puedes agendar una consulta directamente con tu nutriólogo. ¿Te ayudo a solicitar una?"
    
    elif "peso" in mensaje or "imc" in mensaje:
        return f"Tu último registro de peso fue de {paciente.ultimo_peso} kg. ¿Quieres registrar uno nuevo?"
    
    elif "plan" in mensaje or "dieta" in mensaje:
        return "Tu plan alimenticio actual está disponible en la aplicación web. ¿Necesitas ayuda para acceder?"
    
    elif "gracias" in mensaje:
        return "¡De nada! Estoy aquí para ayudarte."
    
    else:
        return "Gracias por tu mensaje. Tu nutriólogo recibirá la notificación y te responderá pronto."

@messenger_bp.route('/chat')
def chat():
    """
    Página de chat para el nutriólogo (simulada)
    """
    if 'user_id' not in session or session.get('user_rol') != 'nutriologo':
        flash('No autorizado', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('messenger/chat.html')

@messenger_bp.route('/api/send', methods=['POST'])
def api_send_message():
    """
    API para enviar mensaje desde la app
    """
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.get_json()
    recipient_psid = data.get('psid')
    message = data.get('message')
    
    if not recipient_psid or not message:
        return jsonify({'error': 'Faltan datos'}), 400
    
    result = MessengerService.send_text_message(recipient_psid, message)
    
    if result:
        return jsonify({'success': True, 'result': result})
    else:
        return jsonify({'error': 'Error al enviar mensaje'}), 500