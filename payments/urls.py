from django.urls import path
from .views import (
    bank_confirm,
    esewa_fail,
    esewa_verify,
    fonepay_verify,
    initiate_payment,
    khalti_verify,
)

urlpatterns = [
    path("initiate/", initiate_payment, name="initiate_payment"),
    path("esewa-verify/", esewa_verify, name="esewa_verify"),
    path("esewa-fail/", esewa_fail, name="esewa_fail"),
    path("khalti-verify/", khalti_verify, name="khalti_verify"),
    path("fonepay-verify/", fonepay_verify, name="fonepay_verify"),
    path("bank-confirm/", bank_confirm, name="bank_confirm"),
]
