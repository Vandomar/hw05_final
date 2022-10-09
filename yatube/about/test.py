from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_author_url_uses_correct_template(self):
        """Страница по адресу / использует шаблон about/author.html."""
        response = self.authorized_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_url_uses_correct_template(self):
        """Страница по адресу / использует шаблон about/author.html."""
        response = self.authorized_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')
