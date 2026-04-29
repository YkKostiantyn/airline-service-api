from rest_framework.viewsets import ModelViewSet
from .models import User
from .serializers import UserSerializer, CreateUserSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from .permissions import IsAdminRole, IsSelfOrAdmin

# Create your views here.

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action == "list":
            return [IsAdminRole()]
        return [IsSelfOrAdmin()]
