import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый заголовок',
            image=SimpleUploadedFile(
                name='small.gif',
                content=cls.small_gif,
                content_type='image/gif')
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый текст',
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post_form(self):
        """Форма PostForm при создании поста работает корректно."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data.get('text'),
            ).exists()
        )

    def test_edit_post_form(self):
        """Форма PostForm редактирует корректно."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Новый заголовок',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.id},),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args={self.post.id},)
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=form_data['text']
            ).exists())

    def test_add_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комент'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args={self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', args={self.post.id},)
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text']
            ).exists())

    def test_create_post_image(self):
        post_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'image': self.post.image
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostFormTests.post.author,
                text=PostFormTests.post.text,
                image=PostFormTests.post.image
            ).exists()
        )
