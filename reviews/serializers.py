from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'owner', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']
