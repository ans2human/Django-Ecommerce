from django.db import models
from django.conf import settings
# Create your models here.



class Stock(models.Model):
    stock_name = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()
    def __str__(self):
        return self.stock_name

        
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)