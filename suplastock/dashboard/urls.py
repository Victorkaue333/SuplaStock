from django.urls import path

from .views import landing_view

app_name = 'dashboard'

urlpatterns = [
    path('', landing_view, name='landing'),
]
