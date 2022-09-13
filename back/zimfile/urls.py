from rest_framework import routers
from django.urls import path, include,re_path
from . import views

router = routers.DefaultRouter()
router.register('zimfile', views.ZimFileView, basename='zimfile')

urlpatterns = [
    re_path(r'^zim', include(router.urls)),
    path('zim/', views.index, name='index'),
    path('zim/listfile', views.ZimFileView.as_view({'get': 'listfile'}), name='listfile'),
    path('zim/createfile', views.ZimFileView.as_view({'post': 'createfile'}), name='createfile'),
    path('zim/updatefile/<int:pk>', views.ZimFileView.as_view({'put': 'updatefile'}), name='updatefile'),
    path('zim/deletefile/<int:pk>', views.ZimFileView.as_view({'delete': 'deletefile'}), name='deletefile'),
    path('zim/search/<str:partial>', views.ZimFileView.as_view({'get': 'search'}), name='search'),
    path('zim/search_en', views.ZimFileView.as_view({'get': 'search_en'}), name='search_en'),
]
