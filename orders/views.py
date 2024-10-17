from rest_framework import viewsets, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from cart.models import Cart
from products.models import Product
from .models import Order, OrderItem
import uuid
from decimal import Decimal
import stripe
import logging
from .serializers import OrderSerializer, OrderItemSerializer

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY

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


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

def create_stripe_invoice(session, cart, total_price, order_number):
    # Create customer in Stripe if not already exists
    stripe_customer = stripe.Customer.create(
        email=session['customer_details']['email'],
        name=session['customer_details']['name'],
        address=session['customer_details']['address']
    )

    # Prepare invoice items based on cart
    for item in cart.items.all():
        stripe.InvoiceItem.create(
            customer=stripe_customer.id,
            amount=int(item.product.price * 100),  # Convert to cents
            currency="usd",
            description=f"{item.product.name} (Quantity: {item.quantity})"
        )

    # Create the invoice
    invoice = stripe.Invoice.create(
        customer=stripe_customer.id,
        collection_method='send_invoice',
        days_until_due=30,
        metadata={
            'order_number': order_number
        }
    )

    # Finalize and send the invoice to the customer
    stripe.Invoice.finalize_invoice(invoice.id)

    # Return the invoice URL for reference
    return invoice.hosted_invoice_url


def process_order_from_session(session):
    customer_email = session['customer_details']['email']
    cart_id = session.get('metadata', {}).get('cart_id')

    try:
        cart = Cart.objects.get(id=cart_id)
        total_price = calculate_total_price(cart)
        order_number = generate_order_number()

        with transaction.atomic():
            # Create Order
            order = Order.objects.create(
                owner=cart.owner,
                order_number=order_number,
                total_price=total_price
            )

            # Create Order Items and Update Stock
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price * item.quantity
                )
                update_product_stock(item.product, item.quantity)

            # Clear Cart
            cart.items.all().delete()

            # Create Stripe Invoice
            invoice_url = create_stripe_invoice(session, cart, total_price, order_number)

            # Send Confirmation Email with Invoice
            send_order_confirmation_email(customer_email, order, invoice_url)

    except Cart.DoesNotExist:
        logger.error(f"Cart with ID {cart_id} not found.")
        raise serializers.ValidationError({'detail': 'Cart not found for the session.'})


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
