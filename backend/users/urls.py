from django.urls import path
from users.views.views_auth import login_view, token_refresh_view
from users.views.views_user import users_list, users_detail
from users.views.views_batch import users_bulk

urlpatterns = [
    # Auth
    path('login/', login_view, name='login'),
    path('token/refresh/', token_refresh_view, name='token_refresh'),

    # User CRUD
    path('', users_list, name='users_list'),
    path('<int:pk>/', users_detail, name='users_detail'),

    # Batch
    path('batch/', users_bulk, name='users_bulk'),
]
