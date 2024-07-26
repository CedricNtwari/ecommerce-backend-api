from rest_framework import serializers
from phonenumbers import parse, is_valid_number, NumberParseException
from .models import Profile
from django_countries.serializer_fields import CountryField  # Import CountryField

EU_COUNTRY_CODES = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", 
    "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", 
    "SI", "ES", "SE"
]

class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    country = CountryField()

    class Meta:
        model = Profile
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'name', 'street_address', 'city', 
            'state', 'postal_code', 'country', 'phone_number', 'content', 'image', 'is_owner'
        ]
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request.user == obj.owner if request else False

    def validate_phone_number(self, value):
        for country_code in EU_COUNTRY_CODES:
            try:
                phone_number = parse(value, country_code)
                if is_valid_number(phone_number):
                    return value
            except NumberParseException:
                continue
        raise serializers.ValidationError("The phone number is not valid for any of the EU countries.")
