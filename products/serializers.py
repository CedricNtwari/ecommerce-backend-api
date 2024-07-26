from rest_framework import serializers
from .models import Product
from profiles.models import Profile

class ProductSerializer(serializers.ModelSerializer):
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

    def validate_image(self, value):
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('Image size larger than 2MB!')
        if value.image.height > 4096:
            raise serializers.ValidationError('Image height larger than 4096px!')
        if value.image.width > 4096:
            raise serializers.ValidationError('Image width larger than 4096px!')
        return value

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner if request else False

    def get_phone_number(self, obj):
        # Convert the phone number to a string
        return str(obj.owner.profile.phone_number)
    
    def get_country(self, obj):
        # Convert the country object to a string
        return obj.owner.profile.country.name if obj.owner.profile.country else None

    class Meta:
        model = Product
        fields = [
            'id', 'owner', 'is_owner', 'profile_id', 'profile_image',
            'created_at', 'updated_at', 'name', 'description', 'price',
            'stock', 'image', 'image_filter', 'street_address', 'city', 
            'state', 'postal_code', 'country', 'phone_number'
        ]
