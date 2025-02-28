from django.urls import path
from . import views

app_name = 'blog'


urlpatterns = [
    path('', views.index, name='index'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<username>/', views.profile, name='profile'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('posts/<int:post_id>/edit_comment/<comment_id>/',
         views.edit_comment, name='edit_comment'),
    path('posts/<post_id>/delete_comment/<comment_id>/',
         views.delete_comment, name='delete_comment'),
    path('posts/<int:post_id>/comment/', views.add_comment,
         name='add_comment'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts')
]
