"""DailyFresh URL Configuration
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin', admin.site.urls),
    path('tinymce', include('tinymce.urls')),
    path('user/', include(('apps.user.urls', 'user'), namespace='user')),
    path('order/', include(('apps.cart.urls', 'order'), namespace='order')),
    path('cart/', include(('apps.order.urls', 'cart'), namespace='cart')),
    path('', include(('apps.goods.urls', 'goods'), namespace='goods')),
]
