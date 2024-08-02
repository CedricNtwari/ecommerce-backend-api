from rest_framework import serializers
from .models import Product
from reviews.models import Review
from django.db.models import Avg

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product instances.

    This serializer provides detailed information about products, including owner
    details, location, and review statistics. It includes various read-only fields
    to display related user profile information and computed fields for reviews.
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    street_address = serializers.ReadOnlyField(source='owner.profile.street_address')
    city = serializers.ReadOnlyField(source='owner.profile.city')
    state = serializers.ReadOnlyField(source='owner.profile.state')
    postal_code = serializers.ReadOnlyField(source='owner.profile.postal_code')
    country = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    def validate_image(self, value):
        """
        Validate the image field to ensure the file size and dimensions are within acceptable limits.

        Raises:
            ValidationError: If the image exceeds the size or dimension constraints.
        """
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('Image size larger than 2MB!')
        if value.image.height > 4096:
            raise serializers.ValidationError('Image height larger than 4096px!')
        if value.image.width > 4096:
            raise serializers.ValidationError('Image width larger than 4096px!')
        return value

    def get_is_owner(self, obj):
        """
        Determine if the request user is the owner of the product.

        Returns:
            bool: True if the request user is the owner, otherwise False.
        """
        request = self.context['request']
        return request.user == obj.owner if request else False

    def get_phone_number(self, obj):
        """
        Retrieve the phone number from the owner's profile.

        Returns:
            str: The owner's phone number as a string.
        """
        return str(obj.owner.profile.phone_number)
    
    def get_country(self, obj):
        """
        Retrieve the country name from the owner's profile.

        Returns:
            str: The name of the owner's country or None if not set.
        """
        return obj.owner.profile.country.name if obj.owner.profile.country else None

    def get_review_count(self, obj):
        """
        Calculate the total number of reviews for the product.

        Returns:
            int: The count of reviews associated with the product.
        """
        return obj.reviews.count()

    def get_average_rating(self, obj):
        """
        Calculate the average rating of the product based on its reviews.

        Returns:
            float: The average rating of the product, or 0 if there are no reviews.
        """
        return obj.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    class Meta:
        model = Product
        fields = [
            'id', 'owner', 'is_owner', 'profile_id', 'profile_image',
            'created_at', 'updated_at', 'name', 'description', 'price',
            'stock', 'image', 'image_filter', 'street_address', 'city', 
            'state', 'postal_code', 'country', 'phone_number',
            'review_count', 'average_rating'
        ]
