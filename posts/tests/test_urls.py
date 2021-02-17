from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('posts:index')
URL_404 = reverse('posts:404')
NEW_POST = reverse('posts:new_post')
AUTHOR = reverse('about:author')
TECH = reverse('about:tech')
USERNAME = 'TestAuthor'
USERNAME2 = 'TestAut'
AUTH_LOGIN = reverse('login')
SLUG = 'testgroup'
GROUP_URL = reverse('posts:group', kwargs={'slug': SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
FOLLOW_INDEX = reverse('posts:follow_index')
FOLLOW = reverse('posts:profile_follow', kwargs={'username': USERNAME})
UNFOLLOW = reverse('posts:profile_unfollow', kwargs={'username': USERNAME})


class YatubePostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            slug=SLUG,
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )
        cls.POST_URL = reverse('posts:post',
                               args=[cls.user.username, cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    args=[cls.user.username, cls.post.id])
        cls.ADD_COMMENT_URL = reverse('posts:add_comment',
                                      args=[cls.user.username, cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = User.objects.create(username=USERNAME2)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_urls_uses_correct_template(self):
        cache.clear()
        template_urls_names = [
            ['index.html', INDEX],
            ['new.html', NEW_POST],
            ['group.html', GROUP_URL],
            ['post.html', self.POST_URL],
            ['profile.html', PROFILE_URL],
            ['author.html', AUTHOR],
            ['tech.html', TECH],
            ['new.html', self.POST_EDIT_URL],
            ['follow.html', FOLLOW_INDEX]
        ]
        for template, url in template_urls_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(self.authorized_client.get(url),
                                        template)

    def test_urls_status_code(self):
        urls_names = [
            [self.POST_EDIT_URL, self.authorized_client2, 302],
            [INDEX, self.guest_client, 200],
            [NEW_POST, self.guest_client, 302],
            [GROUP_URL, self.guest_client, 200],
            [self.POST_URL, self.guest_client, 200],
            [PROFILE_URL, self.guest_client, 200],
            [AUTHOR, self.guest_client, 200],
            [TECH, self.guest_client, 200],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.authorized_client, 200],
            [NEW_POST, self.authorized_client, 200],
            [URL_404, self.client, 404],
            [self.ADD_COMMENT_URL, self.guest_client, 302],
            [FOLLOW, self.authorized_client2, 302],
            [UNFOLLOW, self.authorized_client2, 302]
        ]
        for url, client, status in urls_names:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, status)

    def test_redirect_urls_correct(self):
        urls = [
            [NEW_POST, self.guest_client, f'{AUTH_LOGIN}?next={NEW_POST}'],
            [self.POST_EDIT_URL, self.guest_client,
             f'{AUTH_LOGIN}?next={self.POST_EDIT_URL}'],
            [self.POST_EDIT_URL, self.authorized_client2, self.POST_URL],
            [self.ADD_COMMENT_URL, self.guest_client,
             f'{AUTH_LOGIN}?next={self.ADD_COMMENT_URL}'],
            [FOLLOW, self.authorized_client2, PROFILE_URL],
            [UNFOLLOW, self.authorized_client2, PROFILE_URL]
        ]
        for url, client, redirect in urls:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), redirect)
