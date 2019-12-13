from django.urls import path
from .views import crm_home


urlpatterns = [
    path("home", crm_home, name="crm_home"),
]