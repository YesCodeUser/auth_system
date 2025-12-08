from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, UserUpdateSerializer
from .models import User
from .permissions import CanViewSelf, CanEditSelf, CanDeleteSelf


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
                if user.is_deleted:
                    return Response({'error': 'user is not available'})
                if not user.is_active:
                    return Response({'error': 'user is not available'})
                if not user.check_password(password):
                    return Response({'error': 'invalid email or password'})
                else:
                    refresh = RefreshToken.for_user(user)
                    access = refresh.access_token
                    return Response({'refresh': str(refresh), 'access': str(access)})

            except User.DoesNotExist:
                return Response({'error': 'user is not available'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_string = request.data.get('refresh')
        if token_string:
            try:
                token_object = RefreshToken(token_string)
                token_object.blacklist()
                return Response('Successfully logged out', status=status.HTTP_200_OK)

            except InvalidToken:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'token is not exists'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    permission_classes = [IsAuthenticated, CanViewSelf]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class EditView(APIView):
    permission_classes = [IsAuthenticated, CanEditSelf]

    def patch(self, request):
        serializer = UserUpdateSerializer(instance=request.user ,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated, CanDeleteSelf]

    def delete(self, request):
        request.user.soft_delete()
        token_string = request.data.get('refresh')
        if token_string:
            try:
                token_object = RefreshToken(token_string)
                token_object.blacklist()
                return Response(status=status.HTTP_204_NO_CONTENT)

            except InvalidToken:
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)