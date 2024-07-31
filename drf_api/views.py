# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view()
def root_route(request):
    return Response({
        "message": "Welcome to the eCommerce Backend API! Manage products, user authentication, orders and reviews efficiently."
    })
