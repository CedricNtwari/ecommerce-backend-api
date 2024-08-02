from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review instances.

    This serializer provides a detailed view of review information, including 
    the owner, rating, comment, and natural time representation of the creation 
    and update timestamps. It formats the created and updated timestamps in a 
    human-readable format using Django's `naturaltime`.
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    
    def get_created_at(self, obj):
        """
        Get the natural time representation of the created_at timestamp.

        Args:
            obj (Review): The review instance.

        Returns:
            str: Human-readable representation of the created_at timestamp.
        """
        return naturaltime(obj.created_at)

    def get_updated_at(self, obj):
        """
        Get the natural time representation of the updated_at timestamp.

        Args:
            obj (Review): The review instance.

        Returns:
            str: Human-readable representation of the updated_at timestamp.
        """
        return naturaltime(obj.updated_at)
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'owner', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']
