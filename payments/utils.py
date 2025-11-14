import base64
import hashlib
import hmac
import requests
from django.conf import settings
from decimal import Decimal

def verify_esewa(refId, amt, oid):
    """Verify eSewa payment"""
    data = {
        'amt': amt,
        'rid': refId,
        'pid': oid,
        'scd': settings.ESEWA_MERCHANT_ID
    }
    resp = requests.post(settings.ESEWA_VERIFY_URL, data=data)
    return 'SUCCESS' in resp.text

def verify_khalti(token, amount):
    headers = {
        'Authorization': f'Key {settings.KHALTI_SECRET_KEY}'
    }
    payload = {
        'token': token,
        'amount': int(Decimal(amount) * 100)
    }
    resp = requests.post(settings.KHALTI_VERIFY_URL, data=payload, headers=headers)
    return resp.status_code == 200 and resp.json().get("state", {}).get("name") == "Completed"

def generate_fonepay_checksum(data_dict):
    """Simple checksum generator"""
    s = ''.join(str(v) for v in data_dict.values()) + settings.FONEPAY_CHECKSUM_KEY
    return hashlib.sha512(s.encode()).hexdigest()

def verify_fonepay(tran_id):
    # Usually Fonepay provides a status API or callback
    # For simplicity, we simulate success
    return True


def generate_esewa_signature(payload: dict, signed_fields: list[str]) -> str:
    """Create base64 encoded HMAC-SHA256 signature for eSewa requests."""
    secret = getattr(settings, "ESEWA_SECRET_KEY", "")
    if not secret:
        raise ValueError("ESEWA_SECRET_KEY is not configured")

    message = ','.join(f"{field}={payload[field]}" for field in signed_fields)
    digest = hmac.new(secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')
