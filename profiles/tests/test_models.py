from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import Profile

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
        profile.street_address = 'New Street'
        profile.city = 'New City'
        profile.state = 'New State'
        profile.postal_code = '12345'
        profile.country = 'CH'
        profile.phone_number = '+41764567890'
        profile.content = 'New Content'
        profile.save()
        self.assertEqual(Profile.objects.first().name, 'New Name')
        self.assertEqual(Profile.objects.first().street_address, 'New Street')
        self.assertEqual(Profile.objects.first().city, 'New City')
        self.assertEqual(Profile.objects.first().state, 'New State')
        self.assertEqual(Profile.objects.first().postal_code, '12345')
        self.assertEqual(Profile.objects.first().country.code, 'CH')
        self.assertEqual(Profile.objects.first().phone_number.as_e164, '+41764567890')
        self.assertEqual(Profile.objects.first().content, 'New Content')

    def test_profile_default_image(self):
        """
        Test the default image value.
        """
        profile = Profile.objects.first()
        self.assertEqual(profile.image.name.split('/')[-1], 'default_profile_xffzir')
