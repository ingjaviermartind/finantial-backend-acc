
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from Backend.serializers import CustomTokenObtainPairSerializer, ChangePasswordSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]
        if not user.check_password(current_password):
            return Response(
                {
                    "detail": "La contraseña actual es incorrecta."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.check_password(new_password):
            return Response(
                {
                    "detail": "La nueva contraseña debe ser diferente a la actual."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {
                    "detail": e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response(
            {
                "detail": "Contraseña actualizada correctamente."
            }
        )