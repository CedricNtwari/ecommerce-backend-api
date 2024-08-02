from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Review
from .serializers import ReviewSerializer
from drf_api.permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Review instances.

    This viewset provides actions to list, create, retrieve, update, and delete reviews.
    It enforces permissions to ensure that only authenticated users can interact with reviews
    and only the owner of a review can modify or delete it. Additionally, it prevents users 
    from reviewing the same product more than once.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        """
        Create a new review for a product.

        This method checks if the user has already reviewed the product and raises a 
        ValidationError if a review already exists. Otherwise, it saves the new review 
        with the current user as the owner.

        Args:
            serializer (ReviewSerializer): The serializer instance containing the validated data.
        
        Raises:
            ValidationError: If the user has already reviewed the product.
        """
        if Review.objects.filter(product=serializer.validated_data['product'], owner=self.request.user).exists():
            raise ValidationError("You have already reviewed this product.")
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        Update an existing review instance.

        This method ensures that only the owner of the review can update it, raising a 
        ValidationError if the current user is not the owner.

        Args:
            serializer (ReviewSerializer): The serializer instance containing the validated data.
        
        Raises:
            ValidationError: If the user is not the owner of the review.
        """
        if self.get_object().owner != self.request.user:
            raise ValidationError("You do not have permission to edit this review.")
        serializer.save()
