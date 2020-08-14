from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class BaseRecipeAttrViewset(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin
                            ):
    ''' Classe base contendo os atributos de name e user '''
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        ''' Retorna queryset contendo somente referencias do usuário atual '''
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        ''' Realiza a criação referente ao serializer da classe '''
        serializer.save(user=self.request.user)
    

class TagViewSet(BaseRecipeAttrViewset):
    ''' Lida com as tags no BD '''
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseRecipeAttrViewset):
    ''' Lida com ingredients no BD '''
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    ''' Lida com os recipes no BD '''

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        ''' Retorna as Recipes do usuário da requisição '''
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        ''' Retorna a classe de serializer apropriada '''
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        
        return self.serializer_class

    def perform_create(self, serializer):
        ''' Realiza a criação referente ao serializer da classe '''
        serializer.save(user=self.request.user)