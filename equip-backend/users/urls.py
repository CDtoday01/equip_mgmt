from django.urls import path
from users.views import (
    login_view,
    token_refresh_view,
    users_list,
    users_detail,
    users_bulk,
    users_search,
)

urlpatterns = [
    path('login/', login_view),
    path('refresh/', token_refresh_view),
    path('bulk/', users_bulk),
    path('search/', users_search),
    path('<str:id_number>/', users_detail),
    path('', users_list),
]
