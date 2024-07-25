from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile

class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_profile_creation(self):
        """
        Test that a Profile instance is created when a new User is created.
        """
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.first().owner, self.user)

    def test_profile_str_method(self):
        """
        Test the __str__ method of the Profile model.
        """
        profile = Profile.objects.first()
        self.assertEqual(str(profile), f"{self.user}'s profile")

    def test_profile_update(self):
        """
        Test that the profile can be updated.
        """
        profile = Profile.objects.first()
        profile.name = 'New Name'
        profile.save()
        self.assertEqual(Profile.objects.first().name, 'New Name')

    def test_profile_default_image(self):
        """
        Test the default image value.
        """
        profile = Profile.objects.first()
        self.assertEqual(profile.image.name.split('/')[-1], 'default_profile_xffzir')
