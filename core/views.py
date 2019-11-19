from django.shortcuts import render, get_object_or_404, redirect
from nsetools import Nse
import requests
from django.utils import timezone
from .models import Stock, Wishlist
nse = Nse()

iex_Base = "https://cloud.iexapis.com" 
iex_Token = "sk_0862eb49e31743088bcfd091a92771c2"





def home(request):
    
    return render(request, 'core/home.html')





def stock_search(request, **kwargs):
    query = request.POST.get('stock_query')
    if query:
        stock_data = nse.get_quote(query)
        if not stock_data:
            iex_data = requests.get(iex_Base + '/stable/stock/' + query + '/quote?token=' + iex_Token)
            stock_data = iex_data.json()
    else:
        stock_data = nse.get_quote('ITC') 
    # print(stock_data)   
    stdata = {}
    if stock_data:

        stdata['stock_name'] = stock_data.get('symbol')
        # stdata['stock_price'] = stock_data.get('basePrice')
        if not Stock.objects.filter(stock_name=stock_data.get('symbol')).exists():
            stdata['updated_at'] = timezone.now()
            aa = Stock.objects.create(**stdata)
            context = {'stock_data':aa}
        else:
            aa = Stock.objects.filter(stock_name=stock_data.get('symbol')).first()
            aa.updated_at = timezone.now()
            aa.save()
            if Wishlist.objects.filter(user=request.user, stock=aa).exists():
                context = {'stock_data':aa, 'stock_exists':"true"}
            else:
                context = {'stock_data':aa}
    else:
        context = {'stock_data':"No data Available"}
    return render(request, "core/stock_search.html", context)


def add_to_wishlist(request):
    query = request.GET.get('links')
    stock_obj = Stock.objects.filter(stock_name=query).first()
    user_obj = request.user
    Wishlist.objects.create(user=user_obj, stock=stock_obj)
    return redirect('stock_search')



def wishlist(request):
    qs = Wishlist.objects.filter(user=request.user)
    return render(request, 'core/wishlist.html',{'qs':qs})