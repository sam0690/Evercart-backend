from rest_framework import serializers
from .models import CartItem, Order, OrderItem
from products.serializers import ProductSerializer
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), 
        write_only=True, 
        source="product"
    )
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ("id", "user", "product", "product_id", "product_details", "quantity", "added_at")
        read_only_fields = ("id", "user", "product_details", "added_at")

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ("id", "product", "quantity", "price")

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "total",
            "status",
            "is_paid",
            "transaction_id",
            "shipping_address",
            "shipping_city",
            "shipping_postal_code",
            "shipping_country",
            "created_at",
            "items",
        )
        read_only_fields = (
            "user",
            "total",
            "status",
            "is_paid",
            "transaction_id",
            "created_at",
            "items",
        )


class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class OrderSubmitSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)
    shipping_address = serializers.CharField(max_length=255)
    shipping_city = serializers.CharField(max_length=120)
    shipping_postal_code = serializers.CharField(max_length=30)
    shipping_country = serializers.CharField(max_length=120)
