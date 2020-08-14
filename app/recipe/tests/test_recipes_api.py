from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    ''' Retorna o URL de um detalhe de Recipe '''
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='TAG TESTE'):
    ''' Cria e retorna uma Tag '''
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='canela'):
    ''' Cria e retorna um Ingredient '''
    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params):
    '''Cria e retorna uma Recipe'''
    defaults = {
        'title' : 'Title',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    ''' Classe Teste de recursos publicos do endpoint de Recipes '''

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        ''' Teste que valida a necessidade de autenticação para o acesso de Recipes '''
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    ''' Classe Teste de recursos privados do endpoint de Recipes '''

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='email@email.com',
            password='senha123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)


    def test_retrieve_recipes(self):
        ''' Teste de listagem de Recipes '''
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        recipes = Recipe.objects.all().order_by('-id')
        serialized = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialized.data)

    def test_retrive_recipes_limited_to_user(self):
        ''' Teste de listagem de Recipes do usuário autenticado '''
        user_2 = get_user_model().objects.create_user(
            email='email@teste.com',
            password='teste1234'
        )
        sample_recipe(self.user)
        sample_recipe(self.user)
        sample_recipe(user_2)   

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serialized = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serialized.data)

    def test_view_recipe_detail(self):
        ''' Teste de apresentação de detalhe de Recipe '''
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)