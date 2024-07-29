from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Product
from profiles.models import Profile
from reviews.models import Review
from django.core.files.uploadedfile import SimpleUploadedFile

class ProductTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user2 = User.objects.create_user(username='otheruser', password='12345')
        
        self.profile = Profile.objects.get(owner=self.user)
        self.profile.street_address = 'Test Street'
        self.profile.city = 'Test City'
        self.profile.state = 'Test State'
        self.profile.postal_code = '12345'
        self.profile.country = 'CH'
        self.profile.phone_number = '+41764567890'
        self.profile.save()

        self.profile2 = Profile.objects.get(owner=self.user2)
        self.profile2.street_address = 'Other Street'
        self.profile2.city = 'Other City'
        self.profile2.state = 'Other State'
        self.profile2.postal_code = '54321'
        self.profile2.country = 'CH'
        self.profile2.phone_number = '+41764567891'
        self.profile2.save()

        self.product = Product.objects.create(
            owner=self.user,
            name='Test Product',
            description='Test Description',
            price=100.00,
            stock=10,
            image=SimpleUploadedFile(
                name='test_image.jpg',
                content=open('products/test_image.jpg', 'rb').read(),
                content_type='image/jpeg'
            )
        )
        self.review = Review.objects.create(
            product=self.product,
            owner=self.user,
            rating=5,
            comment='Great product!'
        )
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=open('products/test_image.jpg', 'rb').read(),
            content_type='image/jpeg'
        )

    def test_create_product(self):
        self.client.login(username='testuser', password='12345')
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 150.00,
            'stock': 5,
            'image': self.image
        }
        response = self.client.post('/products/', data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)  # Print error details
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_product(self):
        response = self.client.get(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)
        self.assertEqual(response.data['street_address'], self.profile.street_address)
        self.assertEqual(response.data['city'], self.profile.city)
        self.assertEqual(response.data['state'], self.profile.state)
        self.assertEqual(response.data['postal_code'], self.profile.postal_code)
        self.assertEqual(response.data['country'], 'Switzerland')  # Ensure we match the expected string
        self.assertEqual(response.data['phone_number'], str(self.profile.phone_number))
        self.assertEqual(response.data['review_count'], 1)
        self.assertEqual(response.data['average_rating'], 5.0)

    def test_update_product(self):
        self.client.login(username='testuser', password='12345')
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': 120.00,
            'stock': 8,
            'image': self.image
        }
        response = self.client.put(f'/products/{self.product.id}/', data, format='multipart')
        if response.status_code != status.HTTP_200_OK:
            print(response.data)  # Print error details
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product')

    def test_delete_product(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.delete(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_unauthenticated_user_cannot_create_product(self):
        data = {
            'name': 'New Product',
            'description': 'New Description',
            'price': 150.00,
            'stock': 5,
            'image': self.image
        }
        response = self.client.post('/products/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_update_product(self):
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': 120.00,
            'stock': 8,
            'image': self.image
        }
        response = self.client.put(f'/products/{self.product.id}/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_product(self):
        response = self.client.delete(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_update_another_users_product(self):
        self.client.login(username='otheruser', password='12345')
        data = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': 120.00,
            'stock': 8,
            'image': self.image
        }
        response = self.client.put(f'/products/{self.product.id}/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_delete_another_users_product(self):
        self.client.login(username='otheruser', password='12345')
        response = self.client.delete(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_products(self):
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_product_creation_validation_error(self):
        self.client.login(username='testuser', password='12345')
        data = {
            'name': '',
            'description': 'New Description',
            'price': 150.00,
            'stock': 5,
            'image': self.image
        }
        response = self.client.post('/products/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
