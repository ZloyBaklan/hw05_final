from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from yatube.settings import POSTS
from posts.models import Group, Post, User, Comment, Follow

INDEX = reverse('posts:index')
FOLLOW_INDEX = reverse('posts:follow_index')
SLUG = 'TestG'
GROUP = reverse('posts:group', kwargs={'slug': SLUG})
SLUG2 = 'group-2'
GROUP2 = reverse('posts:group', kwargs={'slug': SLUG2})
USERNAME = 'Тестовый автор'
USERNAME2 = 'Author'
PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})
FOLLOW = reverse('posts:profile_follow', kwargs={'username': USERNAME})
UNFOLLOW = reverse('posts:profile_unfollow', kwargs={'username': USERNAME})


class YatubePostsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug=SLUG,
            description='Описание тестовой группы',
        )
        cls.group_2 = Group.objects.create(
            title="Другая группа",
            slug=SLUG2,
            description="В этой группе нет постов",
        )

    def setUp(self):
        self.guest_client = Client()
        self.user2 = User.objects.create(username=USERNAME2)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='Текст Комментария'

        )
        self.REVERSE_POST = reverse(
            'posts:post',
            kwargs={'username': self.user.username, 'post_id': self.post.id}
        )
        self.ADD_COMMENT = reverse('posts:add_comment',
                                   args=[self.user.username, self.post.id])

    def test_group_page_show_correct_context(self):
        """Отображение страницы группы"""
        response_group = self.authorized_client.get(GROUP)
        group_test = response_group.context.get('group')
        self.assertEqual(group_test, self.group)

    def test_post_in_url(self):
        cache.clear()
        urls_names = [
            GROUP,
            INDEX,
            PROFILE,
            FOLLOW_INDEX,
        ]
        for value in urls_names:
            with self.subTest(value=value):
                self.authorized_client2.get(FOLLOW)
                response = self.authorized_client2.get(value)
                self.assertEqual(len(response.context['page']), 1)
                self.assertEqual(self.post,
                                 response.context.get('page')[0])

    def test_unfollow_index_page_null(self):
        """Пост не отображается в ленте у отписавшегося"""
        response = self.authorized_client2.get(FOLLOW_INDEX)
        self.assertEqual(len(response.context['page']), 0)

    def test_post_not_in_group2(self):
        """Пост не отображается в другой группе"""
        response_group = self.authorized_client.get(GROUP2)
        self.assertNotIn(self.post, response_group.context.get('page'))

    def test_profile_page_show_correct_context(self):
        """Проверка отображения /<username>/. """
        response = self.authorized_client.get(PROFILE)
        self.assertEqual(self.user, response.context.get('author'))

    def test_post_page_show_correct_context(self):
        """Проверка отображения /<username>/<post_id>/. """
        response = self.authorized_client.get(self.REVERSE_POST)
        self.assertEqual(self.post, response.context.get('post'))
        self.assertEqual(self.user, response.context.get('author'))
        self.assertEqual(len(response.context['comments']), 1)
        self.assertEqual(self.comment, response.context.get('comments')[0])

    def test_follow_user(self):
        """Проверка подписки. """
        self.authorized_client2.get(FOLLOW)
        follow_exist = Follow.objects.filter(user=self.user2,
                                             author=self.user).exists()
        self.assertTrue(follow_exist)

    def test_unfollow_user(self):
        """Проверка отписки. """
        self.authorized_client2.get(FOLLOW)
        self.authorized_client2.get(UNFOLLOW)
        follow_exist = Follow.objects.filter(user=self.user2,
                                             author=self.user).exists()
        self.assertFalse(follow_exist)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')
        posts = [Post(author=cls.user, text=str(i)) for i in range(POSTS)]
        Post.objects.bulk_create(posts)

    def test_page_count_records(self):
        cache.clear()
        response = self.client.get(INDEX)
        self.assertEqual(len(response.context.get('page').object_list), POSTS)
