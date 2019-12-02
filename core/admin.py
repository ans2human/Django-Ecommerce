from django.contrib import admin
from .models import Wishlist, Stock, StockData, Portfolio, EmailTemplate
# Register your models here.


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('stock_name', 'company_name',  'created_at', 'updated_at', 'created_by')




@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock')


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'stock', 'quantity', 'bought_price')


@admin.register(StockData)
class StockDataAdmin(admin.ModelAdmin):
    list_display = ('stock_meta', 'base_price', 'current_price', 'created_at', 'updated_at')


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('email_type', 'email_template_name')