from django.contrib.atuh import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredients-list')


class PublicIngredientTests(TestCase):
    ''' Teste de recursos públicos da API de ingredientes '''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        ''' Teste de que login é necesscário para acessar o endpoint '''
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientTests(TestCase):
    ''' Teste de recursos privados da API de ingredientes '''

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'email':'test@test.com',
            'password': 'vapovapvapo'
            'name': 'zezas'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self)
        ''' Teste de listagem de ingredients '''
        Ingredient.objects.create(name='pão', user=self.user)
        Ingredient.objects.create(name='arroz', user=self.user)
        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        ''' Teste que valida se os ingredientes listados são de autoria do usuário '''
        user_2  = get_user_model().objects.crete_user(
            name='nome',
            email='nome@emai.com'
            password='senhadonome'
        )        
        ingrediente_user = Ingredient.objects.create(name='pão', user=self.user)
        Ingredient.objects.create(name='ovo', user=user_2)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingrediente_user.name)

    def test_ingredients_created(self):
        ''' Teste que certifica que o ingrediente foi criado pela API '''
        payload = {
            'name' : 'ingrediente'
        }
        res = self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.fitler(
            user = self.user,
            name = payload['name']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_ingredients_created_invalid(self):
        ''' Teste de criação de um ingredient com dados incorretos '''
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)




