import stripe
from flask import current_app, session, url_for

class PaymentService:
    
    @staticmethod
    def create_checkout_session(plan_nombre, plan_precio, plan_descripcion):
        """
        Crea una sesión de checkout de Stripe para un plan nutricional
        """
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        try:
            # Precio en centavos (Stripe trabaja con la moneda base)
            # Ejemplo: $99.99 MXN = 9999 centavos
            precio_centavos = int(plan_precio * 100)
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'mxn',
                        'product_data': {
                            'name': plan_nombre,
                            'description': plan_descripcion,
                        },
                        'unit_amount': precio_centavos,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=url_for('payment.success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=url_for('payment.cancel', _external=True),
                metadata={
                    'plan_nombre': plan_nombre,
                    'usuario_id': session.get('user_id', '')
                }
            )
            return checkout_session
        except Exception as e:
            print(f"Error creando sesión de checkout: {e}")
            return None
    
    @staticmethod
    def get_payment_intent(session_id):
        """
        Obtiene los detalles de un pago completado
        """
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            payment_intent = stripe.PaymentIntent.retrieve(checkout_session.payment_intent)
            return payment_intent
        except Exception as e:
            print(f"Error obteniendo payment intent: {e}")
            return None