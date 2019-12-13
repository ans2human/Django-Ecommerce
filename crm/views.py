from django.shortcuts import render, HttpResponse

# Create your views here.


def crm_home(request):
    return HttpResponse("this is crm ")