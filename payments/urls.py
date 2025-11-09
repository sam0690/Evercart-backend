from django.urls import path
from .views import (
    initiate_payment,
    esewa_verify,
    khalti_verify,
    fonepay_verify,
    bank_confirm,
)

urlpatterns = [
    path("initiate/", initiate_payment, name="initiate_payment"),
    path("esewa-verify/", esewa_verify, name="esewa_verify"),
    path("khalti-verify/", khalti_verify, name="khalti_verify"),
    path("fonepay-verify/", fonepay_verify, name="fonepay_verify"),
    path("bank-confirm/", bank_confirm, name="bank_confirm"),
]
