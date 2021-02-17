from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from yatube.settings import POSTS, CACHE_S
from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm


@cache_page(CACHE_S)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'paginator': paginator,
        'page': page,
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'group': group,
        'paginator': paginator,
        'page': page,
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if not form.is_valid():
        return render(request, 'new.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:index')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    context = {
        'author': author,
        'paginator': paginator,
        'page': page,
        'following': following
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    comments = post.comments.all()
    form = CommentForm()
    following = (
        request.user.is_authenticated
        and request.user != author
        and author.following.filter(user=request.user, author=author).exists()
    )
    context = {
        'author': author,
        'form': form,
        'post': post,
        'comments': comments,
        'following': following
    }
    return render(request, 'post.html', context)


@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post', username, post_id)


@login_required
def post_edit(request, username, post_id):
    if not request.user.username == username:
        return redirect('posts:post', username, post_id)
    post = Post.objects.get(id=post_id, author=request.user)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post',
                        username=post.author.username, post_id=post.id)
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'new.html', context)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):
    follow_posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(follow_posts, POSTS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'paginator': paginator,
        'page': page,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=author.username)
