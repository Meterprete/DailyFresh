from celery import Celery
from django.core.mail import send_mail
import django
from django.template import loader
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DailyFresh.settings')
django.setup()
from django.conf import settings
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner
from django_redis import get_redis_connection

# 创建一个celery类的实例
app = Celery("celery_task.tasks", broker="redis://127.0.0.1:6379/8")

from apps.user.models import User


# 定义任务视图
@app.task
def send_active_email(email, username, password):
    # 进行业务处理，用户注册
    user = User.objects.create_user(username=username, password=password, email=email)
    user.is_active = False
    user.save()
    # 加密用户信息
    ser = Serializer(settings.SECRET_KEY, 300)
    seid = ser.dumps(user.id)
    seid = seid.decode()
    info = "http://39.105.92.190:80/user/active/{}".format(seid)
    subject = "天天生鲜会员用户激活邮件"
    message = ""
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [email]
    html_message = '''<div style="width: 400px;margin: auto">
        <h2>尊敬的用户 {}：</h2>请您在<span style="color: red;font-weight: bolder">确保为本人操作</span>的情况下，点击 <span
            style="color: red;font-weight: bolder">以下链接</span>
        进行<span style="color: red;font-weight: bolder">会员用户激活</span><br>
        凡是未激活的用户一律视为<span style="color: red;font-weight: bolder">非法用户</span>，不给予登陆权限:<br><br>
        <span style="color: green;font-weight: bolder;font-size: 20px">本邮箱激活链接为：</span><br>
        <a href="{}">{}</a><br><br><span style="color: red;
                font-weight: bolder;font-size: 15px">过期时间：5分钟，请在正确时间内激活</span></div>'''.format(username, info, info)
    send_mail(subject, message, from_email, to_email, html_message=html_message)


@app.task
def static_index_html():
    '''商品种类'''
    goods_type = GoodsType.objects.all()
    '''轮播图展示'''
    index_goods_banner = IndexGoodsBanner.objects.all().order_by('index')
    '''促销图展示'''
    index_promotion_banner = IndexPromotionBanner.objects.all().order_by('index')
    '''获取首页商品展示信息'''
    for type in goods_type:
        type.image_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        type.title_banner = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
    context = {
        'types': goods_type,
        'goods_banners': index_goods_banner,
        'promotion_banners': index_promotion_banner,
    }
    # 加载模板文件，返回模板对象
    temp = loader.get_template('static_index.html')
    # 模板渲染
    st_index_html = temp.render(context)
    # 生成模板对应的静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    print(save_path)
    with open(save_path, 'w') as f:
        print("静态文件生成")
        f.write(st_index_html)
