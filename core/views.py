import os
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from nsetools import Nse
import requests
from .models import Stock, Wishlist, Portfolio, StockData, EmailTemplate
from urllib.error import URLError
nse = Nse()
from bs4 import BeautifulSoup

iex_Base = "https://cloud.iexapis.com/stable/stock/"
iex_Token = "sk_0862eb49e31743088bcfd091a92771c2"


def home(request):
    if request.user.is_authenticated:
        return render(request, 'core/home.html')
    else:
        return render(request, 'landing.html')


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
    headers={'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30"}
    raw = requests.get(url_data, headers=headers)
    soup = BeautifulSoup(raw.content, 'html5lib')
    links = soup.find('a', {"class":"image"})
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
    print(query)
    stock_obj = Stock.objects.filter(stock_name=query).first()
    user_obj = request.user
    bought_price_query = StockData.objects.filter(stock_meta=stock_obj).first()
    print("bought_price_query>>>>>>>", bought_price_query.base_price)
    portfolio_data = {
        'stock': stock_obj,
        'user': user_obj,
        'quantity': 4,
        'bought_price': int(bought_price_query.base_price)
    }
    Portfolio.objects.create(**portfolio_data)
    qs = EmailTemplate.objects.get(email_type="WM")
    html_content = qs.email_template
    html_file = str(os.path.join(settings.EMAIL_TEMP, "mail_templates/email.html"))
    print(html_file)
    file = open(html_file, 'w+')
    file.write(html_content)
    file.close()
    subject = qs.email_template_name
    from_email = settings.EMAIL_HOST_USER
    body = render_to_string(
        "mail_templates/email.html",
        {
            'user': request.user.get_full_name,
            'body': "we're glad that you chose us for trading! We strive to cater all your trading needs"
            }
        )
    email = request.user.email
    send_mail(f'Welcome {request.user.first_name}',subject, from_email, [email], html_message=body,)
    open(html_file, 'w').close()
    return redirect('user_portfolio')


def user_portfolio(request):
    qs = Portfolio.objects.filter(user=request.user)
    return render(request, 'core/portfolio.html', {'qs': qs})


# wishlist function
def wishlist(request):                                                                                              #<--- function name
    wishlist_qs = Wishlist.objects.filter(user=request.user)                                                                 #<---- Getting wishlist for particular user who is logged in.
    if wishlist_qs:
        for q in wishlist_qs:                                                                                                   #<---- for loop to iterate through the wishlist items
            stock_last_data = StockData.objects.filter(stock_meta=q.stock)                                              #<-----
        return render(request, 'core/wishlist.html', {'qs': wishlist_qs, "stock_last_data": stock_last_data})
    else:
        return render(request, 'core/wishlist.html')

# TODO: report generation based on date filter
# TODO: analytics dashboard
# TODO: portfolio
# TODO: Suppose we search TCS and IEX has some IPO called the consulting services then the user will be confused with the response
# as he wished to see indian TCS and got some american company. SO new fucntionality should be something like listing of IPOs from both
# the platform if they exist.


# YES ITS POSSIBLE TO WRITE PYTHON SCRIPT AND CONVERT IT AS EXE
# NOW THE TASK IS HOW TO INSTALL PWA WITH PYTHON SCRIPT