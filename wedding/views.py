from django.conf import settings
from django.shortcuts import render

def home(request):
    return render(request, 'home.html', context={
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
        'website_url': settings.WEDDING_WEBSITE_URL,
        'couple_name': settings.BRIDE_AND_GROOM,
        'wedding_location': settings.WEDDING_LOCATION,
        'wedding_date': settings.WEDDING_DATE, 
        'map_url': settings.CEREMONY_MAP,
        'ceremony_start' : settings.CEREMONY_START,
        'ceremony_address': settings.CEREMONY_ADDRESS,
        # Some of the wedding party stayed at an AirBnB called Caboose Farm. 
        'caboose_farm_name': settings.CABOOSE_FARM_NAME, 
        'caboose_farm_map' : settings.CABOOSE_FARM_MAP, 
        'caboose_farm_address': settings.CABOOSE_FARM_ADDRESS,
        # A honeymoon fund is not strictly necessary. Replace the URL with whatever you like in your .env file 
        'honeymoon_fund' : settings.HONEYMOON_FUND,
    })  
