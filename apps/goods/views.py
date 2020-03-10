from django.core.cache import cache
from django.shortcuts import render
from django.views import View
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner
from django_redis import get_redis_connection


class IndexView(View):
    def get(self, request):
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')
        if context is None:
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
            cache.set('index_page_data', context, 3600)
        cart_count = 0
        user = request.user
        if user.is_authenticated:
            # 用户已经登录
            conn = get_redis_connection('default')
            cart_key = 'cart_{}'.format(user.id)
            cart_count = conn.hlen(cart_key)
        # 组织模板上下文
        context.update(cart_count=cart_count)
        # 使用模板
        return render(request, 'index.html', context)
