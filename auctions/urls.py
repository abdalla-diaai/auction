from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("edit/<int:listing_id>/", views.edit, name="edit"),
    path("delete/<int:listing_id>/", views.delete, name="delete"),
    path("add_watchlist/<int:listing_id>/", views.add_watchlist, name="add_watchlist"),
    path("view/<int:listing_id>", views.view, name="view"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("unwatch/<int:listing_id>/", views.unwatch, name="unwatch"),
    path("categories", views.categories, name="categories"),
    path("categories_view/<str:subcat>/", views.categories_view, name="categories_view"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("end/<int:listing_id>", views.end, name="end"),
    path("buy/<int:listing_id>/", views.buy, name="buy"),
]
