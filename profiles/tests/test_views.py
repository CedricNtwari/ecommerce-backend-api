from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from profiles.models import Profile

class ProfileDetailTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.profile = Profile.objects.get(owner=self.user)
        self.client = APIClient()
        self.client.login(username='testuser', password='12345')

    def test_retrieve_profile(self):
        """
        Ensure we can retrieve a profile by ID.
        """
        response = self.client.get(f'/profiles/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.profile.name)

    def test_update_profile(self):
        """
        Ensure we can update a profile by ID.
        """
        response = self.client.put(f'/profiles/{self.profile.id}/', {'name': 'Updated Name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'Updated Name')

    def test_delete_profile(self):
        """
        Ensure we can delete a profile by ID.
        """
        response = self.client.delete(f'/profiles/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profile.objects.count(), 0)
