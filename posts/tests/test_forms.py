import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('posts:index')
NEW_POST = reverse('posts:new_post')


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username='TestsAuthor')
        cls.group = Group.objects.create(
            title='Test',
            slug='Tests',
            description='Описание теста',
        )
        cls.group2 = Group.objects.create(
            title='Test2',
            slug='Tests2',
            description='Описание',
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=self.group,
        )
        self.ADD_COMMENT_URL = reverse(
            'posts:add_comment',
            args=[self.user.username, self.post.id])
        self.POST_URL = reverse(
            'posts:post',
            args=[self.user.username, self.post.id])
        self.POST_EDIT_URL = reverse(
            'posts:post_edit',
            args=[self.user.username, self.post.id])

    def test_post_create(self):
        """Корректное отображение созданного поста."""
        post = Post.objects.first()
        post.delete()
        SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        UPLOADED = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст формы',
            'group': self.group.id,
            'image': UPLOADED,
        }
        response = self.authorized_client.post(
            NEW_POST,
            data=form_data,
            follow=True
        )
        post = response.context['page'][0]
        image_data = form_data['image']
        self.assertEqual(len(response.context['page']), 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image.name, f'posts/{image_data.name}')
        self.assertRedirects(response, INDEX)

    def test_new_post_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        urls = [
            NEW_POST,
            self.POST_EDIT_URL
        ]
        for url in urls:
            response = self.authorized_client.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.Field,
                'image': forms.fields.ImageField
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_edit_save(self):
        """Корректное отображение /<username>/<post_id>/edit/. """
        SM_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        UPLOADED = SimpleUploadedFile(
            name='sm.gif',
            content=SM_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Другой текст!',
            'group': self.group2.id,
            'image': UPLOADED,
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data, follow=True
        )
        '''Пост должен поменяться'''
        post = response.context['post']
        image_data = form_data['image']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group2)
        self.assertEqual(post.image.name, f'posts/{image_data.name}')
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(response, self.POST_URL)

    def test_comment_save(self):
        """Корректное отображение комментария."""
        form_data = {
            'text': 'Текст Комментария!',
            'post': self.post.id,
            'author': self.user,
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT_URL,
            data=form_data, follow=True
        )
        self.assertEqual(len(response.context['comments']), 1)
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)
