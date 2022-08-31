
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newpost", views.newPost, name="newPost"),
    path("profile/<int:user_id>", views.profile_view, name="profile"),
    path("following", views.following_view, name="following"),

    path("likes/<int:post_id>", views.is_liked, name="is_liked"),
    path("follows/<int:profile_id>", views.is_follower, name="is_follower"),
    path("edit/<int:post_id>", views.edit, name="edit")
]
