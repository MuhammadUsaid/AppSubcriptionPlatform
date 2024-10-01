from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup),
    path('login', views.login),
    path('logout', views.logout),
    path('change_pass', views.change_password),
    path('app/', views.AppListCreateView.as_view()),
    path('app/<int:pk>/', views.AppDetailView.as_view()),
    path('app/sub/<int:pk>/', views.SubscriptionUpdateView.as_view())
]