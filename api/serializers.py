from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Plan, App, Subscription

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'password', 'email']

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price']

class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'active', 'start_date', 'end_date']

class AppSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = App
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'subscription']
        read_only_fields = ['user', 'created_at', 'updated_at']
