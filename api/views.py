from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth.models import User
from .serializers import UserSerializer, AppSerializer, SubscriptionSerializer
from .models import App, Plan, Subscription
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, Http404

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
        return Response("error: username or password is wrong", status=status.HTTP_404_NOT_FOUND)
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

class AppListCreateView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        apps = App.objects.filter(user=request.user)
        serializer = AppSerializer(apps, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AppSerializer(data=request.data)
        if serializer.is_valid():
            app = serializer.save(user=request.user)
            
            # Automatically subscribe to free plan
            try:
                free_plan = Plan.objects.get(name='FREE')
            except Plan.DoesNotExist:
                # If the FREE plan doesn't exist, create it
                free_plan = Plan.objects.create(name='FREE')
            
            # Create the subscription for the new app
            Subscription.objects.create(app=app, plan=free_plan)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AppDetailView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return App.objects.get(pk=pk, user=user)
        except App.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        print(request.user)
        app = self.get_object(pk, request.user)
        serializer = AppSerializer(app)
        return Response(serializer.data)

    def put(self, request, pk):
        app = self.get_object(pk, request.user)
        serializer = AppSerializer(app, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        app = self.get_object(pk, request.user)
        app.delete()        
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class SubscriptionUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    
    def put(self, request, pk):
        try:
            app = App.objects.get(pk=pk, user=request.user)
        except App.DoesNotExist:
            return Response({'error': 'App not found'}, status=status.HTTP_404_NOT_FOUND)

        plan_name = request.data.get('plan')
        if not plan_name in ["STANDARD", "PRO", "FREE"]:
            return Response({'error': "Plan doesn't exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            plan = Plan.objects.get(name=plan_name)
        except Plan.DoesNotExist:
            plan = Plan.objects.create(name=plan_name)

        subscription, created = Subscription.objects.get_or_create(app=app)
        subscription.plan = plan
        subscription.active = True
        subscription.save()

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        try:
            app = App.objects.get(pk=pk, user=request.user)
        except App.DoesNotExist:
            return Response({'error': 'App not found'}, status=status.HTTP_404_NOT_FOUND)
        
        subscription = Subscription.objects.get(app=app)
        subscription.active = False
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)