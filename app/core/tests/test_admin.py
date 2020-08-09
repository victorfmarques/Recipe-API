from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@admin.com',
            password='senha123'
            )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create(
            email='test@admin.com',
            password='teste123',
            name='Testevaldo Testado'
            )

    def test_user_listed(self):
        ''' Testa a listagem de usuários '''
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)


    def test_user_change_page(self):
        ''' Teste da página de edição de usuários '''    
        url = reverse('admin:core_user_change', args = [self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)


    def test_create_user_page(self):
        ''' Teste da página de criação de usuários '''
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)