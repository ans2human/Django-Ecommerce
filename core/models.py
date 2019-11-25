from django.db import models
from django.conf import settings
# Create your models here.



class Stock(models.Model):
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
    current_price = models.IntegerField()
    base_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()

class Portfolio(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    bought_price = models.FloatField(default=0.0)

    def total_price(self):
        return self.bought_price * self.quantity
        
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)