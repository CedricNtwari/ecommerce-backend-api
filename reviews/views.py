from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Review
from .serializers import ReviewSerializer
from drf_api.permissions import IsOwnerOrReadOnly

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        if Review.objects.filter(product=serializer.validated_data['product'], owner=self.request.user).exists():
            raise ValidationError("You have already reviewed this product.")
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        # Ensure the review owner is the one updating
        if self.get_object().owner != self.request.user:
            raise ValidationError("You do not have permission to edit this review.")
        serializer.save()
