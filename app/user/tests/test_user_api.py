from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    ''' Teste user API '''
    
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        ''' Teste de criação de usuário com formato correto '''
        payload = {
            'email': 'email@teste.com',
            'password': 'testedesenha123',
            'name': 'nome do teste',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        ''' Teste de criação de usuário já existente '''
        payload = {
            'email': 'email@teste.com',
            'password': 'testedesenha123',
            'name': 'nome do teste',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        ''' Teste de validação de quantidade de caracteres na senha '''
        payload = {
            'email': 'email@teste.com',
            'password': 'test',
            'name': 'nome do teste',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        ''' Teste se o token criado é para o usuário '''
        payload = {
            'email': 'email@teste.com',
            'password': 'testee'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_create_token_invalid_credentials(self):
        ''' Teste de criação de token para usuário inválido '''
        create_user(email='test@test.com', password='tesetee')
        payload = {
            'email': 'test@test.com',
            'password': 'incorrectpwd'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        ''' Teste de criação de token para usuário inexistente'''
        payload = {
            'email': 'email@teste.com',
            'password': 'senha123'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        ''' Teste para criação de token para campos em brancos enviados '''
        res = self.client.post(TOKEN_URL, {'email': 'one@email.com', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unothorized(self):
        ''' Teste para criação de token para usuário não cadastrado '''
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    ''' Testes de usuários que necessitam de autenticação '''

    def setUp(self):
        self.user = create_user(
            email = 'email@email.com',
            password = 'testpass',
            name='name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        ''' Teste retornando um perfil para o login utilizado '''
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name' : self.user.name,
            'email': self.user.email
        })

    
    def test_post_me_not_allowed(self):
        ''' Teste aonde prova que um POST não é permitido na URL '''
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    
    def test_update_user_profile(self):
        ''' Teste atualizando o perfil do usuário para um usuário autenticado'''
        payload = {'name': 'nome novo', 'password': 'novasenha2222'}
        
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    