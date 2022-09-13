from django.shortcuts import render
from rest_framework import viewsets, response, status
import requests
from .serializers import ZimFileSerializer
from .models import ZimFile
from django.shortcuts import render, get_object_or_404

class ZimFileView(viewsets.ModelViewSet):
    serializer_class = ZimFileSerializer
    queryset = ZimFile.objects.all()
    
    def search(self, request, partial=None):
        queryset = ZimFile.objects.filter(name__contains=partial)
        serializer = ZimFileSerializer(queryset, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    def search_en (self, request, partial="_en_"):
        zim_files = ZimFile.objects.filter(name__contains='_en_').order_by('size')
        return render(request, 'pages/zimfile.html', {'zim_files': zim_files})
    
    def listfile(self, request):
        queryset = ZimFile.objects.all()
        serializer = ZimFileSerializer(queryset, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    
    def createfile(self, request):
        serializer = ZimFileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def updatefile(self, request, pk):
        zim = get_object_or_404(ZimFile, pk=pk)
        serializer = ZimFileSerializer(zim, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def deletefile(self, request, pk):
        zim = get_object_or_404(ZimFile, pk=pk)
        zim.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


def index(request):
    zim_files = ZimFile.objects.all().order_by('id')
    context = {'zim_files': zim_files}
    return render(request, 'pages/zimfile.html', context)

