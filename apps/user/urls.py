from django.urls import path
from apps.user import views

urlpatterns = [
    path('register', views.Register.as_view(), name='register'),  # 用户注册视图
    path('active/<str:info>', views.User_Active.as_view(), name='active'),  # 用户激活视图
    path('login', views.Longin.as_view(), name='login'),  # 用户登录视图
    path('user', views.User_center_info.as_view(), name='user'),  # 用户中心——信息页
    path('order', views.User_center_order.as_view(), name='order'),  # 用户中心——订单页
    path('address', views.User_center_site.as_view(), name='address'),  # 用户中心——地址页

]
