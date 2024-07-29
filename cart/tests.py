from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Cart, CartItem
from products.models import Product

class CartTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user2 = User.objects.create_user(username='otheruser', password='12345')
        self.admin_user = User.objects.create_user(username='adminuser', password='12345')
        self.admin_user.is_staff = True
        self.admin_user.save()
        self.product = Product.objects.create(
            owner=self.user,
            name='Test Product',
            description='Test Description',
            price=100.00,
            stock=10
        )
        self.client.login(username='testuser', password='12345')

    def test_create_cart(self):
        response = self.client.post('/carts/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.count(), 1)
        cart = Cart.objects.first()
        self.assertEqual(cart.owner, self.user)

    def test_add_item_to_cart(self):
        cart = Cart.objects.create(owner=self.user)
        item_data = {
            'product': self.product.id,
            'quantity': 1,
            'price': 100.00
        }
        response = self.client.post(f'/carts/{cart.id}/add_item/', item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.cart, cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 1)
        self.assertEqual(cart_item.price, 100.00)

    def test_remove_item_from_cart(self):
        cart = Cart.objects.create(owner=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=1, price=100.00)
        item_data = {
            'item_id': cart_item.id
        }
        response = self.client.post(f'/carts/{cart.id}/remove_item/', item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_update_item_quantity_in_cart(self):
        cart = Cart.objects.create(owner=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=1, price=100.00)
        item_data = {
            'item_id': cart_item.id,
            'quantity': 2
        }
        response = self.client.post(f'/carts/{cart.id}/update_quantity/', item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_user_cannot_access_another_users_cart(self):
        cart = Cart.objects.create(owner=self.user2)
        self.client.logout()
        self.client.login(username='testuser', password='12345')
        response = self.client.get(f'/carts/{cart.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_list_all_carts(self):
        self.client.login(username='adminuser', password='12345')
        Cart.objects.create(owner=self.user)
        Cart.objects.create(owner=self.user2)
        response = self.client.get('/carts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
