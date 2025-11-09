from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Payment
from orders.models import Order
from django.db import models
from .utils import verify_esewa, verify_khalti, verify_fonepay, generate_fonepay_checksum

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
        payload = {
            "amt": order.total,
            "pdc": 0,
            "psc": 0,
            "txAmt": 0,
            "tAmt": order.total,
            "pid": str(order.id),
            "scd": settings.ESEWA_MERCHANT_ID,
            "su": f"http://localhost:8000/api/payments/esewa-verify/?oid={order.id}",
            "fu": f"http://localhost:8000/api/payments/esewa-fail/?oid={order.id}"
        }
        return Response({"url": settings.ESEWA_PAYMENT_URL, "params": payload})

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
@api_view(["GET"])
@permission_classes([AllowAny])
def esewa_verify(request):
    refId = request.GET.get("refId")
    amt = request.GET.get("amt")
    oid = request.GET.get("oid")

    success = verify_esewa(refId, amt, oid)
    payment = Payment.objects.filter(order_id=oid, method="esewa").first()

    if success and payment:
        payment.status = "success"
        payment.ref_id = refId
        payment.save()
        payment.order.status = "paid"
        payment.order.is_paid = True
        payment.order.transaction_id = refId
        payment.order.save()
        return Response({"message": "eSewa Payment Successful"})
    else:
        if payment:
            payment.status = "failed"
            payment.save()
        return Response({"message": "eSewa Payment Failed"}, status=400)


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
