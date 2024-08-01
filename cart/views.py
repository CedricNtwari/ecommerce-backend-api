from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_api.permissions import IsOwnerOrReadOnly
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Cart.objects.all()
        return Cart.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Check if a cart already exists for the user
        if Cart.objects.filter(owner=self.request.user).exists():
            raise serializers.ValidationError({'non_field_errors': ["A cart already exists for this user."]})
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        # Get or create a cart for the current user
        cart, _ = Cart.objects.get_or_create(owner=request.user)
        
        # Get the product ID and quantity from the request data
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        # Fetch the product to get its price
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the item already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={'quantity': quantity, 'price': product.price * quantity}
        )

        if not created:
            # If the item already exists, update the quantity and price
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * product.price
            cart_item.save()

        serializer = CartItemSerializer(cart_item, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        CartItem.objects.filter(id=item_id, cart=cart).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def update_quantity(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.quantity = quantity
            cart_item.price = cart_item.quantity * cart_item.product.price
            cart_item.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in cart.'}, status=status.HTTP_404_NOT_FOUND)
