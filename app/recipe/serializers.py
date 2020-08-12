from rest_framework import serializers

from core.models import Tag


class TagSerializer(serializers.ModelSerializer):
    ''' Serializer para o modelo de Tag '''

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)