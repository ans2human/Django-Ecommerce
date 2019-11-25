from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name="home"),
    path('stock/search', views.stock_search, name="stock_search"),
    path('stock/wishlist', views.wishlist, name="wishlist"),
    path('stock/wishlist/add', views.add_to_wishlist, name="add_to_wishlist"),
    path('user/portfolio/add', views.add_to_portfolio, name="add_to_portfolio"),
    path('user/portfolio', views.user_portfolio, name="user_portfolio"),
]