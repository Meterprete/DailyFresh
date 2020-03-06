from django.contrib import admin
from apps.goods.models import GoodsType


class GoodsTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'logo', 'image']


admin.site.register(GoodsType, GoodsTypeAdmin)
