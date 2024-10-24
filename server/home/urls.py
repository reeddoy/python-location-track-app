from home import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='home'),
    path('api/v2/test', views.test, name='test'),
    path('login/', views.login_view, name='login'),
    path('check_location/', views.location_view, name='location_view'),
]




