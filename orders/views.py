from rest_framework import generics, viewsets, permissions, status, serializers, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Order instances.
    
    This viewset allows for the creation, retrieval, update, and deletion of orders. 
    It enforces that only authenticated users can perform actions and includes filtering 
    and searching capabilities based on order details.

    Filters:
        - Order Number
        - Owner's Username
        - Status
        - Total Price

    Search Fields:
        - Order Number
        - Owner's Username
        - Status
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['order_number', 'owner__username', 'status', 'total_price']
    search_fields = ['order_number', 'owner__username', 'status']

    def perform_create(self, serializer):
        """
        Create a new order with a unique order number and associated items.
        
        The method generates a unique order number for each order and saves the order 
        with the current user as the owner. It then creates order items based on the 
        provided request data.

        Raises:
            ValidationError: If no order items are provided in the request data.
        """
        import uuid
        order_number = str(uuid.uuid4()).replace("-", "").upper()[:20]

        # Save the order with the current user and generated order number
        order = serializer.save(owner=self.request.user, order_number=order_number)

        # Create order items (this example assumes order items are sent in the request data)
        order_items_data = self.request.data.get('order_items', [])

        # Check if order_items_data is None
        if order_items_data is None:
            raise serializers.ValidationError("No order items provided.")

        for item_data in order_items_data:
            product_id = item_data['product']
            quantity = item_data['quantity']
            price = item_data['price']
            OrderItem.objects.create(order=order, product_id=product_id, quantity=quantity, price=price)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        """
        Update an existing order instance.

        Ensures that orders with a status of 'Delivered' or 'Cancelled' cannot be modified.
        
        Raises:
            ValidationError: If attempting to modify an order that is already delivered or cancelled.
        """
        instance = self.get_object()
        if instance.status in ['Delivered', 'Cancelled']:
            raise serializers.ValidationError("Cannot modify delivered or cancelled orders.")
        serializer.save()

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """
        Custom action to add an item to an existing order.

        This method validates and adds a new item to the specified order, 
        associating it with the order instance.
        
        Returns:
            Response: Serialized data of the newly added order item or validation errors.
        """
        order = self.get_object()
        item_data = request.data
        item_data['order'] = order.id
        serializer = OrderItemSerializer(data=item_data)
        if serializer.is_valid():
            serializer.save(order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Custom action to cancel an order.

        Only the owner of an order can cancel it, and it can only be cancelled if 
        its status is 'Pending' or 'Processing'. Updates the order status to 'Cancelled'.

        Returns:
            Response: Confirmation of order cancellation or error message if not permitted.
        """
        order = self.get_object()
        if order.owner != request.user:
            return Response({'detail': 'You do not have permission to cancel this order.'}, status=status.HTTP_403_FORBIDDEN)
        if order.status not in ['Pending', 'Processing']:
            return Response({'detail': 'Cannot cancel an order that is already shipped or delivered.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'Cancelled'
        order.save()
        return Response({'status': 'Order cancelled'}, status=status.HTTP_200_OK)

class OrderItemViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing OrderItem instances.
    
    This viewset allows for full CRUD operations on order items, with permissions 
    restricted to authenticated users. It provides a detailed view of the items 
    associated with each order.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderHistoryView(generics.ListAPIView):
    """
    API view for retrieving a list of orders belonging to the authenticated user.
    
    This view provides users with a history of their orders, filtered by the 
    current authenticated user.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return the queryset of orders for the current authenticated user.
        """
        return Order.objects.filter(owner=self.request.user)
