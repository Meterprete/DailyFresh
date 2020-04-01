### 环境：
 1. **Django == 2.2** 
```bash
pip install django==2.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```
 2. **django-tinymce**
```bash
pip install django-tinymce==2.6.0 -l https://pypi.tuna.tsinghua.edu.cn/simple
```
---
##### 富文本后台编辑器配置：
 3. **在settings.py中注册 tinymce**![在这里插入图片描述](https://img-blog.csdnimg.cn/20200302132014747.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
 4. **settings.py中富文本编辑框大小设置**
```python
'''富文本编辑器的大小配置'''
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'width': 600,
    'height': 400
}
```
 5. **配置富文本编辑器的url**![在这里插入图片描述](https://img-blog.csdnimg.cn/20200302170540967.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
##### 指定认证系统使用的模型类：
 6. **在settins.py中设置认证系统使用的模型类**
```python
# 指定认证系统使用的模型类
AUTH_USER_MODEL = 'apps.user.User'
```
---
---
---
---
### 实现步骤：
###### 【1】用户注册逻辑的实现:

> 需要注意的是，使用反向解析的时候导入的包的路径
> `from django.urls import reverse`

- 配置user.urls![在这里插入图片描述](https://img-blog.csdnimg.cn/20200302193134714.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
- user.views配置![在这里插入图片描述](https://img-blog.csdnimg.cn/20200302193246826.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
- goods.url配置![在这里插入图片描述](https://img-blog.csdnimg.cn/2020030217091034.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
###### 【2】celery发送邮件以及使用celery将用户信息写入数据库
- [配置redis树据库](https://blog.csdn.net/weixin_44449518/article/details/102466666)
- 在ubantu服务器上安装celery
```bash
pip install celery
或者
pip install celery -i https://pypi.tuna.tsinghua.edu.cn/simple
```
- 本地逻辑代码的实现，大体步骤如下所示
> 【1】在项目根目录下新建  “celery_task” 文件夹（或者python package）
> 【2】在 “celery_task” 中新建“tasks.py”文件，里面加入如下代码，初始化Django项目以及完成邮件发送任务。这里更改了原本注册视图，将注册逻辑添加到 “celery_task” 下面的 tasks.py 文件中（目的是加快页面跳转速度，把注册任务交给代理完成）
> ------------注意事项-----------
> 这里有两点需要注意，一个是需要安装`itsdangerous`这个库，进行用户必要信息的加密，`使用前需要导包`，第二个是，当使用它去解密一个已过期的数据的时候，会抛出一个异常，这个异常的抓取也需要导入`SignatureExpired`包
```python
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
import os
import django
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from apps.user.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DailyFresh.settings')
django.setup()

# 创建一个celery类的实例
app = Celery("celery_task.tasks", broker="redis://127.0.0.1:6379/8")


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
    info = "http://39.105.92.190:81/user/active/{}".format(seid)
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
```
> 【3】在settings.py中添加如下代码，完成对内置邮件发送系统的配置

```python
# 电子邮件相关
# 这里开启ssl加密，因为全部服务器的默认的25端口被阿里云封闭了，不得不改为465端口
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ''				  # 你的邮箱
EMAIL_HOST_PASSWORD = ''			  # 邮箱的申请
DEFAULT_FROM_EMAIL = '天天生鲜项目组<>' # 邮箱授权码
EMAIL_USE_SSL = True
```
> 剩下的部分（收到激活请求，进行用户id解密，把用户i设置为激活状态，以及**celery的启动**），这里就直接放上图片了，比较简单

 - [x] user/urls.py配置
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200303165815110.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
 - [x] user/views.py配置![在这里插入图片描述](https://img-blog.csdnimg.cn/20200303170111273.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
 - [x] celery的启动
```powershell
celery -A celery_task.tasks worker -l info
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200303170510256.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
###### 【3】使用redis存储session以及用户登录逻辑

-  【1】user/urls.py中基本用户登录逻辑的实现（如下图所示）

> 需要注意的是，这里用了Django内置的认证系统，所以密码的验证不可以用平常思路去验证。需要用Django内置的方法`authenticate()`认证，以及使用内置的 `login()`方法在树据库中记录用户登录的session信息，`使用前需要导包`

```python
from django.contrib.auth import authenticate, login

user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # 判断是否勾选了 “记住用户名”
                res = redirect(next)
                if remember == 'on':
                    res.set_cookie('username', value=username)
                else:
                    res.delete_cookie('username')
                return res
            else:
                return render(request, 'login.html', {'errmsg': "请先激活用户后登录！！！"})
        else:
            return render(request, 'login.html', {'errmsg': "用户名或密码错误！！！"})
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200303230012539.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
- 【2】安装 django-redis包，并在 settings.py 中进行配置

```python
# 【1】进行 djang-redis 的安装
pip install django-redis -i https://pypi.tuna.tsinghua.edu.cn/simple

# 【2】在settings.py中进行如下配置
# session缓存设置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # redis的地址
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            # 密码
            # "PASSWORD": "135089293",
        }
    }
}
# 配置session存储
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```
效果如图所示：![在这里插入图片描述](https://img-blog.csdnimg.cn/20200303230535352.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
- 【3】最后，就可以进行登陆测试，用户登录之后的通过login()函数添加到session中的信息就可以在redis中查看了![在这里插入图片描述](https://img-blog.csdnimg.cn/2020030323080071.png)
###### 【4】is_authenticated以及`login_required`的使用
> 需要注意的是：
> 【1】传入前端模板的数据不仅有后端传入的数据，也有Django默认传入的数据（`request.user`），当`用户未登录`的时候，request.user默认为`AnonymousUser`类的实例，此时它的`is_authenticated`属性为`False`，当`用户已登录`时，request.user默认为`User`类的实例，此时它的`is_authenticated`属性为`True`，所以我们可以直接在模板中通过`user.is_authenticated`来判断用户是否登录来显示不同的内容
> 【2】我们可以借助 Django内置的一个装饰器` login_required`来指定用户未登录的时不可以访问某页面，并指定跳转到登录界面，登录以后根据地址栏的`next`参数跳转到指定页面。
> `使用前需在settings.py中指定跳转的页面`（使用方法如下，`介绍了两种`）

```python
# settings.py （设置未登录跳转的页面）
LOGIN_URL = "/user/login"

# 方法一：
# urls.py （导包，直接在类视图上装饰—————手动调用 login_required）
from django.contrib.auth.decorators import login_required
urlpatterns = [
	...
	...
	...
    path('user', login_required(views.User_center_info.as_view()), name='user'),  # 用户中心——信息页
    path('order', login_required(views.User_center_order.as_view()), name='order'),  # 用户中心——订单页
    path('address', login_required(views.User_center_site.as_view()), name='address'),  # 用户中心——地址页
]



# 方法二（使用LoginRequiredMixin）
# 在项目根目录下新建`utils`包，然后在其下面新建 mixin.py文件
# 在 mixin.py中添加以下内容
from django.contrib.auth.decorators import login_required

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类的as_view()
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)
        
# 在 `views.py`中直接导入 util.mixin包中的`LoginRequiredMixin`，让需要登陆后才显示的类视图继承这个类
from utils.mixin import LoginRequiredMixin

class User_center_info(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_info.html', {'page': 'user'})

class User_center_order(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_order.html', {'page': 'order'})
        
class User_center_site(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'user_center_site.html', {'page': 'address'})
```

> 上面加上`login_required`装饰器之后，还需再配置以下登录类视图，如下图所示。在之前基础上加了获取GET请求中的`next`参数，进行判断，如果没有参数就默认跳到首页。首页的表单`action地址不写，默认提交到地址栏的地址`

views.py中进行用户中心三个视图的编写，并对原本的登录视图做修改（红框标出改动部分）
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200304145848896.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
urls.py中配置用户中心三个页面![在这里插入图片描述](https://img-blog.csdnimg.cn/2020030415013376.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)mixin.py中配置login_required![在这里插入图片描述](https://img-blog.csdnimg.cn/20200304150255294.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
在父模板 base.py中使用`is_authenticated`完成用户信息和登录注册的显示与隐藏![在这里插入图片描述](https://img-blog.csdnimg.cn/20200304150613488.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
###### 【5】FastDFS和Nginx的安装及配置
[写到了《Ubantu下安装FastDFS和Nginx及其配置》
这篇博客里，点击链接查看](https://blog.csdn.net/weixin_44449518/article/details/104673669)
###### 【6】Django与FastDFS交互（相关配置）
> 首先需要独立出一个模块来:
> 在 `utils包`下新建`fdfs包`，然后再fdfs包下新建 `storage.py`文件，加入如下所示的代码

```python
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client


class FDFSStorage(Storage):
    '''fast dfs的存储类'''

    def _open(self, name, mode='rb'):
        '''打开文件时使用'''
        pass

    def _save(self, name, content):
        '''保存文件时使用'''
        # 创建一个Fast_client对象
        client = Fdfs_client('./utils/fdfs/client.conf')

        # 上传文件到fast dfs系统中
        res = client.upload_by_buffer(content.read())
        if res.get('Status') != 'Upload successed.':
            raise Exception("上传文件到 Fast_DFS 失败！")
        # 返回文件ID
        filename = res.get('Remote file_id')
        return filename

    def exists(self, name):
        '''Django判断文件是否可用'''
        return False

    def url(self, name):
        '''返回访问文件的url'''
        return 'http://39.105.92.190:8888' + name

```

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200306141158722.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
> 然后，拷贝在[**《Ubantu下安装FastDFS和Nginx及其配置》**](https://blog.csdn.net/weixin_44449518/article/details/104673669)
这篇博客开头说的腾讯微云中的`client.conf`到`fdfs包`中，并配置其中的`base_path`和`tracker_server`

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200306142745456.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
> 最后，在`settings.py`最后添加如下所示一段配置，用来设置Django默认文件存储类：
>`DEFAULT_FILE_STORAGE = 'utils.fdfs.storage.FDFSStorage'`
最后，可以在goods的admin中注册有文件上传的类，做上传文件的测试：如下图所示

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200306143301370.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)

> 最后，我们可以上传一个文件看到，返回的是这样一串代号`group1/M00/00/00/rBHtHF5h4mmAUFjiAAIMqagzXdo9969059`，我们通过这个代号，前面跟上Tracker服务器的ip和端口号就可以访问到图片了。
> 例如：`http://39.105.92.190:8888/group1/M00/00/00/rBHtHF5h4mmAUFjiAAIMqagzXdo9969059`![在这里插入图片描述](https://img-blog.csdnimg.cn/20200306143521194.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
###### 【7】从redis缓存数据库中获取购物车记录
> **步骤大体如下：**
> （1）配置settings.py中配置缓存

```python
# session缓存设置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # redis的地址
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            # 密码
            # "PASSWORD": "",
        }
    }
}
# 配置session存储
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

> （2）`goods/views.py`中通过`hlen`这个函数获取购物车中商品种类的数量
> 
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200310102715814.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)
###### 【8】设置首页静态页面
> （1）在celery/tasks中定义函数`static_index_html()`，然后，把`goods/views.py`中获取数据库信息，的 代码复制到新定义的函数中，并去掉购物车的操作（静态页面用于对应`没有登录`的游客进行防止DDOS攻击采取的手段，并且购物车信息不同用户之间无关联，所以不需要购物车信息）。
> `注意：`这一步可以重写index.html，也可以不重写，重写的目的是完全消除购物车这个信息，不重写其实影响并不大。

```python
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
```

> （2）此时可以发出一个请求给celery，可以生成一个静态页面了。
> 步骤：进入在启动了celery的主机上，进入python终端，进入到项目目录下，在终端中输入以下命令就可以发送命令给celery生成首页静态页面

```python
from celery_task.tasks import static_index_html
        static_index_html.delay()
```

>（3）静态页面需要考虑一个问题，就是 `——>` 当管理员从后台更改首页对应的数据库中的信息的时候，需要重新生成静态首页。
> 这里的解决方法就是 `——>` 重写 `admin.ModelAdmin` 中的`save_model`和`delete_model`，因为这两个方法分别是：当更新表中数据，者删除表中数据的时候分别自动调用的方法。所以，我们就需要在这两个方法中添加 调用 celery生成首页静态页面的代码（如下图所示）
> 这里，我们抽出一个基类，让其他模型类继承于这个基类即可。这样便实现了，管理员更改后台数据库中的数据的时候，自动重新生成首页静态页面。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200310113255716.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)

> 除此之外，如果想让nginx关联首页静态页面，可以在nginx中增加配置项，目的就是区分开 当地址栏直接敲入网址和重定向时的区别。当然。如果不配置nginx也没有什么问题，可以在`goods/urls.py`中区分到底要返回静态页面还是非静态页面。

###### 【9】设置首页信息缓存
> 设置首页信息缓存到redis中，目的是为了防止恶意DDOS攻击，导致数据库压力过大，以至于崩溃
> **具体步骤如下：**
> 在views.py中配置获取缓存中首页缓存的信息，判断是否已经缓存，如果没有缓存就去数据库查询数据，查到的context后把信息存到redis中。如果redis中有对应的首页的缓存信息，就直接从缓存里读取信息。(如下图所示)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200310120913840.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)

> 配置完这个之后，还需要和celery生成静态首页一样考虑到什么时候页面缓存更新的问题，这个问题的解决有两种方式。
> 其中一种是，设置缓存的过期时间，上面在设置的时候就顺便设置了以下缓存的过期时间，`cache.set('index_page_data', context, 3600)`，3600秒之后会过期。
> 第二种是，和celery生成静态首页更新一样，在`admin.py`中配置，当管理员更改表中数据的时候，cache就清除。（如下图所示）

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200310121546419.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80NDQ0OTUxOA==,size_16,color_FFFFFF,t_70)

