from django.db import models
from django.contrib.auth.models import User

class App(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apps')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Plan(models.Model):
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('STANDARD', 'Standard'),
        ('PRO', 'Pro'),
    ]
    name = models.CharField(max_length=50, choices=PLAN_CHOICES)
    planPrices = { 'FREE': 0, 'STANDARD': 10, 'PRO': 25}
    @property
    def price(self):
        return self.planPrices[self.name]

    def __str__(self):
        return f"{self.name} (${self.price})"
    
class Subscription(models.Model):
    app = models.OneToOneField(App, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.app.name} - {self.plan.name}"