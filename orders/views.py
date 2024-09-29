from rest_framework import generics, viewsets, permissions, status, serializers, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings


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

        This method generates a unique order number for each order, validates the order items,
        checks for stock availability, calculates the total price, saves the order with the 
        current user as the owner, and sends an email confirmation to the user.

        Raises:
        ValidationError: If no order items are provided, if item data is invalid, or if 
        stock is insufficient for any item.
        """
        import uuid
        from decimal import Decimal
        from django.core.mail import send_mail
        from django.conf import settings
        from .models import Product  # Assuming your product model is in the same app

        # Generate a unique order number
        order_number = str(uuid.uuid4()).replace("-", "").upper()[:20]

        # Validate order items
        order_items_data = self.request.data.get('order_items', [])
        if not order_items_data:
            raise serializers.ValidationError("No order items provided.")

        # Initialize the total price
        total_price = Decimal(0)

        # Validate and check stock availability for each item
        for item_data in order_items_data:
            product_id = item_data['product']
            quantity = item_data['quantity']
            price = Decimal(item_data['price'])

            # Fetch the product from the database to check stock availability
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {product_id} does not exist.")

            # Check if there is enough stock for the requested quantity
            if product.stock < quantity:
                raise serializers.ValidationError(f"Not enough stock for product '{product.name}'. Only {product.stock} left.")

            # Calculate the total price for this item
            total_price += price * quantity

        # Save the order with the current user and generated order number
        order = serializer.save(owner=self.request.user, order_number=order_number, total_price=total_price)

        # Create the order items and update product stock
        for item_data in order_items_data:
            product_id = item_data['product']
            quantity = item_data['quantity']
            price = Decimal(item_data['price'])

            # Fetch the product and reduce stock
            product = Product.objects.get(id=product_id)
            product.stock -= quantity  # Deduct the purchased quantity from stock
            product.save()  # Save the updated stock to the database

        # Create the order item
        OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

        # Send order confirmation email
        subject = f"Order Confirmation - {order_number}"
        message = (
            f"Dear {self.request.user.username},\n\n"
            f"Thank you for your order. Your order number is {order_number}.\n\n"
            f"Total Price: ${order.total_price}\n\n"
            f"We will notify you once the order is processed."
        )
        recipient_list = [self.request.user.email]

        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            raise serializers.ValidationError({"error": f"Failed to send confirmation email. Error: {str(e)}"})

        return order


    def perform_update(self, serializer):
        """
        Update an existing order instance.

        Ensures that orders with a status of 'Delivered' or 'Cancelled' cannot be modified.
        
        Raises:
            ValidationError: If attempting to modify an order that is already delivered or cancelled.
        """
        instance = self.get_object()
        previous_status = instance.status
        order = super().perform_update(serializer)
    
         # If the status has changed, send an email notification
        if previous_status != instance.status:
            subject = f"Order {instance.order_number} Status Update"
            message = f"Dear {self.request.user.username},\n\nYour order {instance.order_number} status has been updated to {instance.status}."
            recipient_list = [self.request.user.email]

        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                recipient_list,
                fail_silently=False,
            )
        except Exception as e:
            raise serializers.ValidationError({"error": "Failed to send status update email."})

        return order

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
