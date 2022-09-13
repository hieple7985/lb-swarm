from rest_framework import serializers
from .models import ZimFile

class ZimFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZimFile
        fields = ('name', 'file', 'size', 'timestamp', 'status', 'hash', 'bzzlink','id')
        
    def create(self, validated_data):
        return ZimFile.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.file = validated_data.get('file', instance.file)
        instance.size = validated_data.get('size', instance.size)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.status = validated_data.get('status', instance.status)
        instance.hash = validated_data.get('hash', instance.hash)
        instance.bzzlink = validated_data.get('bzzlink', instance.bzzlink)
        instance.save()
        return instance
    
    def delete(self, instance):
        instance.delete()
        return instance