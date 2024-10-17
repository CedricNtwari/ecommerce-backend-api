from rest_framework import generics, viewsets, permissions, status, serializers, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order, OrderItem, Product
from .serializers import OrderSerializer, OrderItemSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
import stripe
import uuid
from decimal import Decimal
import logging


# Order ViewSet
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
        # Order creation will be handled by the Stripe webhook after payment.
        pass

    def perform_update(self, serializer):
        """
        Update an existing order instance and send an email if the status changes.
        """
        instance = self.get_object()
        previous_status = instance.status
        order = super().perform_update(serializer)

        if previous_status != instance.status:
            subject = f"Order {instance.order_number} Status Update"
            message = f"Dear {self.request.user.username},\n\nYour order {instance.order_number} status has been updated to {instance.status}."
            recipient_list = [self.request.user.email]
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
            except Exception as e:
                raise serializers.ValidationError({"error": "Failed to send status update email."})

        return order

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """
        Custom action to add an item to an existing order.
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
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderHistoryView(generics.ListAPIView):
    """
    API view for retrieving a list of orders belonging to the authenticated user.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return the queryset of orders for the current authenticated user.
        """
        return Order.objects.filter(owner=self.request.user)

logger = logging.getLogger(__name__)

# Stripe webhook handler
@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Signature verification failed: {e}")
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        create_order_and_send_email(session)
        
    logger.info(f"Processed Stripe event: {event['type']}")
    return Response(status=200)


def create_order_and_send_email(session):
    """
    Create an order after payment success and send a confirmation email.
    """
    customer_email = session['customer_details']['email']
    line_items = session['line_items']['data']
    
    # Fetch the metadata if cart info is passed
    cart_id = session.get('metadata', {}).get('cart_id')
    
    try:
        # Fetch the cart from the cart ID, if passed
        cart = Cart.objects.get(id=cart_id)
    except Cart.DoesNotExist:
        raise serializers.ValidationError({'detail': 'Cart not found for the session.'})

    # Generate an order number
    order_number = str(uuid.uuid4()).replace("-", "").upper()[:20]
    
    # Validate and calculate total price
    total_price = Decimal(0)
    for item in cart.items.all():
        total_price += item.product.price * item.quantity

    # Create the order and save to the database
    order = Order.objects.create(
        owner_email=customer_email, 
        order_number=order_number, 
        total_price=total_price,
        owner=cart.owner  # Assuming Cart has an owner field linked to the user
    )

    # Create order items and update stock
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order, 
            product=item.product, 
            quantity=item.quantity, 
            price=item.product.price * item.quantity
        )
        item.product.stock -= item.quantity
        if item.product.stock <= 0:
            item.product.available = False  # Mark as out of stock
        item.product.save()

    # Clear the cart
    cart.items.all().delete()

    # Send the confirmation email
    subject = f"Order Confirmation - {order_number}"
    message = f"Dear {customer_email},\n\nThank you for your order. Your order number is {order_number}."
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [customer_email], fail_silently=False)
    except Exception as e:
        raise serializers.ValidationError({"error": f"Failed to send confirmation email. Error: {str(e)}"})

