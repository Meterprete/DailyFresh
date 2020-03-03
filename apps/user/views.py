from apps.user.models import User
from django.views import View
import re
from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from celery_task.tasks import send_active_email
from django.contrib.auth import authenticate, login


# 用户注册及邮件发送逻辑
class Register(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        '''进行数据注册处理'''
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': "数据不完整"})
        try:
            User.objects.get(username=username)
            return render(request, 'register.html', {'errmsg': "用户名已存在！！！"})
        except Exception as e:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return render(request, 'register.html', {'errmsg': "邮箱格式不正确"})
            if allow != 'on':
                return render(request, 'register.html', {'errmsg': '请同意协议'})

            # 注册并发送邮件
            send_active_email(email=email, username=username, password=password)
            # 返回应答
            return redirect(reverse('goods:index'))


# 用户激活的逻辑
class User_Active(View):
    def get(self, request, info):
        ser = Serializer(settings.SECRET_KEY, 300)
        try:
            sid = ser.loads(info)
        except SignatureExpired as e:
            return HttpResponse("邮件激活链接已失效，激活失败")
        user = User.objects.get(id=sid)
        user.is_active = True
        user.save()
        return redirect(reverse('user:login'))


# 用户登录的逻辑
class Longin(View):
    def get(self, request):
        username = request.COOKIES.get('username')
        if all([username]):
            return render(request, 'login.html', {'username': username, 'checked': 'checked'})
        return render(request, 'login.html')

    def post(self, request):
        # 接收到用户输入的数据，进行校验
        username = request.POST.get('username')
        password = request.POST.get("pwd")
        remember = request.POST.get("remember")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # 判断是否勾选了 “记住用户名”
                res = redirect(reverse("goods:index"))
                if remember == 'on':
                    res.set_cookie('username', value=username)
                else:
                    res.delete_cookie('username')
                return res
            else:
                return render(request, 'login.html', {'errmsg': "请先激活用户后登录！！！"})
        else:
            return render(request, 'login.html', {'errmsg': "用户名或密码错误！！！"})
