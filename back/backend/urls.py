from django.contrib import admin
from django.urls import path, include
from zimfile.views import index

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('api/', include('zimfile.urls')),
    path('trigger/', include('trigger.urls')),
    path('download/', include('download.urls')),
    path('extract/', include('extract.urls')),
]
