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

    def test_create_basic_recipe(self):
        ''' Teste de criação de Recipe '''
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
    
    def test_create_recipe_with_tags(self):
        ''' Teste criando uma Recipe com Tags '''
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes' : 60,
            'price':20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        ''' Teste criando uma Recipe com Ingredients '''
        ingredient1 = sample_ingredient(user=self.user, name='picanha')
        ingredient2 = sample_ingredient(user=self.user, name='alho')
        payload = {
            'title': 'Picanha com alho',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 15,
            'price': 30.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_patch_update_recipe(self):
        ''' Testa o update de dados de uma Recipe com o verbo HTTP PATCH '''
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user)) 
        tag_atualizada = sample_tag(user=self.user, name="tag_atualizada")

        payload = {
            'title': 'Title novo de Recipe',
            'tags': [tag_atualizada.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(tag_atualizada, tags)

    def test_put_update_recipe(self):
        ''' Testa o update de dados de uma Recipe com o verbo HTTP PUT '''
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'titulo 10/10',
            'time_minutes': 60,
            'price': 10
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])

        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)