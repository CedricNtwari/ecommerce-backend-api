from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    

    def get_created_at(self, obj):
        return naturaltime(obj.created_at)

    def get_updated_at(self, obj):
        return naturaltime(obj.updated_at)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'owner', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']
