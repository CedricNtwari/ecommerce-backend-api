from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet, OrderHistoryView, stripe_order_webhook

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('order-history/', OrderHistoryView.as_view(), name='order-history'),
    path('stripe-webhook/', stripe_order_webhook, name='stripe-webhook'),

]
