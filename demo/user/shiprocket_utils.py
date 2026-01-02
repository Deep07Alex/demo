import requests
import json
import logging
import hmac
import hashlib
from django.conf import settings

logger = logging.getLogger(__name__)


class ShiprocketAPI:
    BASE_URL = "https://apiv2.shiprocket.in/v1/external"

    def __init__(self):
        self.email = settings.SHIPROCKET_EMAIL
        # use the setting you actually defined
        self.password = settings.SHIPROCKET_API_PASSWORD
        # optional: if you have a channel id in env, otherwise set None
        self.channel_id = getattr(settings, "SHIPROCKET_CHANNEL_ID", None)
        self.token = None
        self.authenticate()

    def authenticate(self):
        """Authenticate and get access token"""
        try:
            url = f"{self.BASE_URL}/auth/login"
            payload = {"email": self.email, "password": self.password}
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("token"):
                self.token = data["token"]
                logger.info("Shiprocket authentication successful")
                return True
            else:
                logger.error(f"Shiprocket auth failed: {data}")
                return False
        except Exception as e:
            logger.error(f"Shiprocket auth error: {str(e)}")
            return False

    def get_headers(self):
        """Get authorized headers"""
        if not self.token:
            self.authenticate()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def calculate_shipping_rates(
    self,
    pickup_pincode,
    delivery_pincode,
    weight,
    length,
    width,
    height,
    cod=0,
    ):
        """Calculate shipping rates between pincodes"""
        try:
            url = f"{self.BASE_URL}/courier/serviceability"
            params = {
                "pickup_postcode": pickup_pincode,
                "delivery_postcode": delivery_pincode,
                "weight": weight,
                "length": length,
                "breadth": width,
                "height": height,
                "cod": cod,
            }
            headers = self.get_headers()
            # CHANGED: use GET with params
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == 200:
                rates = data.get("data", {}).get("available_courier_companies", [])
                if rates:
                    rates.sort(
                        key=lambda x: (
                            x.get("rating", 0),
                            x.get("freight_charge", 9999),
                        )
                    )
                    logger.info(f"Found {len(rates)} shipping options")
                    return True, rates
                else:
                    logger.warning("No courier companies available")
                    return False, "No shipping options available"
            else:
                logger.error(f"Shiprocket API error: {data}")
                return False, data.get("message", "API error")
        except Exception as e:
            logger.error(f"Shipping calculation error: {str(e)}")
            return False, str(e)

    def create_order(self, order, items):
        """Create order in Shiprocket after payment success"""
        try:
            url = f"{self.BASE_URL}/orders/create/adhoc"

            order_items = []
            for item in items:
                order_items.append(
                    {
                        "name": item.title[:100],
                        "sku": f"FB-{item.item_type}-{item.item_id}",
                        "units": item.quantity,
                        "selling_price": float(item.price),
                        "discount": 0,
                        "tax": 0,
                        "hsn": "4901",
                    }
                )

            for item in items.filter(item_type="addon"):
                order_items.append(
                    {
                        "name": item.title[:100],
                        "sku": f"FB-ADDON-{item.title}",
                        "units": 1,
                        "selling_price": float(item.price),
                        "discount": 0,
                        "tax": 0,
                        "hsn": "9999",
                    }
                )

            total_items = sum(
                item.quantity for item in items if item.item_type != "addon"
            )
            total_weight = round(0.5 * total_items, 2)
            package_length = 20
            package_breadth = 15
            package_height = max(2, total_items * 2)

            payload = {
                "order_id": f"FB{order.id}",
                "order_date": order.created_at.strftime("%Y-%m-%d %H:%M"),
                # use the pickup name from Shiprocket (e.g. "Gopal")
                "pickup_location": settings.SHIPROCKET_PICKUP_LOCATION,
                "channel_id": str(self.channel_id) if self.channel_id else "",
                "billing_customer_name": order.full_name,
                "billing_last_name": "",
                "billing_address": order.address,
                "billing_address_2": "",
                "billing_city": order.city,
                "billing_pincode": order.pin_code,
                "billing_state": order.state,
                "billing_country": "India",
                "billing_email": order.verified_email or order.email,
                "billing_phone": order.phone_number,
                "shipping_is_billing": True,
                "order_items": order_items,
                "payment_method": "prepaid",
                "shipping_charges": float(order.shipping),
                "giftwrap_charges": 0,
                "transaction_charges": 0,
                "total_discount": float(order.discount),
                "sub_total": float(order.subtotal),
                "length": package_length,
                "breadth": package_breadth,
                "height": package_height,
                "weight": total_weight,
            }
            headers = self.get_headers()
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Shiprocket often returns order/shipment fields at top level (status = "NEW")
            if data.get("order_id") and data.get("shipment_id"):
                logger.info(f"Shiprocket order created: {data.get('order_id')}")
                return True, {
                    "order_id": data.get("order_id"),
                    "awb_code": data.get("awb_code") or "",
                    "courier_name": data.get("courier_name") or "",
                    "label_url": data.get("label_url"),
                }
            else:
                logger.error(f"Shiprocket order creation failed: {data}")
                return False, data.get("message", "Order creation failed")
        except Exception as e:
            logger.error(f"Shiprocket order creation error: {str(e)}")
            return False, str(e)

    @staticmethod
    def verify_webhook_signature(payload, signature):
        """Verify webhook signature using HMAC-SHA256"""
        try:
            secret = settings.SHIPROCKET_WEBHOOK_SECRET.encode("utf-8")
            computed_signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(computed_signature, signature)
        except Exception as e:
            logger.error(f"Webhook verification error: {str(e)}")
            return False
