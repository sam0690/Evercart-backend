from rest_framework import serializers
from decimal import Decimal
from django.contrib.auth import get_user_model
from .models import CartItem, Order, OrderItem
from products.serializers import ProductSerializer
from products.models import Product
from payments.models import Payment
from payments.serializers import PaymentSerializer
from users.serializers import UserSerializer

User = get_user_model()

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
    product_details = ProductSerializer(source="product", read_only=True)
    product_id = serializers.IntegerField(source="product.id", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_details", "product_id", "quantity", "price")

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_details = UserSerializer(source="user", read_only=True)
    payment_details = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "user_details",
            "total",
            "status",
            "is_paid",
            "transaction_id",
            "shipping_address",
            "shipping_city",
            "shipping_postal_code",
            "shipping_country",
            "shipping_phone",
            "created_at",
            "items",
            "payment_details",
        )
        read_only_fields = (
            "user",
            "total",
            "status",
            "is_paid",
            "transaction_id",
            "created_at",
            "items",
            "payment_details",
        )


    def get_payment_details(self, obj):
        prefetched = getattr(obj, "_prefetched_objects_cache", {})
        payments = prefetched.get("payment_set") if isinstance(prefetched, dict) else None
        if payments:
            payment_instance = payments[0]
            return PaymentSerializer(payment_instance, context=self.context).data
        payment_instance = Payment.objects.filter(order=obj).order_by("-created_at").first()
        if payment_instance:
            return PaymentSerializer(payment_instance, context=self.context).data
        return None

class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class OrderSubmitSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)
    shipping_address = serializers.CharField(max_length=255)
    shipping_city = serializers.CharField(max_length=120)
    shipping_postal_code = serializers.CharField(max_length=30)
    shipping_country = serializers.CharField(max_length=120)
    shipping_phone = serializers.CharField(max_length=20)


class OrderAdminWriteSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    items_data = OrderItemInputSerializer(many=True, write_only=True, required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

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
            "shipping_phone",
            "created_at",
            "items",
            "items_data",
        )
        read_only_fields = ("total", "created_at", "items")
        extra_kwargs = {
            "status": {"required": False},
            "is_paid": {"required": False},
            "transaction_id": {"required": False, "allow_blank": True},
            "shipping_address": {"required": False, "allow_blank": True},
            "shipping_city": {"required": False, "allow_blank": True},
            "shipping_postal_code": {"required": False, "allow_blank": True},
            "shipping_country": {"required": False, "allow_blank": True},
            "shipping_phone": {"required": False, "allow_blank": True},
        }

    def _create_items(self, order: Order, items_data):
        total = Decimal("0")
        for item in items_data:
            product: Product = item["product"]
            quantity = item["quantity"]
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )
            total += product.price * quantity
        order.total = total
        order.save()

    def create(self, validated_data):
        items_data = validated_data.pop("items_data", [])
        if not items_data:
            raise serializers.ValidationError({"items_data": "At least one item is required."})
        order = Order.objects.create(**validated_data)
        self._create_items(order, items_data)
        return order

    def update(self, instance: Order, validated_data):
        items_data = validated_data.pop("items_data", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if items_data is not None:
            instance.items.all().delete()
            self._create_items(instance, items_data)
        else:
            instance.save()
        return instance
