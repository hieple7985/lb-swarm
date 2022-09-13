from zimfile.models import ZimFile
from django.http import JsonResponse
from django.shortcuts import  get_object_or_404
import requests


SWARM_HOST = 'http://localhost:1633/bzz'
SWARM_BATCH_ID = ""

def download(request,name=None):
    zim_file = get_object_or_404(ZimFile, name=name)
    if zim_file.status == 'DOWNLOADED':
        data = {'file': zim_file.name,
                'swarm-batch-id:': SWARM_BATCH_ID,}
        status = requests.post(SWARM_HOST, data=data).status_code
        if status == 200:
            zim_file.status = 'UPLOADED'
            zim_file.save()
            return JsonResponse({zim_file.name: 'Uploaded'}, status=status)
        else :
            return JsonResponse({zim_file.name: 'Upload failed'}, status=status)
    else:
        return JsonResponse({zim_file.name: 'Not downloaded'}, status=400)
