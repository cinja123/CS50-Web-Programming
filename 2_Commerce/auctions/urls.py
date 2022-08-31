from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("auction/<int:auction_id>", views.auction_view, name="auction"),
    path("create", views.create_auction, name="create"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("watchlist/<int:auction_id>", views.watchlist_add, name="watchlist_add"),
    path("bid/<int:auction_id>", views.bid, name="bid"),
    path("close_auction", views.close_auction, name="close_auction"),
    path("comment_auction/<int:auction_id>", views.comment_auction, name="comment_auction"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category_view, name="category_view")
]
