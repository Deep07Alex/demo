import requests
import logging
from django.conf import settings


logger = logging.getLogger(__name__)



class EnviaAPI:
    """
    Minimal Envia client that matches the parts:
    - quote shipping
    - create shipment
    """


    def __init__(self):
        self.base_url = settings.ENVIA_BASE_URL.rstrip("/")
        self.token = settings.ENVIA_API_TOKEN
        if not self.token:
            raise RuntimeError("ENVIA_API_TOKEN is not configured")


    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }


    def quote(self, origin_zip, dest_zip, weight, length, width, height):
        url = f"{self.base_url}/quote"
        payload = {
            "origin": {"zip": origin_zip, "country": "IN"},
            "destination": {"zip": dest_zip, "country": "IN"},
            "packages": [{
                "weight": weight,
                "length": length,
                "width": width,
                "height": height,
            }],
        }
        resp = requests.post(url, json=payload, headers=self.get_headers(), timeout=15)
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            logger.error("ENVIA QUOTE ERROR %s: %s", resp.status_code, resp.text)
            raise
        return resp.json()



    def create_shipment(self, order, items, carrier_id):
        """
        Create a shipment in Envia.


        'carrier_id' should come from the quote selection.
        This is a skeleton; you will need to align with Envia's create-shipment payload.
        """
        url = f"{self.base_url}/shipments"


        # Build items list
        packages = []
        for item in items:
            packages.append(
                {
                    "description": item.title[:100],
                    "quantity": int(item.quantity),
                    "weight": 0.5,  # 500g per book; refine later
                    "length": 20,
                    "width": 15,
                    "height": 4,
                    "price": float(item.price),
                }
            )


        payload = {
            "carrier": carrier_id,
            "service": None,  # can be chosen from quote if available
            "type": 1,        # 1 = standard package in Envia docs
            "label": 1,
            "origin": {
                "name": "Family BookStore",
                "company": "Family BookStore",
                "email": order.verified_email or order.email,
                "phone": order.phone_number,
                "street": order.address,
                "city": order.city,
                "state": order.state,
                "country": "IN",
                "zip": settings.PICKUP_PINCODE,
            },
            "destination": {
                "name": order.full_name,
                "company": "",
                "email": order.verified_email or order.email,
                "phone": order.phone_number,
                "street": order.address,
                "city": order.city,
                "state": order.state,
                "country": "IN",
                "zip": order.pin_code,
            },
            "packages": packages,
        }


        resp = requests.post(url, json=payload, headers=self.get_headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        logger.info("Envia shipment created: %s", data)
        return data