import os
import requests
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db.models import F, Sum
from bs4 import BeautifulSoup
from nsetools import Nse
from .models import Stock, Wishlist, Portfolio, StockData, EmailTemplate
from .notification_emails import add_to_portfolio_mail
from .forms import PortfolioForm
from urllib.error import URLError
nse = Nse()

iex_Base = "https://cloud.iexapis.com/stable/stock/"
iex_Token = "sk_0862eb49e31743088bcfd091a92771c2"


def user_portfolio_dashboard(request):
    if request.user.is_authenticated:
        no_of_bought_stocks = Portfolio.objects.filter(
            user=request.user).count()

        context = {
            "no_of_bought_stocks": no_of_bought_stocks
        }
        return render(request, 'core/home.html', context)
    else:
        return redirect('login')


def iex_api_func(query):
    if query is not "None":
        iex_data = requests.get(iex_Base + query + '/quote?token=' + iex_Token)
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


def company_logo_scraper(aa):
    url = 'https://en.wikipedia.org/wiki/'
    url_data = url + aa.company_name
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"}
    raw = requests.get(url_data, headers=headers)
    soup = BeautifulSoup(raw.content, 'html5lib')
    links = soup.find('a', {"class": "image"})
    a = links.img['srcset'].split(",")
    b = a[-1].strip().replace("//", 'https://').replace(" 2x", "")
    comp_obj = Stock.objects.get(id=aa.id)
    comp_obj.stock_image = b
    comp_obj.save()


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
            company_logo_scraper(aa)
        else:
            aa = Stock.objects.filter(
                stock_name=stock_data.get('symbol')).first()
            aa.updated_at = timezone.now()
            aa.save()
        context = {'stock_data': aa, 'stock_data_response': True}

        if StockData.objects.filter(stock_meta=aa).exists():
            stock_data_obg = StockData.objects.filter(stock_meta=aa).first()
            stock_data_obg.current_price = stock_data.get('iexRealtimePrice') if stock_data.get(
                'iexRealtimePrice') else stock_data.get('basePrice')
            stock_data_obg.save()
        else:
            cice = stock_data.get('iexRealtimePrice') if stock_data.get(
                'iexRealtimePrice') else stock_data.get('basePrice')
            brie = stock_data.get('latestPrice') if stock_data.get(
                'latestPrice') else stock_data.get('lastPrice')
            updt = timezone.now()
            StockData.objects.create(
                stock_meta=aa, current_price=cice, base_price=brie, updated_at=updt)

        if Wishlist.objects.filter(user=request.user, stock=aa).exists():
            context = {'stock_data': aa, 'stock_exists': "True",
                       'stock_data_response': True}
        else:
            context = {'stock_data': aa, "stock_data_response": True}
    else:
        context = {
            'stock_data': "No data Available, Please check the Symbol",
            'stock_data_response': False
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
    stock_obj = Stock.objects.filter(stock_name=query).first()
    data_dict={
             'user' : request.user.id,
             'stock': stock_obj.id,
             'quantity' : 1,
             'bought_price' : 0.0
             }
    if request.method == "POST":
        form = PortfolioForm(request.POST or None)
        if form.is_valid():
            form.user = request.user.id,
            print(form)
            form.save()
            return redirect('user_portfolio')
        else:
            form = PortfolioForm(initial = data_dict)
            return render(request, "core/add_portfolio.html", {"form":form})
    else:
        form = PortfolioForm(initial = data_dict)
        return render(request, "core/add_portfolio.html", {"form":form})

@login_required()
def user_portfolio(request):
    qs = Portfolio.objects.values("stock__stock_name").annotate(Sum('quantity'), tcp=Sum(F('quantity')*F('bought_price')))
    for stock_name in qs:
        stock_cr_price = iex_api_func(stock_name.get('stock__stock_name')) if iex_api_func(stock_name.get('stock__stock_name')) else nse_api_func(stock_name.get('stock__stock_name'))
        stock_c_price = stock_cr_price.get('iexRealtimePrice') if stock_cr_price.get('iexRealtimePrice') else stock_cr_price.get('basePrice') or stock_cr_price.get('latestPrice')
        qnty = int(stock_name.get('quantity__sum'))
        dtcp = float(stock_name.get('tcp'))
        gain_percent = ((stock_c_price * qnty) - dtcp)/dtcp * 100
        cpdata = {
            "stock_c_price": stock_c_price,
            "gain_percent" : gain_percent
        }
        stock_name.update(cpdata)
        print(stock_name)
    return render(request, 'core/portfolio.html', {'qs': qs})


def wishlist(request):
    wishlist_qs = Wishlist.objects.filter(user=request.user)
    if wishlist_qs:
        for q in wishlist_qs:
            stock_last_data = StockData.objects.filter(
                stock_meta=q.stock)
        return render(request, 'core/wishlist.html', {'qs': wishlist_qs, "stock_last_data": stock_last_data})
    else:
        return render(request, 'core/wishlist.html')


def search_st_aj_func(request):
    query = request.GET.get('search', "None")
    print("query", query)
    queryset = Stock.objects.filter(stock_name__startswith=query)
    print(queryset)
    st = []
    for i in queryset:
        st.append(i.stock_name)
    data = {
        'list': st,
    }
    print(data)
    return JsonResponse(data)


def search_stock_ajax(request):
    return render(request, "core/ajax_stock_search.html")


# TODO: report generation based on date filter
# TODO: analytics dashboard
# TODO: portfolio
# TODO: Suppose we search TCS and IEX has some IPO called the consulting services then the user will be confused with the response
# as he wished to see indian TCS and got some american company. SO new fucntionality should be something like listing of IPOs from both
# the platform if they exist.


# YES ITS POSSIBLE TO WRITE PYTHON SCRIPT AND CONVERT IT AS EXE
# NOW THE TASK IS HOW TO INSTALL PWA WITH PYTHON SCRIPT
