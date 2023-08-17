from django.contrib.auth import authenticate, login, logout
from rest_framework import generics, permissions, status, views
from drf_spectacular.utils import extend_schema

from users.serializers import *
from utils.serializers import EmptySerializer


@extend_schema(
    tags=['Users'],
    description='Register a new user. The new user will be logged in, and information about them returned.',
    responses=UserResponseSerializer
)
class RegisterView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterRequestSerializer

    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        self.perform_create(request_serializer)
        user = request_serializer.instance
        login(request, user)
        response_serializer = UserResponseSerializer(user)
        headers = self.get_success_headers(response_serializer.data)
        return views.Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    tags=['Users'],
    description='Log in with username and password. Information about the user will be returned.',
    responses=UserResponseSerializer
)
class LoginView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginRequestSerializer

    def create(self, request, *args, **kwargs):
        user = authenticate(request, username=request.data.get('username'), password=request.data.get('password'))
        if user is not None:
            login(request, user)
            response_serializer = UserResponseSerializer(user)
            headers = self.get_success_headers(response_serializer.data)
            return views.Response(response_serializer.data, status=status.HTTP_200_OK, headers=headers)
        raise serializers.ValidationError('Invalid credentials')


@extend_schema(
    tags=['Users'],
    description='Log out the user'
)
class LogoutView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmptySerializer

    def post(self, request, *args, **kwargs):
        logout(request)
        return views.Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Users'],
    description='Get information about the current user',
    responses=UserResponseSerializer
)
class WhoAmiIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserResponseSerializer(request.user)
        return views.Response(serializer.data)
    