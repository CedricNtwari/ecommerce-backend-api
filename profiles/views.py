from rest_framework import generics
from .models import Profile
from .serializers import ProfileSerializer
from drf_api.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class ProfileList(generics.ListAPIView):
    """
    API view to retrieve a list of all profiles.

    This view allows any user to retrieve a list of all profiles in the system.
    The permission class `IsAuthenticatedOrReadOnly` ensures that both authenticated
    and unauthenticated users can read the data, but modifications are restricted.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a profile instance.

    This view provides detailed operations on a single profile instance. Only
    the owner of the profile has permissions to update or delete it, enforced
    by the `IsOwnerOrReadOnly` permission class.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
