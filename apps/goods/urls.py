from django.urls import path
from apps.goods import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index')
]
