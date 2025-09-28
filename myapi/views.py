from django.shortcuts import render
from .models import Customer , Account , Transaction
from .serializers import RegisterSerializer , loginSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions as permission


class RegisterView(APIView):
    permission_classes = [permission.AllowAny]
    def post(self , request):
        serializers = RegisterSerializer(data = request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()

        

        refresh = RefreshToken.for_user(request.user)
        access_token = refresh.access_token


        return Response({
            "message": "User registered successfully",
            "refresh": str(refresh),
            "access": str(access_token)
        })


class LoginView(APIView):
    permission_classes = [permission.AllowAny]
    def post(self , request):
        serializers = loginSerializer(data = request.data)
        serializers.is_valid(raise_exception=True)
        user = serializers.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            "message": "Login successful",
            "refresh": str(refresh),
            "access": str(access_token)
        })