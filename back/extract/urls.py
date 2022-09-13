from django.urls import path
from rest_framework import routers
from .views import extract

router = routers.DefaultRouter()
router.register('extract', extract, basename='extract') 

urlpatterns = [
    path('', extract, name='extract'),
]
