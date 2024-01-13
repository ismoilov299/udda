from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number', 'lang_id', 'chat_id', 'shop_name')
    # list_display_links = ('first_name')

admin.site.register(User, UserAdmin)

class AdminAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'chat_id', 'delivery_right', 'stat_right', 'report_right', 'test_right', 'all_right')

admin.site.register(Admin, AdminAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'name_ru', 'name_en', 'parent')


admin.site.register(Category, CategoryAdmin)

class shop_nameAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'parent')


admin.site.register(shop_name, shop_nameAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
    'p_id', 'name_uz', 'name_ru', 'name_en', 'category', 'description_uz', 'description_ru', 'description_en', 'price', 'image')


admin.site.register(Product, ProductAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id',  'status', 'user_id', 'created_at','order_id')

admin.site.register(Order, OrderAdmin)


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'amount', 'created_at')


admin.site.register(OrderProduct, OrderProductAdmin)

# admin.site.register(About)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'comment_text', 'username')


# admin.site.register(About)
admin.site.register(Comment, CommentAdmin)


class NewAdmin(admin.ModelAdmin):
    list_display = ('posted_at',  'text_uz', 'text_ru', 'text_en', 'image')


admin.site.register(New, NewAdmin)
