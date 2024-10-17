from rest_framework.decorators import api_view
from rest_framework.response import Response
from .settings import (
    JWT_AUTH_COOKIE, JWT_AUTH_REFRESH_COOKIE, JWT_AUTH_SAMESITE,
    JWT_AUTH_SECURE,
)
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.views import APIView
from .serializers import ContactSerializer
import os, stripe
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from django.db import transaction
from cart.models import Cart
from products.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view()
def root_route(request):
    """
    Root API view that provides a welcome message to the eCommerce Backend API.
    
    This endpoint serves as an entry point or landing API, giving a brief description of the backend capabilities.
    It is typically used to confirm that the API is operational and to provide initial guidance to developers.
    """
    return Response({
        "message": "Welcome to the eCommerce Backend API! Manage products, user authentication, orders and reviews efficiently."
    })


@api_view(['POST'])
def logout_route(request):
    """
    API view to log out a user by clearing the JWT tokens stored in cookies.
    
    This function sets the JWT access and refresh tokens to expire immediately, effectively logging the user out.
    It uses secure, HTTP-only cookies to ensure that the tokens are not accessible via client-side scripts,
    enhancing the security of the logout process.
    """
    response = Response()
    response.set_cookie(
        key=JWT_AUTH_COOKIE,
        value='',
        httponly=True,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',
        max_age=0,
        samesite=JWT_AUTH_SAMESITE,
        secure=JWT_AUTH_SECURE,
    )
    response.set_cookie(
        key=JWT_AUTH_REFRESH_COOKIE,
        value='',
        httponly=True,
        expires='Thu, 01 Jan 1970 00:00:00 GMT',
        max_age=0,
        samesite=JWT_AUTH_SAMESITE,
        secure=JWT_AUTH_SECURE,
    )
    return response


class ContactUsView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('name')
            email = serializer.validated_data.get('email')
            message = serializer.validated_data.get('message')

            subject = f"New Contact Form Submission from {name}"
            email_message = f"Message from {name} ({email}):\n\n{message}"
            recipient_list = recipient_list=[os.environ.get('EMAIL_HOST_USER')]


            try:
                send_mail(
                    subject,
                    email_message,
                    email,
                    recipient_list,
                    fail_silently=False,
                )
                return Response({"detail": "Message sent successfully."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=400)

    # Only handle the successful checkout session completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Assuming order_data is stored in the session metadata
        order_data = session.get('metadata', {}).get('order_data')

        if order_data:
            # Update product stock and availability
            with transaction.atomic():
                for item in order_data['order_items']:
                    product = Product.objects.get(id=item['product'])
                    
                    # Reduce product stock by the purchased quantity
                    product.stock -= item['quantity']
                    
                    # If stock reaches 0, mark the product as unavailable
                    if product.stock <= 0:
                        product.stock = 0
                        product.available = False
                        
                    # Save the updated product details
                    product.save()

                # You could also save the order here to order history if needed.
        
    return Response(status=200)


@api_view(['POST'])
def create_checkout_session(request):
    try:
        cart_id = request.data.get('cart_id')
        if not cart_id:
            return Response({'error': 'cart_id is required'}, status=400)

        cart = Cart.objects.get(id=cart_id)

        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                    'unit_amount': int(float(item.product.price) * 100),
                },
                'quantity': item.quantity,
            }
            for item in cart.items.all()
        ]

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='https://trade-corner-018d2b5f7079.herokuapp.com/payment-success',
            cancel_url='https://trade-corner-018d2b5f7079.herokuapp.com/payment-failure',
            metadata={'cart_id': cart_id}
        )

        return Response({'id': checkout_session.id})
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
