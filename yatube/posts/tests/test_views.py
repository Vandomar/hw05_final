from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый заголовок',
            image=SimpleUploadedFile(
                name='small.gif',
                content=cls.small_gif,
                content_type='image/gif')
        )
        cls.post_none_group = Post.objects.create(
            author=cls.user,
            text='Тестовый заголовок',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый текст',
            author=cls.user
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_cache_index(self):
        """Тестирование кэша страницы index.html"""
        cache.clear()
        response_first = self.authorized_client.get(
            reverse('posts:index')
        )
        first_object = Post.objects.get(id=1)
        first_object.text = 'Измененный заголовок'
        first_object.save()
        response_second = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(response_first.content, response_second.content)
        cache.clear()
        response_third = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(response_first.content, response_third.content)

    def test_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertEqual(
            len(response.context['page_obj'].object_list), 2
        )
        first_object = response.context['page_obj'][0]
        if first_object.id != self.post.id:
            first_object = response.context['page_obj'][1]
            post_id = first_object.id
            post_text_0 = first_object.text
            post_author_0 = first_object.author
            post_image_0 = first_object.image
            self.assertEqual(post_text_0, self.post.text)
            self.assertEqual(post_author_0, self.post.author)
            self.assertEqual(post_image_0, self.post.image)
            self.assertEqual(post_id, self.post.id)

    def test_group_post_context(self):
        """Шаблон group_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(
            len(response.context['page_obj'].object_list), 1
        )
        first_object = response.context['page_obj'][0]
        post_id = first_object.id
        post_group_0 = first_object.group.title
        post_group_image_0 = first_object.image
        self.assertEqual(post_group_0, self.post.group.title)
        self.assertEqual(post_group_image_0, self.post.image)
        self.assertEqual(post_id, self.post.id)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        self.assertEqual(
            len(response.context['page_obj'].object_list), 2
        )
        first_object = response.context['page_obj'][0]
        second_object = response.context['page_obj'][1]
        if first_object.id != self.post.id:
            first_object = response.context['page_obj'][1]
            second_object = response.context['page_obj'][0]
            post_id_0 = first_object.id
            post_id_1 = second_object.id
            author_post_0 = first_object.author
            author_post_1 = second_object.author
            post_image_0 = first_object.image
            self.assertEqual(author_post_0, author_post_1)
            self.assertEqual(post_id_0, self.post.id)
            self.assertEqual(post_id_1, self.post_none_group.id)
            self.assertEqual(post_image_0, self.post.image)

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['post']
        post_id = first_object.id
        post_image_0 = first_object.image
        self.assertEqual(post_id, self.post.id)
        self.assertEqual(post_image_0, self.post.image)

    def test_post_create_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_task_list_url_redirect_anonymous_on_login(self):
        """Страница по адресу create перенаправит анонимного
        пользователя на страницу логина."""
        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}))
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )


class FollowerViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.un_follower = User.objects.create_user(username='un_Follower')
        cls.author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый заголовок автора',
        )
        cls.anoter_post = Post.objects.create(
            author=cls.un_follower,
            text='Тестовый заголовок',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.follower)
        cls.authorized_un_follower = Client()
        cls.authorized_un_follower.force_login(cls.un_follower)
        cache.clear()

    def test_follow(self):
        """Показывает посты зафоловленного автора"""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}))
        self.assertEqual(Follow.objects.count(), 1)

    def test_un_follow(self):
        """ Проверка отписки от автора"""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}))
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}))
        self.assertEqual(Follow.objects.count(), 0)

    def show_follow_post(self):
        """Показывает посты в ленте подписок"""
        Follow.objects.create(user=self.follower,
                              author=self.author)
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}))
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index')
        )
        post_text_0 = response.context["page_obj"][0].text
        self.assertEqual(post_text_0, self.post.text)
        response = self.authorized_un_follower.get(
            reverse(
                'posts:follow_index')
        )
        self.assertNotContains(
            response, self.post.text or self.anoter_post.text
        )
