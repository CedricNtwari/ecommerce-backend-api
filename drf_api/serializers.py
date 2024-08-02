from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

class CurrentUserSerializer(UserDetailsSerializer):
    """
    Serializer for the current user details, extending the default UserDetailsSerializer.
    
    Adds additional fields to the user details to include profile-specific information:
    - 'profile_id': The ID of the associated profile.
    - 'profile_image': The URL of the profile image.

    These fields provide a richer set of user data ideal for client-side applications requiring user profiles and images.
    """
    profile_id = serializers.ReadOnlyField(source='profile.id')
    profile_image = serializers.ReadOnlyField(source='profile.image.url')

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('profile_id', 'profile_image')
