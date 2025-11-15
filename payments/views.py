import uuid
from decimal import Decimal

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from .models import Payment
from .utils import (
    generate_esewa_signature,
    generate_fonepay_checksum,
    verify_esewa,
    verify_fonepay,
    verify_khalti,
)

# ---------- INITIATE PAYMENT ----------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    method = request.data.get("method")
    order_id = request.data.get("order_id")
    order = Order.objects.filter(id=order_id, user=request.user).first()

    if not order:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.create(
        user=request.user,
        order=order,
        method=method,
        amount=order.total
    )

    if method == "esewa":
        transaction_uuid = str(uuid.uuid4())
        product_code = getattr(settings, "ESEWA_PRODUCT_CODE", settings.ESEWA_MERCHANT_ID)

        def _fmt(value: Decimal | str | float | int) -> str:
            decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
            quantized = decimal_value.quantize(Decimal("0.01"))
            sval = format(quantized, "f")
            if "." not in sval:
                sval = f"{sval}.00"
            else:
                fractional = sval.split(".")[-1]
                if len(fractional) == 1:
                    sval = f"{sval}0"
            return sval or "0"

        total_amount_decimal = (
            order.total if isinstance(order.total, Decimal) else Decimal(str(order.total))
        ).quantize(Decimal("0.01"))
        tax_amount_decimal = Decimal("0")
        base_amount_decimal = (total_amount_decimal - tax_amount_decimal).quantize(Decimal("0.01"))

        success_callback = request.build_absolute_uri(
            reverse("esewa_verify") + f"?oid={order.id}&uuid={transaction_uuid}"
        )
        failure_callback = request.build_absolute_uri(
            reverse("esewa_fail") + f"?oid={order.id}&uuid={transaction_uuid}"
        )

        payload = {
            "amount": _fmt(base_amount_decimal),
            "tax_amount": _fmt(tax_amount_decimal),
            "total_amount": _fmt(total_amount_decimal),
            "transaction_uuid": transaction_uuid,
            "product_code": product_code,
            "product_service_charge": "0",
            "product_delivery_charge": "0",
            "success_url": success_callback,
            "failure_url": failure_callback,
            "merchant_code": settings.ESEWA_MERCHANT_ID,
            "signed_field_names": "amount,tax_amount,total_amount,transaction_uuid,product_code",
        }

        signed_fields = payload["signed_field_names"].split(",")
        signature_message = ",".join(f"{field}={payload[field]}" for field in signed_fields)
        payload["signature"] = generate_esewa_signature(payload, signed_fields)

        payment.transaction_uuid = transaction_uuid
        payment.product_code = product_code
        payment.save(update_fields=["transaction_uuid", "product_code"])

        response_payload = {"url": settings.ESEWA_PAYMENT_URL, "params": payload}
        if getattr(settings, "DEBUG", False):
            response_payload["debug"] = {"signature_message": signature_message}

        return Response(response_payload)

    elif method == "khalti":
        # Frontend uses Khalti widget directly, backend only verifies
        return Response({"khalti_key": "test_public_key_xxx"})

    elif method == "fonepay":
        data = {
            "MERCHANT_CODE": settings.FONEPAY_MERCHANT_CODE,
            "PRN": str(order.id),
            "AMOUNT": str(order.total),
            "CURRENCY": "NPR",
        }
        checksum = generate_fonepay_checksum(data)
        data["CHECKSUM"] = checksum
        return Response({"url": settings.FONEPAY_PAYMENT_URL, "params": data})

    elif method == "bank":
        # Generate a bank reference and provide instructions
        reference = f"BANK-{order.id}"
        payment.method = "bank"
        payment.save()
        instructions = {
            "reference": reference,
            "amount": str(order.total),
            "bank_account": settings.BANK_ACCOUNT_NUMBER if hasattr(settings, "BANK_ACCOUNT_NUMBER") else "<ADD_BANK_ACCOUNT>",
            "bank_name": settings.BANK_NAME if hasattr(settings, "BANK_NAME") else "<BANK_NAME>",
        }
        return Response({"method": "bank", "instructions": instructions})

    else:
        return Response({"detail": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST)


# ---------- VERIFY ESEWA ----------
def _frontend_success_redirect(order_id: str | int, ref_id: str | None = None) -> str:
    base_url = getattr(settings, "ESEWA_SUCCESS_REDIRECT", getattr(settings, "FRONTEND_BASE_URL", ""))
    if not base_url:
        return "/"  # default fallback
    extras = f"?order_id={order_id}"
    if ref_id:
        extras += f"&ref_id={ref_id}"
    return f"{base_url}{extras}" if base_url.endswith('/') else f"{base_url}{extras}"


def _frontend_failure_redirect(order_id: str | int | None = None) -> str:
    base_url = getattr(settings, "ESEWA_FAILURE_REDIRECT", getattr(settings, "FRONTEND_BASE_URL", ""))
    if not base_url:
        return "/"
    extras = f"?order_id={order_id}" if order_id else ""
    return f"{base_url}{extras}" if base_url.endswith('/') else f"{base_url}{extras}"


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def esewa_verify(request):
    data = request.data if request.method == "POST" else request.GET

    ref_id = data.get("refId") or data.get("reference_id")
    amt = data.get("amt") or data.get("amount")
    oid = data.get("oid") or data.get("order_id")
    transaction_uuid = data.get("transaction_uuid") or data.get("uuid")

    if not (ref_id and (amt or transaction_uuid) and (oid or transaction_uuid)):
        return redirect(_frontend_failure_redirect(oid))

    payment_qs = Payment.objects.filter(method="esewa")
    payment = None
    if transaction_uuid:
        payment = payment_qs.filter(transaction_uuid=transaction_uuid).order_by("-created_at").first()
    if not payment and oid:
        payment = payment_qs.filter(order_id=oid).order_by("-created_at").first()
    if payment and not oid:
        oid = payment.order_id

    amount_to_verify = amt or (payment.amount if payment else None)
    if amount_to_verify is None:
        return redirect(_frontend_failure_redirect(oid))

    candidate_pids: list[str] = []
    if transaction_uuid:
        candidate_pids.append(transaction_uuid)
    if oid:
        candidate_pids.append(str(oid))
    if payment and payment.product_code:
        candidate_pids.append(payment.product_code)
    # Ensure uniqueness while preserving order
    seen = set()
    candidate_pids = [pid for pid in candidate_pids if not (pid in seen or seen.add(pid))]

    if not candidate_pids:
        return redirect(_frontend_failure_redirect(oid))

    success = False
    details: dict[str, object] = {}
    for pid in candidate_pids:
        is_valid, details = verify_esewa(ref_id, amount_to_verify, pid)
        if not is_valid:
            continue

        parsed_payload = (details or {}).get('parsed', {})
        response_oid = parsed_payload.get('oid') or parsed_payload.get('orderid') or parsed_payload.get('order_id')
        if response_oid and oid and str(response_oid).strip() != str(oid).strip():
            continue

        success = True
        break

    if success:
        order_identifier = oid or transaction_uuid or ""
        if payment:
            payment.status = "success"
            payment.ref_id = ref_id
            payment.save(update_fields=["status", "ref_id"])

            if payment.order:
                order_obj = payment.order
                order_obj.status = "paid"
                order_obj.is_paid = True
                order_obj.transaction_id = ref_id

                update_fields = ["status", "is_paid", "transaction_id"]
                desired_uuid = payment.transaction_uuid or transaction_uuid
                if desired_uuid and order_obj.transaction_uuid != desired_uuid:
                    order_obj.transaction_uuid = desired_uuid
                    update_fields.append("transaction_uuid")

                order_obj.save(update_fields=update_fields)
                order_identifier = order_obj.id

        return redirect(_frontend_success_redirect(order_identifier, ref_id))

    raw_status = str(data.get("status") or "").strip().lower()
    parsed_status = str((details.get("parsed") or {}).get("status") or "").strip().lower()
    pending_in_response = "pending" in raw_status or "pending" in parsed_status
    payment_is_pending = bool(payment and str(payment.status or "").strip().lower() == "pending")
    pending_order_id = None
    if payment and payment.order_id:
        pending_order_id = payment.order_id
    elif oid:
        pending_order_id = oid
    elif transaction_uuid:
        pending_order_id = transaction_uuid

    if (pending_in_response or payment_is_pending) and pending_order_id:
        return redirect(_frontend_success_redirect(pending_order_id, ref_id))

    if payment:
        if payment.status != "failed":
            payment.status = "failed"
            payment.save(update_fields=["status"])

    return redirect(_frontend_failure_redirect(oid))


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def esewa_fail(request):
    data = request.data if request.method == "POST" else request.GET
    oid = data.get("oid") or data.get("order_id")
    transaction_uuid = data.get("transaction_uuid") or data.get("uuid")
    payment_qs = Payment.objects.filter(method="esewa")
    payment = None
    if transaction_uuid:
        payment = payment_qs.filter(transaction_uuid=transaction_uuid).order_by("-created_at").first()
    if not payment and oid:
        payment = payment_qs.filter(order_id=oid).order_by("-created_at").first()
    if payment:
        if payment.status == "success":
            return redirect(_frontend_success_redirect(payment.order_id, payment.ref_id))
        if payment.status != "failed":
            payment.status = "failed"
            payment.save(update_fields=["status"])
        fallback_oid = payment.order_id
    else:
        fallback_oid = oid
    return redirect(_frontend_failure_redirect(fallback_oid))


# ---------- VERIFY KHALTI ----------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def khalti_verify(request):
    token = request.data.get("token")
    amount = request.data.get("amount")
    order_id = request.data.get("order_id")

    success = verify_khalti(token, amount)
    payment = Payment.objects.filter(order_id=order_id, method="khalti").first()

    if success and payment:
        payment.status = "success"
        payment.ref_id = token
        payment.save()
        payment.order.status = "paid"
        payment.order.is_paid = True
        payment.order.transaction_id = token
        payment.order.save()
        return Response({"message": "Khalti Payment Successful"})
    else:
        return Response({"message": "Khalti Payment Failed"}, status=400)


# ---------- VERIFY FONEPAY ----------
@api_view(["GET"])
@permission_classes([AllowAny])
def fonepay_verify(request):
    oid = request.GET.get("prn")
    success = verify_fonepay(oid)
    payment = Payment.objects.filter(order_id=oid, method="fonepay").first()

    if success and payment:
        payment.status = "success"
        payment.save()
        payment.order.status = "paid"
        payment.order.is_paid = True
        payment.order.save()
        return Response({"message": "Fonepay Payment Successful"})
    else:
        if payment:
            payment.status = "failed"
            payment.save()
        return Response({"message": "Fonepay Payment Failed"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def bank_confirm(request):
    """Confirm a bank transfer by reference and transaction id. This can be called by an admin
    panel or an internal webhook from the bank integration if available."""
    order_id = request.data.get("order_id")
    transaction_id = request.data.get("transaction_id")
    if not order_id or not transaction_id:
        return Response({"detail": "order_id and transaction_id are required"}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.filter(id=order_id, user=request.user).first()
    payment = Payment.objects.filter(order_id=order_id, method="bank").first()
    if not order or not payment:
        return Response({"detail": "Order/payment not found"}, status=status.HTTP_404_NOT_FOUND)

    payment.status = "success"
    payment.ref_id = transaction_id
    payment.save()
    order.status = "paid"
    order.is_paid = True
    order.transaction_id = transaction_id
    order.save()
    return Response({"message": "Bank payment confirmed"})


