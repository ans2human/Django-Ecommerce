from django.contrib import admin
from .models import Wishlist, Stock
# Register your models here.


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('stock_name', 'created_at', 'updated_at')




@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock')