from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("create", views.create, name="create"),
    path("edit", views.edit, name="edit"),
    path("random", views.random_page, name="random_page"),
    path("<str:title>", views.open_entry, name="open_entry")
]
