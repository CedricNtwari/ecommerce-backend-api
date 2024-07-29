from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Review
from products.models import Product

class ReviewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.other_user = User.objects.create_user(username='otheruser', password='testpassword')
        self.product = Product.objects.create(
            owner=self.user,
            name='Test Product',
            description='Test Description',
            price='10.00',
            stock=100
        )
        self.review = Review.objects.create(
            product=self.product,
            owner=self.user,
            rating=5,
            comment='Great product!'
        )

    def test_create_review(self):
        self.client.login(username='otheruser', password='testpassword')
        review_data = {
            'product': self.product.id,
            'rating': 4,
            'comment': 'Good product!'
        }
        response = self.client.post('/reviews/', review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        review = Review.objects.get(id=response.data['id'])
        self.assertEqual(review.owner, self.other_user)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'Good product!')

    def test_create_duplicate_review(self):
        self.client.login(username='testuser', password='testpassword')
        review_data = {
            'product': self.product.id,
            'rating': 4,
            'comment': 'Another comment'
        }
        response = self.client.post('/reviews/', review_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You have already reviewed this product.', str(response.data))

    def test_retrieve_review(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Great product!')

    def test_update_review(self):
        self.client.login(username='testuser', password='testpassword')
        update_data = {'product': self.product.id, 'rating': 4, 'comment': 'Updated comment'}
        response = self.client.put(f'/reviews/{self.review.id}/', update_data, format='json')
        print("cece:", response.data)  # Debugging line to print response content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, 'Updated comment')


    def test_update_review_not_owner(self):
        self.client.login(username='otheruser', password='testpassword')
        update_data = {'rating': 4, 'comment': 'Updated comment'}
        response = self.client.put(f'/reviews/{self.review.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.delete(f'/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_not_owner(self):
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.delete(f'/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())
