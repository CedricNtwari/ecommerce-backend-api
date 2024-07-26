from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from profiles.models import Profile

class ProfileDetailTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user2 = User.objects.create_user(username='otheruser', password='12345')
        self.profile = Profile.objects.get(owner=self.user)
        self.client = APIClient()

    def test_retrieve_profile(self):
        """
        Ensure we can retrieve a profile by ID.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.get(f'/profiles/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.profile.name)
        self.assertTrue(response.data['is_owner'])

    def test_update_profile(self):
        """
        Ensure the owner can update their profile by ID.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.put(f'/profiles/{self.profile.id}/', {'name': 'Updated Name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.name, 'Updated Name')

    def test_update_profile_not_owner(self):
        """
        Ensure a user cannot update another user's profile.
        """
        self.client.login(username='otheruser', password='12345')
        response = self.client.put(f'/profiles/{self.profile.id}/', {'name': 'Updated Name'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_profile(self):
        """
        Ensure the owner can delete their profile by ID.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.delete(f'/profiles/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Profile.objects.filter(pk=self.profile.id).exists())

    def test_delete_profile_not_owner(self):
        """
        Ensure a user cannot delete another user's profile.
        """
        self.client.login(username='otheruser', password='12345')
        response = self.client.delete(f'/profiles/{self.profile.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Profile.objects.filter(pk=self.profile.id).exists())
