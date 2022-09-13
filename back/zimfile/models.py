from telnetlib import STATUS
from django.db import models

class ZimFile(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    file = models.FileField(upload_to='zim/', null=True, blank=True)
    size = models.IntegerField()
    timestamp = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    hash = models.CharField(max_length=100, default='', blank=True, null=True)
    bzzlink = models.CharField(max_length=100, default='', blank=True, null=True)

