from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "user", "order", "method", "amount", "ref_id", "status", "created_at")
        read_only_fields = ("user", "status", "created_at")

class PaymentInitiateSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=["esewa", "khalti", "fonepay"])
    order_id = serializers.IntegerField()

class ESewaVerifySerializer(serializers.Serializer):
    refId = serializers.CharField()
    amt = serializers.DecimalField(max_digits=10, decimal_places=2)
    oid = serializers.CharField()

class KhaltiVerifySerializer(serializers.Serializer):
    token = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_id = serializers.IntegerField()
