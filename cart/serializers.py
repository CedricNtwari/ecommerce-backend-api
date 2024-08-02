from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart item instances.
    
    Uses the ProductSerializer to provide a nested representation of the product associated with each cart item.
    Includes fields id, product (nested), quantity, price, and cart (read-only).
    """
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price', 'cart']
        extra_kwargs = {
            'cart': {'read_only': True}
        }

class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for cart instances.

    Provides a detailed view of a cart, including all items within the cart using CartItemSerializer.
    The 'owner' field displays the username of the cart owner. Fields created_at and updated_at are automatically managed and read-only.
    """
    items = CartItemSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Cart
        fields = ['id', 'owner', 'items', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
