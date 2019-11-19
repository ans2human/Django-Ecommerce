from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name="home"),
    path('stock/search', views.stock_search, name="stock_search"),
    path('stock/wishlist', views.wishlist, name="wishlist"),
    path('stock/add', views.add_to_wishlist, name="add_to_wishlist"),
]