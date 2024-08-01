# In orders/serializers.py

from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from profiles.serializers import ProfileSerializer
import uuid

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    profile = ProfileSerializer(source='owner.profile', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'owner', 'profile', 'total_price', 'created_at', 'updated_at', 'status', 'items']
        read_only_fields = ['order_number']

    def create(self, validated_data):
        validated_data['order_number'] = str(uuid.uuid4()).replace("-", "").upper()[:20]
        return super().create(validated_data)
