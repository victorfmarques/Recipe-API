from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


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


class RecipeSerializer(serializers.ModelSerializer):
    ''' Serializer par ao model de Recipe '''

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'ingredients', 'tags', 'time_minutes', 'price', 'link')
        read_only_fields = ('id',)