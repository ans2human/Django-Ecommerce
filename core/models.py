from django.db import models
from django.conf import settings
# Create your models here.


class Stock(models.Model):
    stock_image = models.URLField()
    stock_name = models.CharField(max_length=15)
    company_name = models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
    created_by = models.IntegerField()

    def __str__(self):
        return self.stock_name


class StockData(models.Model):
    # TODO: add more relevant stock data fields
    stock_meta = models.ForeignKey(Stock, on_delete=models.CASCADE)
    current_price = models.IntegerField(null=True, blank=True)
    base_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()

class Portfolio(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1.0)
    bought_price = models.FloatField(default=0.0)

    def stock_current_price(self):
        from .views import iex_api_func, nse_api_func
        stock_cr_price = iex_api_func(self.stock.stock_name) if iex_api_func(self.stock.stock_name) else nse_api_func(self.stock.stock_name)
        stock_c_price = stock_cr_price.get('iexRealtimePrice') if stock_cr_price.get(
            'iexRealtimePrice') else stock_cr_price.get('basePrice') or stock_cr_price.get('latestPrice')
        print(stock_c_price)
        return stock_c_price
    def gain_percent(self):
        scprice = self.stock_current_price() if self.stock_current_price() else None
        if scprice is not None:
            return ((scprice - self.bought_price)/self.bought_price) * 100
        else:
            return 0
    def total_price(self):
        return self.bought_price * self.quantity

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)


EMAIL_TYPES = (
    ("WM", "Welcome mail"),
    ("PM", "portfolio mail"),
    ("WSM", "Wishlist mail"),
    ("PRM", "Password Reset mail"),
)




class EmailTemplate(models.Model):
    email_template = models.TextField(max_length=50000)
    email_template_name = models.CharField(max_length=250)
    email_type = models.CharField(choices=EMAIL_TYPES, max_length=10)
