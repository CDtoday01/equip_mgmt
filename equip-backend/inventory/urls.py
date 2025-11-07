from django.urls import path
from . import views

urlpatterns = [
    path("assets/", views.assets_list, name="assets_list"),            # GET: 列表 / POST: 新增
    path("assets/<int:pk>/", views.asset_detail, name="asset_detail"), # GET / PUT / DELETE
    path('stock_transaction/', views.stock_transaction),
    path('stock_history/<str:asset_tag>/', views.stock_history),
]
