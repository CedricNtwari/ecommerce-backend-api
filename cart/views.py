from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_api.permissions import IsOwnerOrReadOnly
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products.models import Product

class CartViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing cart instances.
    The viewset supports retrieving all carts, adding items to carts,
    removing items from carts, and updating the quantity of items in carts.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Retrieves the queryset for Cart instances. If the user is staff, they can see all carts.
        Regular users see only their own carts.
        """
        if self.request.user.is_staff:
            return Cart.objects.all()
        return Cart.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """
        Custom creation logic for cart. Ensures a user does not create more than one cart.
        Raises a ValidationError if the user already owns a cart.
        """
        if Cart.objects.filter(owner=self.request.user).exists():
            raise serializers.ValidationError({'non_field_errors': ["A cart already exists for this user."]})
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Adds a new item to the cart. If the item is already in the cart, it updates the quantity.
        """
        try:
            cart, _ = Cart.objects.get_or_create(owner=request.user)
            
            product_id = request.data.get('product')
            quantity = request.data.get('quantity')

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, defaults={'quantity': quantity, 'price': product.price * quantity}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.price = cart_item.quantity * product.price
                cart_item.save()

            serializer = CartItemSerializer(cart_item, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error adding item to cart: {e}")
            return Response({'detail': 'Internal server error.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            if quantity > cart_item.product.stock:
                return Response({'detail': 'Quantity exceeds stock.'}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = quantity
            cart_item.price = cart_item.quantity * cart_item.product.price
            cart_item.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in cart.'}, status=status.HTTP_404_NOT_FOUND)
