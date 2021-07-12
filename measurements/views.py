from django.shortcuts import render, get_object_or_404
from .models import Measurement
from .forms import MeasurementModeForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from .utils import get_geo, get_center_coordinates, get_zoom, get_ip_address
import folium
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup as bs
import speech_recognition as sr
import pyttsx3 



# Create your views here.
def index(request):
    
    return render(request, 'index.html')



def search(request):
    if request.method == 'POST':
        search = request.POST['search']
        url = 'https://www.ask.com/web?q='+search
        res = requests.get(url)
        soup = bs(res.text, 'lxml')

        result_listings = soup.find_all('div', {'class': 'PartialSearchResults-item'})

        final_result = []

        for result in result_listings:
            result_title = result.find(class_='PartialSearchResults-item-title').text
            result_url = result.find('a').get('href')
            result_desc = result.find(class_='PartialSearchResults-item-abstract').text

            final_result.append((result_title, result_url, result_desc))

        context = {
            'final_result' : final_result
        }

        return render(request, 'search.html', context)

    else :
        return render(request, 'search.html')
# Create your views here.

def calculate_distance_view(request):
    # initial values
    distance = None
    destination = None
    
    obj = get_object_or_404(Measurement, id=1)
    form = MeasurementModeForm(request.POST or None)
    geolocator = Nominatim(user_agent='measurements')


    ip_ = get_ip_address(request)
    print(ip_)
    res = requests.get('https://ipinfo.io/')
    data=res.json()
    location = data['ip']
    country, city, lat, lon = get_geo(location)
    location = geolocator.geocode(city)

    # location coordinates
    l_lat = lat
    l_lon = lon
    pointA = (l_lat, l_lon)

    # initial folium map
    m = folium.Map(width=700, height=600, location=get_center_coordinates(l_lat, l_lon), zoom_start=8)
    # location marker
    folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],icon=folium.Icon(color='purple')).add_to(m)

    if form.is_valid():
        instance = form.save(commit=False)
        destination_ = form.cleaned_data.get('destination')
        destination = geolocator.geocode(destination_)

        # destination coordinates
        d_lat = destination.latitude
        d_lon = destination.longitude
        pointB = (d_lat, d_lon)
        # distance calculation
        distance = round(geodesic(pointA, pointB).km, 2)

        # folium map modification
        m = folium.Map(width=700, height=600, location=get_center_coordinates(l_lat, l_lon, d_lat, d_lon), zoom_start=get_zoom(distance))
        # location marker
        folium.Marker([l_lat, l_lon], tooltip='click here for more', popup=city['city'],
                    icon=folium.Icon(color='purple')).add_to(m)
        # destination marker
        folium.Marker([d_lat, d_lon], tooltip='click here for more', popup=destination,
                    icon=folium.Icon(color='red', icon='cloud')).add_to(m)


        # draw the line between location and destination
        line = folium.PolyLine(locations=[pointA, pointB], weight=5, color='blue')
        m.add_child(line)
        
        instance.location = location
        instance.distance = distance
        instance.save()
    
    m = m._repr_html_()

    context = {
        'distance' : distance,
        'destination': destination,
        'form': form,
        'map': m,
    }

    return render(request, 'calculate_distance_view.html', context)