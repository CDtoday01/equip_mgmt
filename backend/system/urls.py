from django.urls import path
from .views import get_product_check_setting, toggle_product_check_setting

urlpatterns = [
    path("check-setting/", get_product_check_setting),
    path("toggle-setting/", toggle_product_check_setting),
]
