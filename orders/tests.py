from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Order, OrderItem
from products.models import Product

class OrderTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user2 = User.objects.create_user(username='otheruser', password='12345')
        self.product = Product.objects.create(
            owner=self.user,
            name='Test Product',
            description='Test Description',
            price=100.00,
            stock=10
        )
        self.client.login(username='testuser', password='12345')

    def test_create_order(self):
        order_data = {
            'total_price': 100.00,
            'status': 'Pending',
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 1,
                    'price': 100.00
                }
            ]
        }
        response = self.client.post('/orders/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.owner, self.user)
        self.assertEqual(order.total_price, 100.00)
        self.assertEqual(order.status, 'Pending')
        self.assertEqual(order.items.first().product, self.product)

    def test_add_item_to_order(self):
        order = Order.objects.create(owner=self.user, total_price=100.00, status='Pending')
        order_item_data = {
            'product': self.product.id,
            'quantity': 1,
            'price': 100.00
        }
        response = self.client.post(f'/orders/{order.id}/add_item/', order_item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.price, 100.00)

    def test_order_history(self):
        Order.objects.create(owner=self.user, total_price=100.00, status='Pending')
        response = self.client.get('/order-history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        order = response.data[0]
        self.assertEqual(order['owner'], self.user.username)

    def test_cancel_order(self):
        order = Order.objects.create(owner=self.user, total_price=100.00, status='Pending')
        response = self.client.post(f'/orders/{order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Order cancelled')
        order.refresh_from_db()
        self.assertEqual(order.status, 'Cancelled')

    def test_user_cannot_cancel_another_users_order(self):
        order = Order.objects.create(owner=self.user2, total_price=100.00, status='Pending')
        response = self.client.post(f'/orders/{order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_modify_delivered_or_cancelled_order(self):
        order = Order.objects.create(owner=self.user, total_price=100.00, status='Delivered')
        order_data = {
            'total_price': 150.00,
            'status': 'Processing'
        }
        response = self.client.put(f'/orders/{order.id}/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        order.status = 'Cancelled'
        order.save()
        response = self.client.put(f'/orders/{order.id}/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_with_invalid_data(self):
        order_data = {
            'total_price': 'invalid_price',
            'status': 'Pending'
        }
        response = self.client.post('/orders/', order_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_item_with_invalid_data(self):
        order = Order.objects.create(owner=self.user, total_price=100.00, status='Pending')
        order_item_data = {
            'product': self.product.id,
            'quantity': 'invalid_quantity',
            'price': 100.00
        }
        response = self.client.post(f'/orders/{order.id}/add_item/', order_item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders(self):
        Order.objects.create(owner=self.user, total_price=100.00, status='Pending')
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_order(self):
        order = Order.objects.create(owner=self.user, total_price=100.00, status='Pending')
        response = self.client.get(f'/orders/{order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner'], self.user.username)
        self.assertEqual(response.data['total_price'], '100.00')
        self.assertEqual(response.data['status'], 'Pending')
