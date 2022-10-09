from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый заголовок',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_task_list_url_redirect_anonymous_on_login(self):
        """Страница по адресу create перенаправит анонимного
        пользователя на страницу логина."""
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/')
        )

    def test_guest_url_exists_at_desired_location(self):
        """Страницы доступа любому пользователю."""
        url_names_http_status = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}': HTTPStatus.OK,
            f'/profile/{self.post.author}': HTTPStatus.OK,
            f'/posts/{self.post.id}': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for adress, httpstatus in url_names_http_status.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress, follow=True)
                self.assertEqual(response.status_code, httpstatus)

    def test_authorized_user_create_post(self):
        """Страница доступа к созданию поста."""
        response = self.authorized_client.get('/create/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_edit_post(self):
        """Страница доступа к редактированию поста."""
        self.post_author = Client()
        self.post_author.force_login(self.post.author)
        response = self.post_author.get(
            f'/posts/{self.post.id}/edit', follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_page_404(self):
    #         response = self.guest_client.get('/qwerty12345/')
    #         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)