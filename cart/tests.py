from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Cart, CartItem
from products.models import Product

class CartTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(username='testuser', password='password')
        self.admin_user = User.objects.create_superuser(username='adminuser', password='password')
        another_user = User.objects.create_user(username='anotheruser', password='password')
        
        # Log in as a regular user to test cart creation
        self.client.login(username='testuser', password='password')
        
        # Create a cart for the logged-in user
        Cart.objects.create(owner=self.user)

        # Create a cart for another user
        Cart.objects.create(owner=another_user)

    def test_create_cart(self):
        """
        Ensure that a cart is created for a user if it doesn't exist.
        """
        Cart.objects.filter(owner=self.user).delete()
        
        url = reverse('cart-list')
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.filter(owner=self.user).count(), 1)

    def test_add_item_to_cart(self):
        """
        Ensure we can add an item to the cart.
        """
        self.client.login(username='testuser', password='password')

        product = Product.objects.create(
            owner=self.user,
            name='Test Product',
            price=10.00,
            stock=100
        )

        url = reverse('cart-add-item')
        response = self.client.post(url, {'product': product.id, 'quantity': 2}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cart_item = CartItem.objects.get(cart__owner=self.user, product=product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.price, 20.00)

    def test_admin_can_list_all_carts(self):
        """
        Ensure that an admin user can list all carts.
        """
        self.client.login(username='adminuser', password='password')

        url = reverse('cart-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], Cart.objects.count())
