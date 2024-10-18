from rest_framework import viewsets, serializers, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from rest_framework.views import APIView
import uuid
from decimal import Decimal
import stripe
import logging

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

# Webhook for Stripe payments
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_order_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Signature verification failed: {e}")
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        process_order_from_session(session)

    return Response(status=200)

# Order ViewSet for managing orders
class OrderViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Order instances.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['order_number', 'owner__username', 'status', 'total_price']
    search_fields = ['order_number', 'owner__username', 'status']

    def perform_create(self, serializer):
        pass  # Order creation handled by the Stripe webhook

    def perform_update(self, serializer):
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

# OrderItem ViewSet for managing order items
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

# Order History View for retrieving a user's order history
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

# Stripe invoice creation and processing
def create_stripe_invoice(session, cart, total_price, order_number):
    stripe_customer = stripe.Customer.create(
        email=session['customer_details']['email'],
        name=session['customer_details']['name'],
        address=session['customer_details']['address']
    )

    for item in cart.items.all():
        stripe.InvoiceItem.create(
            customer=stripe_customer.id,
            amount=int(item.product.price * 100),
            currency="usd",
            description=f"{item.product.name} (Quantity: {item.quantity})"
        )

    invoice = stripe.Invoice.create(
        customer=stripe_customer.id,
        collection_method='send_invoice',
        days_until_due=30,
        metadata={
            'order_number': order_number
        }
    )

    stripe.Invoice.finalize_invoice(invoice.id)

    return invoice.hosted_invoice_url

# Order processing from Stripe session
def process_order_from_session(session):
    customer_email = session['customer_details']['email']
    cart_id = session.get('metadata', {}).get('cart_id')

    try:
        cart = Cart.objects.get(id=cart_id)
        total_price = calculate_total_price(cart)
        order_number = generate_order_number()

        with transaction.atomic():
            order = Order.objects.create(
                owner=cart.owner,
                order_number=order_number,
                total_price=total_price
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price * item.quantity
                )
                update_product_stock(item.product, item.quantity)

            cart.items.all().delete()

            invoice_url = create_stripe_invoice(session, cart, total_price, order_number)

            send_order_confirmation_email(customer_email, order, invoice_url)

    except Cart.DoesNotExist:
        logger.error(f"Cart with ID {cart_id} not found.")
        raise serializers.ValidationError({'detail': 'Cart not found for the session.'})

# Helper functions
def calculate_total_price(cart):
    total_price = Decimal(0)
    for item in cart.items.all():
        total_price += item.product.price * item.quantity
    return total_price

def generate_order_number():
    return str(uuid.uuid4()).replace("-", "").upper()[:20]

def update_product_stock(product, quantity):
    product.stock -= quantity
    if product.stock <= 0:
        product.available = False
    product.save()

def send_order_confirmation_email(customer_email, order, invoice_url):
    subject = f"Your Order Confirmation - {order.order_number}"
    message = f"""
    Dear {customer_email},

    Thank you for shopping with us! Your order number is **{order.order_number}**.

    Here are the details of your purchase:
    - Order Number: {order.order_number}
    - Total: ${order.total_price} USD

    You can view your invoice and complete the payment at the following link:
    {invoice_url}

    We'll notify you with a tracking number once your order is shipped.

    Best regards,
    Trade Corner Team
    """
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [customer_email], fail_silently=False)
    except Exception as e:
        raise serializers.ValidationError({"error": f"Failed to send confirmation email. Error: {str(e)}"})
