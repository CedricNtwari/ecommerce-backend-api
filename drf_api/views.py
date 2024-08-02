from rest_framework.decorators import api_view
from rest_framework.response import Response
from .settings import (
    JWT_AUTH_COOKIE, JWT_AUTH_REFRESH_COOKIE, JWT_AUTH_SAMESITE,
    JWT_AUTH_SECURE,
)

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