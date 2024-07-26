from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=False)  # Ensuring the address is not empty
    phone_number = PhoneNumberField(blank=True, region="US")  # Using django-phonenumber-field
    content = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='images/', default='../default_profile_xffzir'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.owner}'s profile"
