from django.test import TestCase

from posts.models import Group, Post, User, Comment

SLUG = 'Тестовая ссылка группы'
USERNAME = 'Тестовый автор'


class YatubePostsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        '''Создание тестовых записей в БД'''
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug=SLUG,
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст Комментария'
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор поста',
            'group': 'Тег группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)
        group = self.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Ссылка',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)
        comment = self.comment
        field_verboses = {
            'post': 'Ссылка на пост',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_texts = {
            'group': 'Ключ для построения ссылки'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
        group = self.group
        field_help_texts = {
            'slug': 'Задайте ссылку на вашу группу'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field(self):
        '''__str__  comment - строка с comment.text.'''
        comment = self.comment
        expected_object_name = comment.text
        self.assertEquals(expected_object_name, str(comment))

    def test_object_name_is_title_field(self):
        '''__str__  group - строка с group.title.'''
        group = self.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))

    def test_object_name_is_text_field(self):
        '''__str__  post - строка с post.text.'''
        post = self.post
        expected_object_name = post.text
        self.assertEquals(expected_object_name, str(post))
