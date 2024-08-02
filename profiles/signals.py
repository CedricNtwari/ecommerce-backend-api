from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Profile

def create_profile(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a Profile instance whenever a new User is created.

    This function listens to the `post_save` signal of the User model. When a new user 
    instance is created, it automatically creates an associated Profile instance with 
    the user as the owner.

    Args:
        sender (Model): The model class sending the signal (User).
        instance (User): The instance of the model being saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        Profile.objects.create(owner=instance)

post_save.connect(create_profile, sender=User)
