from rest_framework import serializers

from core.models import Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    ''' Serializer para o modelo de Tag '''

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    ''' Serializer para o modelo de Ingredient '''

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields =  ('id',)