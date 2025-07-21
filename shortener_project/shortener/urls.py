from django.urls import path
from . import views

urlpatterns = [
    path("shorturls", views.create_short_url),  
    path("<str:code>", views.redirect_to_original),
    path("shorturls/<str:shortcode>", views.get_url_statistics, name="get_url_statistics"),
]
