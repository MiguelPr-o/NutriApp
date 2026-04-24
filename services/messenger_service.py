import requests
from flask import current_app

class MessengerService:
    
    @staticmethod
    def send_text_message(recipient_id, message_text):
        """
        Envía un mensaje de texto a un usuario de Messenger
        """
        access_token = current_app.config['MESSENGER_PAGE_ACCESS_TOKEN']
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={access_token}"
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "messaging_type": "RESPONSE"
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return None
    
    @staticmethod
    def send_typing_action(recipient_id, action="typing_on"):
        """
        Envía acción de "escribiendo..." a Messenger
        """
        access_token = current_app.config['MESSENGER_PAGE_ACCESS_TOKEN']
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={access_token}"
        
        payload = {
            "recipient": {"id": recipient_id},
            "sender_action": action
        }
        
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error enviando acción: {e}")
    
    @staticmethod
    def send_quick_replies(recipient_id, text, replies):
        """
        Envía mensaje con respuestas rápidas
        """
        access_token = current_app.config['MESSENGER_PAGE_ACCESS_TOKEN']
        url = f"https://graph.facebook.com/v18.0/me/messages?access_token={access_token}"
        
        quick_replies = []
        for reply in replies:
            quick_replies.append({
                "content_type": "text",
                "title": reply['title'],
                "payload": reply['payload']
            })
        
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "text": text,
                "quick_replies": quick_replies
            },
            "messaging_type": "RESPONSE"
        }
        
        try:
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error enviando quick replies: {e}")
            return None