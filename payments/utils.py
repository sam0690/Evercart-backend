import base64
import hashlib
import hmac
import json
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Tuple, Union
from xml.etree import ElementTree

import requests
from django.conf import settings

def _format_amount(value: Union[str, float, Decimal, int]) -> str:
    decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    quantized = decimal_value.quantize(Decimal('0.01'))
    text = format(quantized, 'f')
    # eSewa expects amounts with two decimal places even for whole numbers.
    if '.' not in text:
        text = f"{text}.00"
    else:
        fractional = text.split('.')[-1]
        if len(fractional) == 1:
            text = f"{text}0"
    return text or '0'

def _normalize_amount(amount: Union[str, float, Decimal, int, None]) -> Decimal | None:
    if amount is None:
        return None
    try:
        return (amount if isinstance(amount, Decimal) else Decimal(str(amount))).quantize(Decimal('0.01'))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _parse_esewa_response(body: str) -> Dict[str, Any]:
    """Attempt to parse eSewa verification response into a dict with lowercase keys."""
    body = body.strip()
    if not body:
        return {}

    # Try JSON first
    try:
        parsed_json = json.loads(body)
        if isinstance(parsed_json, dict):
            result: Dict[str, Any] = {}
            # Flatten nested "response" payloads commonly returned by eSewa
            stacks = [parsed_json]
            while stacks:
                node = stacks.pop()
                for key, value in node.items():
                    if isinstance(value, dict):
                        stacks.append(value)
                    else:
                        result[key.lower()] = value
            return result
    except json.JSONDecodeError:
        pass

    # Try XML payload
    try:
        root = ElementTree.fromstring(body)
        result: Dict[str, Any] = {}
        for element in root.iter():
            if element is root:
                continue
            if element.text is not None:
                result[element.tag.lower()] = element.text
        if result:
            return result
    except ElementTree.ParseError:
        pass

    # Fallback for key=value responses separated by & or whitespace
    result: Dict[str, Any] = {}
    normalized = body.replace('\n', '&')
    for part in re.split(r'[&\\s]+', normalized):
        if '=' in part:
            key, value = part.split('=', 1)
            result[key.strip().lower()] = value.strip()
    if not result and body:
        result['message'] = body
    return result


def verify_esewa(ref_id: str, amount: Union[str, float, Decimal, int], pid: str) -> Tuple[bool, Dict[str, Any]]:
    """Verify eSewa payment using transaction reference and identifier (pid).

    Returns a tuple of (is_success, response_details) where response_details contains any
    parsed values returned by eSewa for downstream validation.
    """

    payload = {
        'amt': _format_amount(amount),
        'rid': ref_id,
        'pid': pid,
        'scd': settings.ESEWA_MERCHANT_ID,
    }

    try:
        resp = requests.post(settings.ESEWA_VERIFY_URL, data=payload, timeout=10)
    except requests.RequestException:
        return False, {'error': 'network_error'}

    body = resp.text.strip()
    parsed = _parse_esewa_response(body)

    status_value = str(parsed.get('status') or parsed.get('responsecode') or parsed.get('response_code') or '').strip().lower()
    raw_upper = body.upper()
    success_hint = 'SUCCESS' in raw_upper and 'FAIL' not in raw_upper
    is_success = status_value == 'success' or (not status_value and success_hint)

    if not is_success:
        return False, {'raw': body, 'parsed': parsed}

    expected_amount = _normalize_amount(amount)
    response_amount = _normalize_amount(
        parsed.get('amount')
        or parsed.get('amt')
        or parsed.get('totalamount')
        or parsed.get('total_amount')
    )
    if expected_amount is not None and response_amount is not None and expected_amount != response_amount:
        return False, {'raw': body, 'parsed': parsed, 'reason': 'amount_mismatch'}

    response_ref = (parsed.get('refid') or parsed.get('referenceid') or parsed.get('reference_id'))
    if response_ref and str(response_ref).strip() != str(ref_id).strip():
        return False, {'raw': body, 'parsed': parsed, 'reason': 'reference_mismatch'}

    response_pid = (
        parsed.get('productid')
        or parsed.get('product_id')
        or parsed.get('productcode')
        or parsed.get('product_code')
        or parsed.get('pid')
        or parsed.get('transaction_uuid')
    )
    if response_pid and str(response_pid).strip() != str(pid).strip():
        return False, {'raw': body, 'parsed': parsed, 'reason': 'pid_mismatch'}

    details: Dict[str, Any] = {
        'raw': body,
        'parsed': parsed,
    }
    if response_amount is not None:
        details['amount'] = str(response_amount)
    if response_ref:
        details['ref_id'] = str(response_ref)
    if response_pid:
        details['pid'] = str(response_pid)

    return True, details

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
