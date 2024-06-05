from django.urls import path
from .views import signup, login_view, home_view, uav_list, uav_create, uav_update, uav_delete, rental_list, rental_create, rental_form_with_uav, uav_details
from . import views
from .views import get_models_by_brand

urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('uavs/', uav_list, name='uav_list'),
    path('uavs/new/', uav_create, name='uav_create'),
    path('uavs/<int:pk>/edit/', uav_update, name='uav_update'),
    path('uavs/<int:pk>/delete/', uav_delete, name='uav_delete'),
    path('rentals/', rental_list, name='rental_list'),
    path('rentals/new/', rental_create, name='rental_create'),
    path('api/models/', views.get_models, name='get_models'),
    path('get-models/', get_models_by_brand, name='get_models_by_brand'),
    path('rentals/create/<int:uav_id>/', rental_form_with_uav, name='rental_form_with_uav'),
    path('rental/create/<int:uav_id>/', views.rental_create_with_uav, name='rental_create_with_uav'),
    path('uav-details/<int:uav_id>/', views.uav_details, name='uav_details'),
]

