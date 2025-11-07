# urls.py
from django.urls import path
from .views import people_list, people_detail, people_bulk, people_search

urlpatterns = [
    path('bulk/', people_bulk, name='people_bulk'),
    path('search/', people_search, name='people_search'),
    path('', people_list, name='people_list'),
    path('<str:id_number>/', people_detail, name='people_detail'),
]