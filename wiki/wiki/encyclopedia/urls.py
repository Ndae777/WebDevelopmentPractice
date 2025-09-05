from django.urls import path

from . import views

urlpatterns = [
    path("random", views.random_entry , name="random"),
    path("edit/<str:entry>", views.edit, name="edit"),
    path("search", views.search , name="search"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("newpage", views.newpage, name="newpage"),
    path("", views.index, name="index")
]
