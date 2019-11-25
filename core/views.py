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

# iex data format
# {
# 	'symbol': 'AAPL',
# 	'companyName': 'Apple, Inc.',
# 	'primaryExchange': 'NASDAQ',
# 	'calculationPrice': 'tops',
# 	'open': None,
# 	'openTime': None,
# 	'close': None,
# 	'closeTime': None,
# 	'high': None,
# 	'low': None,
# 	'latestPrice': 264.705,
# 	'latestSource': 'IEX real time price',
# 	'latestTime': '1:44:49 PM',
# 	'latestUpdate': 1574707489894,
# 	'latestVolume': None,
# 	'iexRealtimePrice': 264.705,
# 	'iexRealtimeSize': 15,
# 	'iexLastUpdated': 1574707489894,
# 	'delayedPrice': None,
# 	'delayedPriceTime': None,
# 	'extendedPrice': None,
# 	'extendedChange': None,
# 	'extendedChangePercent': None,
# 	'extendedPriceTime': None,
# 	'previousClose': 261.78,
# 	'previousVolume': 16331263,
# 	'change': 2.925,
# 	'changePercent': 0.01117,
# 	'volume': None,
# 	'iexMarketPercent': 0.015709757246503513,
# 	'iexVolume': 160377,
# 	'avgTotalVolume': 23631727,
# 	'iexBidPrice': 262,
# 	'iexBidSize': 100,
# 	'iexAskPrice': 264.75,
# 	'iexAskSize': 100,
# 	'marketCap': 1176155785350,
# 	'peRatio': 22.18,
# 	'week52High': 268,
# 	'week52Low': 142,
# 	'ytdChange': 0.66887,
# 	'lastTradeTime': 1574707489894,
# 	'isUSMarketOpen': True
# }

def iex_api_func(query):
    if query is not "None":
        iex_data = requests.get(iex_Base  + query + '/quote?token=' + iex_Token)
    else:
        stock_data = None 
        return stock_data
    if iex_data:    
        stock_data = iex_data.json()
        return stock_data

# nse data format
# {
# 	'pricebandupper': 272.4,
# 	'symbol': 'ITC',
# 	'applicableMargin': 12.5,
# 	'bcEndDate': '27-MAY-19',
# 	'totalSellQuantity': 9144.0,
# 	'adhocMargin': None,
# 	'companyName': 'ITC Limited',
# 	'marketType': 'N',
# 	'exDate': '22-MAY-19',
# 	'bcStartDate': '24-MAY-19',
# 	'css_status_desc': 'Listed',
# 	'dayHigh': 248.4,
# 	'basePrice': 247.65,
# 	'securityVar': 4.69,
# 	'pricebandlower': 222.9,
# 	'sellQuantity5': None,
# 	'sellQuantity4': None,
# 	'sellQuantity3': None,
# 	'cm_adj_high_dt': '21-MAY-19',
# 	'sellQuantity2': None,
# 	'dayLow': 246.25,
# 	'sellQuantity1': 9144.0,
# 	'quantityTraded': 10586688.0,
# 	'pChange': 0.06,
# 	'totalTradedValue': 26180.88,
# 	'deliveryToTradedQuantity': 62.55,
# 	'totalBuyQuantity': None,
# 	'averagePrice': 247.3,
# 	'indexVar': None,
# 	'cm_ffm': 213052.32,
# 	'purpose': 'DIVIDEND - RS 5.75 PER SHARE',
# 	'buyPrice2': None,
# 	'secDate': '25-Nov-2019 00:00:00',
# 	'buyPrice1': None,
# 	'high52': 310.0,
# 	'previousClose': 247.65,
# 	'ndEndDate': None,
# 	'low52': 234.05,
# 	'buyPrice4': None,
# 	'buyPrice3': None,
# 	'recordDate': None,
# 	'deliveryQuantity': 6622333.0,
# 	'buyPrice5': None,
# 	'priceBand': 'No Band',
# 	'extremeLossMargin': 5.0,
# 	'cm_adj_low_dt': '18-SEP-19',
# 	'varMargin': 7.5,
# 	'sellPrice1': 247.75,
# 	'sellPrice2': None,
# 	'totalTradedVolume': 10586688.0,
# 	'sellPrice3': None,
# 	'sellPrice4': None,
# 	'sellPrice5': None,
# 	'change': 0.15,
# 	'surv_indicator': None,
# 	'ndStartDate': None,
# 	'buyQuantity4': None,
# 	'isExDateFlag': False,
# 	'buyQuantity3': None,
# 	'buyQuantity2': None,
# 	'buyQuantity1': None,
# 	'series': 'EQ',
# 	'faceValue': 1.0,
# 	'buyQuantity5': None,
# 	'closePrice': 247.75,
# 	'open': 247.75,
# 	'isinCode': 'INE154A01025',
# 	'lastPrice': 247.8
# }

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
        # stdata['stock_price'] = stock_data.get('basePrice')
        if not Stock.objects.filter(stock_name=stock_data.get('symbol')).exists():
            stdata['updated_at'] = timezone.now()
            stdata['created_by'] = request.user.id
            aa = Stock.objects.create(**stdata)
            context = {'stock_data':aa}
        else:
            aa = Stock.objects.filter(stock_name=stock_data.get('symbol')).first()
            aa.updated_at = timezone.now()
            aa.save()
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
        'bought_price': 12
    }
    Portfolio.objects.create(**portfolio_data)
    return redirect('user_portfolio')

def user_portfolio(request):
    qs  = Portfolio.objects.filter(user=request.user)
    return render(request, 'core/portfolio.html',{'qs':qs})   

def wishlist(request):
    qs = Wishlist.objects.filter(user=request.user)
    for q in qs:
        stock_last_data = StockData.objects.filter(stock_meta=q.stock)
    return render(request, 'core/wishlist.html',{'qs':qs, "stock_last_data":stock_last_data})