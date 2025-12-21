import os
import requests
from django.conf import settings

def send_otp_to_user(phone_number, otp, delivery_method='sms'):
    try:
        # Clean number: remove spaces, ensure +91
        clean_phone = phone_number.replace(' ', '')
        if not clean_phone.startswith('+'):
            clean_phone = f"+91{clean_phone}"
            
        if delivery_method == 'whatsapp':
            return send_otp_via_whatsapp(clean_phone, otp)
        else:
            return send_otp_via_fast2sms(clean_phone, otp)
            
    except Exception as e:
        print(f"[OTP ERROR] {str(e)}")
        return False, str(e)


def send_otp_via_fast2sms(phone, otp):
    """
    Fast2SMS: 100 free transactional SMS/day for Indian numbers
    Route "q" = Quick Transactional (instant delivery)
    """
    try:
        # Remove +91 for Fast2SMS API (they expect 10-digit number)
        indian_number = phone.replace('+91', '')
        
        url = "https://www.fast2sms.com/dev/bulkV2   "
        headers = {
            'authorization': settings.FAST2SMS_API_KEY,
            'Content-Type': 'application/json'
        }
        
        message = f"Family BookStore: Your OTP is {otp}. Valid for 10 minutes. Don't share it."
        
        payload = {
            "route": "q",  # Quick Transactional
            "message": message,
            "language": "english",
            "numbers": indian_number,
        }
        
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        # Fast2SMS success response: {"return": true, "request_id": "..."}
        if result.get('return') is True:
            return True, result.get('request_id')
        else:
            error = result.get('message', 'Unknown Fast2SMS error')
            return False, error
            
    except Exception as e:
        return False, f"Fast2SMS API failed: {str(e)}"


def send_otp_via_whatsapp(phone, otp):
    """
    WhatsApp Cloud API: FREE, requires Meta Business verification
    Send OTP to any WhatsApp number worldwide
    """
    try:
        url = f"https://graph.facebook.com/v18.0/   {settings.WHATSAPP_PHONE_ID}/messages"
        
        headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,  # Must be in format: +919876543210
            "type": "text",
            "text": {
                "body": f"🏪 *Family BookStore OTP*\n\nYour code: *{otp}*\nValid for: 10 minutes\n\n⚠️ Do not share this code with anyone."
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        
        # Success: {"messages": [{"id": "wamid.XXXXX"}]}
        if 'messages' in result and len(result['messages']) > 0:
            return True, result['messages'][0].get('id')
        else:
            error = result.get('error', {}).get('message', 'WhatsApp API error')
            return False, error
            
    except Exception as e:
        return False, f"WhatsApp API failed: {str(e)}"