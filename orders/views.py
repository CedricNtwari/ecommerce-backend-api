from rest_framework import generics, viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Generate unique order number
        import uuid
        order_number = str(uuid.uuid4()).replace("-", "").upper()[:20]
        
        # Save the order with the current user and generated order number
        order = serializer.save(owner=self.request.user, order_number=order_number)
        
        # Create order items (this example assumes order items are sent in the request data)
        order_items_data = self.request.data.get('items')
        for item_data in order_items_data:
            product_id = item_data['product']
            quantity = item_data['quantity']
            price = item_data['price']
            OrderItem.objects.create(order=order, product_id=product_id, quantity=quantity, price=price)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status in ['Delivered', 'Cancelled']:
            raise serializers.ValidationError("Cannot modify delivered or cancelled orders.")
        serializer.save()

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
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
        order = self.get_object()
        if order.owner != request.user:
            return Response({'detail': 'You do not have permission to cancel this order.'}, status=status.HTTP_403_FORBIDDEN)
        if order.status not in ['Pending', 'Processing']:
            return Response({'detail': 'Cannot cancel an order that is already shipped or delivered.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'Cancelled'
        order.save()
        return Response({'status': 'Order cancelled'}, status=status.HTTP_200_OK)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user)
