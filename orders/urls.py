from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, OrderViewSet, create_order_from_cart, submit_order

router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('create-from-cart/', create_order_from_cart, name='create_order_from_cart'),
    path('submit/', submit_order, name='submit_order'),
]
