from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        ''' Teste criando um novo usuário com um email com sucesso'''

        email = 'email@test.com'
        password = 'Testpassword123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normalize(self):
        ''' Teste de normalização do usuário após criação '''

        email = 'email@TEST.com'
        user = get_user_model().objects.create_user(email, 'TESTE123')
        self.assertEqual(user.email, email.lower())

    
    def test_new_user_invalid_email(self):
        ''' Teste de criação de usuário com nenhum email '''

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'teste123')


    def test_create_superuser(self):
        ''' Teste de criação de super usuário '''
        user = get_user_model().objects.create_superuser(
            email = 'email@email.com',
            password = 'senha123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

        