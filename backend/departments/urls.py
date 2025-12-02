from django.urls import path
from . import views

urlpatterns = [
    path('', views.departments_list, name='departments_list'),           # GET, POST
    path('<int:dept_id>/', views.department_detail, name='department_detail'),  # GET, PUT, DELETE
]
