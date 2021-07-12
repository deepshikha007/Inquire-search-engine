from django.urls import path
from .views import index,search,calculate_distance_view


app_name = 'measurements'

urlpatterns = [
    path('', index, name='index'),
    path('search', search, name='search'),
    path('calculate_distance_view', calculate_distance_view, name='calculate_distance_view'),
]