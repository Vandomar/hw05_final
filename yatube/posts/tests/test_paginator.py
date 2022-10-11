from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст')
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый заголовок')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_paginator(self):
        '''Проверка работы Пагинатора'''
        for post in range(11):
            post = Post.objects.create(
                text=f'Тестовый текст {post}',
                author=self.user,
                group=self.group,
            )
        posturls_posts_page = [
            ('', settings.AMOUNT_POSTS),
            ('?page=2', Post.objects.count() % settings.AMOUNT_POSTS)
        ]
        templates = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for postsurls, posts in posturls_posts_page:
            for page in templates:
                with self.subTest(page=page):
                    response = self.authorized_client.get(page + postsurls)
                    self.assertEqual(len(response.context['page_obj']), posts)
