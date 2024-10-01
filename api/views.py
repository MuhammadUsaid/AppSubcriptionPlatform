from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)

@api_view(['POST'])
def login(request):
    if 'username' not in request.data:
        return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
    if 'password' not in request.data:
        return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        # Delete the user's token
        request.auth.delete()
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    if 'old_password' not in request.data:
        return Response({"error": "Old password is required"}, status=status.HTTP_400_BAD_REQUEST)
    if 'new_password' not in request.data:
        return Response({"error": "New password is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    old_password = request.data['old_password']
    new_password = request.data['new_password']
    
    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    # Invalidate old token and create a new one
    Token.objects.filter(user=user).delete()
    new_token = Token.objects.create(user=user)
    
    return Response({
        "message": "Password successfully changed",
        "new_token": new_token.key
    }, status=status.HTTP_200_OK)
