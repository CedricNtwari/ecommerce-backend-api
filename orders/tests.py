from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from products.models import Product
from .models import Order, OrderItem

class OrderTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Create a test product
        self.product = Product.objects.create(name='Test Product', price=10.00, stock=100, owner=self.user)

    def test_create_order(self):
        """
        Ensure we can create a new order.
        """
        url = reverse('order-list')
        data = {
            'total_price': 20.00,
            'order_items': [
                {'product': self.product.id, 'quantity': 2, 'price': 10.00},
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get().owner, self.user)

    def test_get_order(self):
        """
        Ensure we can retrieve an order.
        """
        order = Order.objects.create(owner=self.user, total_price=20.00, status='Pending')
        OrderItem.objects.create(order=order, product=self.product, quantity=2, price=10.00)
        url = reverse('order-detail', args=[order.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_price'], '20.00')

    def test_update_order_status(self):
        """
        Ensure we can update an order's status if it's not delivered or cancelled.
        """
        order = Order.objects.create(owner=self.user, total_price=20.00, status='Pending')
        url = reverse('order-detail', args=[order.id])
        data = {'status': 'Processing'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get().status, 'Processing')

        # Try updating a delivered order
        order.status = 'Delivered'
        order.save()
        response = self.client.patch(url, {'status': 'Cancelled'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_order(self):
        """
        Ensure we can cancel an order that is pending or processing.
        """
        order = Order.objects.create(owner=self.user, total_price=20.00, status='Pending')
        url = reverse('order-cancel', args=[order.id])
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get().status, 'Cancelled')

    def test_add_item_to_order(self):
        """
        Ensure we can add an item to an existing order.
        """
        order = Order.objects.create(owner=self.user, total_price=20.00, status='Pending')
        url = reverse('order-add-item', args=[order.id])
        data = {'product': self.product.id, 'quantity': 1, 'price': 10.00}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 1)

class OrderItemTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Create a test product
        self.product = Product.objects.create(name='Test Product', price=10.00, stock=100, owner=self.user)

        # Create a test order
        self.order = Order.objects.create(owner=self.user, total_price=10.00, status='Pending')

    def test_create_order_item(self):
        """
        Ensure we can create a new order item.
        """
        url = reverse('orderitem-list')
        data = {'order': self.order.id, 'product': self.product.id, 'quantity': 1, 'price': 10.00}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(OrderItem.objects.get().product, self.product)

    def test_get_order_item(self):
        """
        Ensure we can retrieve an order item.
        """
        order_item = OrderItem.objects.create(order=self.order, product=self.product, quantity=1, price=10.00)
        url = reverse('orderitem-detail', args=[order_item.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 1)
