from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from .models import CartItem, Order, OrderItem
from .serializers import CartItemSerializer, OrderSerializer, OrderSubmitSerializer
from django.shortcuts import get_object_or_404
from products.models import Product
from decimal import Decimal
from django.db import transaction

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related("product")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # increment if already exists
        product_id = request.data.get("product") or request.data.get("product_id")
        qty = int(request.data.get("quantity", 1))
        product = get_object_or_404(Product, pk=product_id)
        obj, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            obj.quantity = obj.quantity + qty
            obj.save()
        else:
            obj.quantity = qty
            obj.save()
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_order_from_cart(request):
    # Create order from cart items of current user
    cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    if not cart_items.exists():
        return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    total = Decimal(0)
    order = Order.objects.create(user=request.user, total=0)
    for item in cart_items:
        price = item.product.price
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=price)
        total += price * item.quantity
    order.total = total
    order.save()
    # clear cart
    cart_items.delete()
    return Response({"order_id": order.id, "total": order.total}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_order(request):
    """Create a new order from explicit client-provided items with is_paid=False.
    Total is computed server-side from product prices.
    """
    serializer = OrderSubmitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    items_data = serializer.validated_data["items"]
    shipping = {
        "shipping_address": serializer.validated_data["shipping_address"],
        "shipping_city": serializer.validated_data["shipping_city"],
        "shipping_postal_code": serializer.validated_data["shipping_postal_code"],
        "shipping_country": serializer.validated_data["shipping_country"],
    }

    with transaction.atomic():
        total = Decimal(0)
        order = Order.objects.create(user=request.user, total=0, status="pending", is_paid=False, **shipping)
        for item in items_data:
            product: Product = item["product"]
            qty = int(item["quantity"])
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
            total += product.price * qty
        order.total = total
        order.save()

    return Response({"order_id": order.id, "total": str(order.total)}, status=status.HTTP_201_CREATED)
