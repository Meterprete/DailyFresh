from django.urls import path
from apps.user import views

urlpatterns = [
    path('register', views.Register.as_view(), name='register'),
    path('active/<str:info>', views.User_Active.as_view(), name='active'),
    path('login', views.Longin.as_view(), name='login'),
]
