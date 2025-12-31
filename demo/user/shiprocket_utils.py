# user/shiprocket_utils.py
import requests
import json
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

class ShiprocketAPI:
    def __init__(self):
        self.email = settings.SHIPROCKET_EMAIL
        self.password = settings.SHIPROCKET_PASSWORD
        self.channel_id = settings.SHIPROCKET_CHANNEL_ID
        self.base_url = "https://apiv2.shiprocket.in/v1/external"
        self.token = None
        self.login()

    def login(self):
        """Authenticate with Shiprocket and get access token"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {
                "email": self.email,
                "password": self.password
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200:
                    self.token = data['token']
                    logger.info("Shiprocket login successful")
                    return True
                else:
                    logger.error(f"Shiprocket login failed: {data}")
                    return False
            else:
                logger.error(f"Shiprocket login HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Shiprocket login exception: {str(e)}")
            return False

    def get_headers(self):
        """Get authorization headers"""
        if not self.token:
            self.login()
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def calculate_shipping_rates(self, pickup_pincode, delivery_pincode, weight, length, width, height):
        """Calculate shipping rates between two pincodes"""
        try:
            url = f"{self.base_url}/courier/serviceability"
            
            payload = {
                "pickup_postcode": pickup_pincode,
                "delivery_postcode": delivery_pincode,
                "weight": weight,
                "length": length,
                "breadth": width,
                "height": height,
                "cod": 0  # 0 for prepaid, 1 for COD
            }
            
            headers = self.get_headers()
            response = requests.get(url, params=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200:
                    return True, data.get('data', {}).get('available_courier_companies', [])
                else:
                    return False, data.get('message', 'No rates available')
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Shipping rates error: {str(e)}")
            return False, str(e)

    def create_order(self, order, items):
        """Create order in Shiprocket"""
        try:
            url = f"{self.base_url}/orders/create/adhoc"
            
            # Prepare order items
            order_items = []
            for item in items:
                order_items.append({
                    "name": item.title,
                    "sku": f"BOOK-{item.item_id}",
                    "units": item.quantity,
                    "selling_price": float(item.price),
                    "discount": 0,
                    "tax": 0,
                    "hsn": "4901"  # HSN code for books
                })

            # Calculate package dimensions (standard book sizes)
            total_weight = 0.5 * len(items)  # Approximate weight calculation
            package_length = 20
            package_breadth = 15
            package_height = 5 * len(items) if len(items) > 1 else 2

            payload = {
                "order_id": str(order.id),
                "order_date": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "pickup_location": "Primary",  # You'll need to configure this in Shiprocket
                "channel_id": self.channel_id,
                "comment": f"Book order from Family BookStore",
                "billing_customer_name": order.full_name,
                "billing_last_name": "",
                "billing_address": order.address,
                "billing_address_2": "",
                "billing_city": order.city,
                "billing_pincode": order.pin_code,
                "billing_state": order.state,
                "billing_country": "India",
                "billing_email": order.email,
                "billing_phone": order.phone_number,
                "shipping_is_billing": True,
                "order_items": order_items,
                "payment_method": "prepaid" if order.payment_method != "cod" else "cod",
                "shipping_charges": float(order.shipping),
                "giftwrap_charges": 0,
                "transaction_charges": 0,
                "total_discount": float(order.discount),
                "sub_total": float(order.subtotal),
                "length": package_length,
                "breadth": package_breadth,
                "height": package_height,
                "weight": total_weight
            }

            headers = self.get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 200 or data.get('status') == 201:
                    shiprocket_order_id = data.get('order_id')
                    logger.info(f"Shiprocket order created: {shiprocket_order_id}")
                    return True, shiprocket_order_id
                else:
                    logger.error(f"Shiprocket order creation failed: {data}")
                    return False, data.get('message', 'Order creation failed')
            else:
                logger.error(f"Shiprocket order HTTP error: {response.status_code}")
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Shiprocket order creation exception: {str(e)}")
            return False, str(e)

    def track_order(self, shiprocket_order_id):
        """Track Shiprocket order"""
        try:
            url = f"{self.base_url}/courier/track"
            payload = {"order_id": shiprocket_order_id}
            
            headers = self.get_headers()
            response = requests.get(url, params=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Track order error: {str(e)}")
            return False, str(e)

    def cancel_order(self, shiprocket_order_id):
        """Cancel Shiprocket order"""
        try:
            url = f"{self.base_url}/orders/cancel"
            payload = {"order_id": shiprocket_order_id}
            
            headers = self.get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Cancel order error: {str(e)}")
            return False, str(e)

    def generate_awb(self, shiprocket_order_id):
        """Generate AWB for order"""
        try:
            url = f"{self.base_url}/courier/assign/awb"
            payload = {"order_id": shiprocket_order_id}
            
            headers = self.get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Generate AWB error: {str(e)}")
            return False, str(e)

    def get_shipping_label(self, shiprocket_order_id):
        """Get shipping label URL"""
        try:
            url = f"{self.base_url}/orders/print/label"
            payload = {"order_id": [shiprocket_order_id]}
            
            headers = self.get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Get label error: {str(e)}")
            return False, str(e)