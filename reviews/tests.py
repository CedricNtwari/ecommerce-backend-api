from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Review
from products.models import Product

class ReviewTestCase(APITestCase):
    """
    Test suite for the Review model and its API endpoints.

    This test suite includes tests for creating, retrieving, updating, and deleting reviews.
    It also verifies permission constraints to ensure only authorized users can perform certain actions.
    """

    def setUp(self):
        """
        Set up test data for the test suite.

        Creates test users, a test product, and a test review. The review is associated with the test user
        and product to facilitate testing of CRUD operations and permissions.
        """
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
        """
        Test that a user can create a review for a product.

        Verifies that a new review is successfully created when valid data is provided by an authenticated user.
        """
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
        """
        Test that a user cannot create a duplicate review for the same product.

        Verifies that a ValidationError is raised when a user attempts to review a product they have already reviewed.
        """
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
        """
        Test that a user can retrieve a review by its ID.

        Verifies that the review data is correctly returned for an authenticated user.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(f'/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Great product!')

    def test_update_review(self):
        """
        Test that the owner of a review can update it.

        Verifies that a review is successfully updated when the owner provides valid data.
        """
        self.client.login(username='testuser', password='testpassword')
        update_data = {'product': self.product.id, 'rating': 4, 'comment': 'Updated comment'}
        response = self.client.put(f'/reviews/{self.review.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, 'Updated comment')

    def test_update_review_not_owner(self):
        """
        Test that a user cannot update a review they do not own.

        Verifies that a 403 Forbidden status is returned when a non-owner attempts to update a review.
        """
        self.client.login(username='otheruser', password='testpassword')
        update_data = {'rating': 4, 'comment': 'Updated comment'}
        response = self.client.put(f'/reviews/{self.review.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review(self):
        """
        Test that the owner of a review can delete it.

        Verifies that a review is successfully deleted when the owner requests deletion.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.delete(f'/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    def test_delete_review_not_owner(self):
        """
        Test that a user cannot delete a review they do not own.

        Verifies that a 403 Forbidden status is returned when a non-owner attempts to delete a review.
        """
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.delete(f'/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())
