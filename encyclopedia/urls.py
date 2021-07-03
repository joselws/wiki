from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    
    #title is the particular subject the wiki will display about
    #pass the title variable from the url entry into the title function in views
    path("wiki/<str:title>", views.title, name="title"),
    path("new", views.new, name="new"),
    path("random", views.random, name="random"),
    path("wiki/<str:title>/edit", views.edit, name="edit")
]
