import time
from django.http import HttpResponse
import docker,os

def extract(request):
    client = docker.from_env()
    try:
        print("Pull image docker ...")
        os.system("docker pull mrdotiendat/zimserver:latest")
        time.sleep(30)
        print("Run image docker ...")
        os.system('docker run -it -p 9454:9454 mrdotiendat/zimserver:latest')
        time.sleep(10)
        print("Extracting ...")
        return HttpResponse("Extracting success on port 9454")
    except:
        print("Error")
        return HttpResponse("Error") 
                
        
        