from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from profiles.serializers import ProfileSerializer
from products.serializers import ProductSerializer
import uuid

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem instances.
    
    This serializer links an OrderItem to its respective Order and Product.
    It now includes full product details instead of just the product ID.
    """
    product = ProductSerializer(read_only=True)  # Use ProductSerializer to include full product details
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order instances.

    Serializes order data including items, owner, and owner's profile.
    Automatically generates a unique order number upon creation using a UUID, truncated to 20 characters.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    profile = ProfileSerializer(source='owner.profile', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'owner', 'profile', 'total_price', 'created_at', 'updated_at', 'status', 'items']
        read_only_fields = ['order_number']

    def create(self, validated_data):
        """
        Overrides the default create method to add a unique order number before saving the new order instance.
        """
        validated_data['order_number'] = str(uuid.uuid4()).replace("-", "").upper()[:20]
        return super().create(validated_data)
