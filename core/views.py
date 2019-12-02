from django.shortcuts import render, get_object_or_404, redirect
from nsetools import Nse
import requests
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Stock, Wishlist, Portfolio, StockData
from urllib.error import URLError
nse = Nse()

iex_Base = "https://cloud.iexapis.com/stable/stock/"
iex_Token = "sk_0862eb49e31743088bcfd091a92771c2"




def home(request):
    return render(request, 'core/home.html')


def iex_api_func(query):
    if query is not "None":
        iex_data = requests.get(iex_Base  + query + '/quote?token=' + iex_Token)
    else:
        stock_data = None
        return stock_data
    if iex_data:
        stock_data = iex_data.json()
        return stock_data


def nse_api_func(query):
    try:
        if query is not 'None':
            stock_data = nse.get_quote(query)
        else:
            stock_data = None
        return stock_data
    except URLError:
            pass



@login_required()
def stock_search(request, **kwargs):
    query = request.POST.get('stock_query', "None")
    stock_data = iex_api_func(query)
    if not stock_data:
        stock_data = nse_api_func(query)
    stdata = {}
    if stock_data:
        stdata['stock_name'] = stock_data.get('symbol')
        stdata['company_name'] = stock_data.get('companyName')
        print(stock_data)
        if not Stock.objects.filter(stock_name=stock_data.get('symbol')).exists():
            stdata['updated_at'] = timezone.now()
            stdata['created_by'] = request.user.id
            aa = Stock.objects.create(**stdata)
        else:
            aa = Stock.objects.filter(stock_name=stock_data.get('symbol')).first()
            aa.updated_at = timezone.now()
            aa.save()
        context = {'stock_data':aa, 'stock_data_response':True}

        if StockData.objects.filter(stock_meta=aa).exists():
            stock_data_obg = StockData.objects.filter(stock_meta=aa).first()
            stock_data_obg.current_price = stock_data.get('iexRealtimePrice') if stock_data.get('iexRealtimePrice') else stock_data.get('basePrice')
            stock_data_obg.save()
        else:
            cice = stock_data.get('iexRealtimePrice') if stock_data.get('iexRealtimePrice') else stock_data.get('basePrice')
            brie = stock_data.get('latestPrice') if stock_data.get('latestPrice') else stock_data.get('lastPrice')
            updt = timezone.now()
            StockData.objects.create(stock_meta=aa, current_price=cice, base_price=brie, updated_at=updt)


            if Wishlist.objects.filter(user=request.user, stock=aa).exists():
                context = {'stock_data':aa, 'stock_exists':"True", 'stock_data_response':True}
            else:
                context = {'stock_data':aa, "stock_data_response": True}
    else:
        context = {
                    'stock_data':"No data Available, Please check the Symbol",
                    'stock_data_response':False
                    }
    return render(request, "core/stock_search.html", context)


def add_to_wishlist(request):
    query = request.GET.get('links')
    stock_obj = Stock.objects.filter(stock_name=query).first()
    user_obj = request.user
    Wishlist.objects.create(user=user_obj, stock=stock_obj)
    return redirect('stock_search')

def add_to_portfolio(request):
    query = request.GET.get('portfolio')
    print(query)
    stock_obj = Stock.objects.filter(stock_name=query).first()
    user_obj = request.user
    bought_price_query = StockData.objects.filter(stock_meta=stock_obj).first()
    print("bought_price_query>>>>>>>", bought_price_query.base_price)
    portfolio_data = {
        'stock':stock_obj,
        'user':user_obj,
        'quantity': 4,
        'bought_price': int(bought_price_query.base_price)
    }
    Portfolio.objects.create(**portfolio_data)
    #send mail
    return redirect('user_portfolio')

def user_portfolio(request):
    qs  = Portfolio.objects.filter(user=request.user)
    return render(request, 'core/portfolio.html',{'qs':qs})

#wishlist function
def wishlist(request):
    qs = Wishlist.objects.filter(user=request.user)
    for q in qs:
        stock_last_data = StockData.objects.filter(stock_meta=q.stock)
    return render(request, 'core/wishlist.html',{'qs':qs, "stock_last_data":stock_last_data})


# TODO: report generation based on date filter
# TODO: analytics dashboard
# TODO: portfolio




# idea
