from django.shortcuts import render
from .models import Customer , Account , Transaction
from .serializers import RegisterSerializer , loginSerializer , TransctionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions as permission
from .permission import TransactionPermission , IsUthenticated
from django.db.models import Q


class RegisterView(APIView):
    permission_classes = [permission.AllowAny]
    def post(self , request):
        serializers = RegisterSerializer(data = request.data)
        serializers.is_valid(raise_exception=True)
        user = serializers.save()

        

        refresh = RefreshToken.for_user(request.user)
        access_token = refresh.access_token


        return Response({
            "message": "User registered successfully",
            "user":{
                "id": user.id,
                "username": user.username,
            },
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
    

class TransactionView(APIView):
    permission_classes = [TransactionPermission , IsUthenticated]

    """View to handle transactions."""
    def post(self , request):
        serializer = TransctionSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Transaction created successfully" , "data": serializer.data})
    
    def get(self , request):
        # Retrieve transactions where the user is either the sender or receiver
       transctions = transactions = Transaction.objects.filter(
           Q(from_account__customer__user=request.user) | Q(to_account__customer__user=request.user)
       )


       #get a JSON array of all the user’s transactions that you can send back in the API response.
       serializer = TransctionSerializer(transctions , many=True)
       return Response(serializer.data)


    