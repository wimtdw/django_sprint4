from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone

from .forms import (CreatePostForm, EditPostForm, EditProfileForm,
                    AddCommentForm)
from .models import Category, Comment, Post
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count

User = get_user_model()


def get_posts(is_author=False, profile=False, user=None):
    now = timezone.now()
    if is_author and profile:

        posts = Post.objects.select_related('category', 'location').filter(
            author=user
        )
    elif is_author and not profile:
        posts = Post.objects.select_related('category', 'location').filter(
        )
    elif not is_author and profile:
        posts = Post.objects.select_related('category', 'location').filter(
            author=user,
            pub_date__lte=now,
            is_published=True,
            category__is_published=True
        )
    else:
        posts = Post.objects.select_related('category', 'location').filter(
            pub_date__lte=now,
            is_published=True,
            category__is_published=True
        )
    return posts


def get_post(user, post_id, is_author=False):
    if is_author:
        post = get_object_or_404(get_posts(is_author=True), pk=post_id)
    else:
        post = get_object_or_404(get_posts(is_author=False), pk=post_id)
    return post


def index(request):
    template = 'blog/index.html'
    posts = get_posts().annotate(
        comment_count=Count('comments')).order_by('-pub_date', 'title')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    author = get_object_or_404(Post, pk=post_id).author
    user = get_object_or_404(User, pk=request.user.id)
    if user != author:
        post = get_post(user, post_id)
    else:
        post = get_post(user, post_id, is_author=True)
    context = {'post': post}
    context['form'] = AddCommentForm()
    context['comments'] = (
        Comment.objects.filter(post=post)
    ).select_related('author')
    return render(request, template, context)


@login_required
def create_post(request):
    template = 'blog/create.html'
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST':
        form = CreatePostForm(request.POST, user=user, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('blog:profile',
                                         args=[(user.get_username())]))
    else:
        form = CreatePostForm(user=user)

    return render(request, template, {'form': form})


@login_required
def edit_post(request, post_id):
    user = get_object_or_404(User, pk=request.user.id)
    post_1 = get_object_or_404(Post, pk=post_id)
    if post_1.author != user:
        return redirect(reverse_lazy('blog:post_detail', args=[(post_id)]))
    post = get_post(user, post_id, is_author=True)
    template = 'blog/create.html'
    if request.method == 'POST':
        form = EditPostForm(request.POST, instance=post, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('blog:post_detail', args=[(post_id)]))
    else:
        form = EditPostForm(instance=post)
    return render(request, template, {'form': form})


@login_required
def delete_post(request, post_id):
    user = get_object_or_404(User, pk=request.user.id)
    post_1 = get_object_or_404(Post, pk=post_id)
    if post_1.author != user:
        return redirect(reverse_lazy('blog:post_detail', args=[(post_id)]))
    post = get_post(user, post_id, is_author=True)
    template = 'blog/create.html'
    form = CreatePostForm(instance=post)
    context = {'form': form}
    if request.method == 'POST':
        post.delete()
        return redirect(reverse_lazy('blog:profile', args=[user.username]))
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True,
        ),
        slug=category_slug
    )
    now = timezone.now()
    posts = category.posts.select_related('location').filter(
        pub_date__lte=now,
        is_published=True,
    ).annotate(
        comment_count=Count('comments')).order_by('-pub_date', 'title')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    template = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)
    if profile.id == request.user.id:
        posts = get_posts(is_author=True, profile=True, user=profile).annotate(
            comment_count=Count('comments')).order_by('-pub_date', 'title')
    else:
        posts = get_posts(profile=True, user=profile).annotate(
            comment_count=Count('comments')).order_by('-pub_date', 'title')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, template, context)


@login_required
def edit_profile(request):
    template = 'blog/user.html'
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('blog:profile',
                                         args=[(user.get_username())]))
    else:
        form = EditProfileForm(instance=user)
    return render(request, template, {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = AddCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    user = get_object_or_404(User, pk=request.user.id)
    comment_1 = get_object_or_404(Comment, pk=comment_id)
    if comment_1.author != user:
        return redirect(reverse_lazy('blog:post_detail', args=[(post_id)]))
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        form = AddCommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = comment.post
            comment.save()
            return redirect(reverse_lazy('blog:post_detail', args=[(post_id)]))
    else:
        form = AddCommentForm(instance=comment)
    return render(request, 'blog/comment.html', {'form': form,
                                                 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    user = get_object_or_404(User, pk=request.user.id)
    comment_1 = get_object_or_404(Comment, pk=comment_id)
    if comment_1.author != user:
        return redirect(reverse_lazy('blog:post_detail', args=[(post_id)]))
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        comment.delete()
        return redirect(reverse_lazy('blog:post_detail', args=[(post_id)]))
    return render(request, 'blog/comment.html', {'comment': comment})
