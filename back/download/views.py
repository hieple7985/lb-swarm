import http
from zimfile.models import ZimFile
from django.conf import settings
from urllib.request import urlretrieve
from django.shortcuts import  get_object_or_404
from django.http import JsonResponse



HOST = 'https://dumps.wikimedia.org/other/kiwix/zim/wikipedia/'

def download(request,pk=None):
    zimfile = get_object_or_404(ZimFile, pk=pk)
    def download_progress(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        print('Downloading: %d%%' % percent)
    urlretrieve(HOST+zimfile.name, settings.MEDIA+zimfile.name, reporthook=download_progress)
    zimfile.status = 'DOWNLOADED'
    zimfile.save()
    return JsonResponse({zimfile.name: 'Downloaded'}, status=http.HTTPStatus.OK)
    