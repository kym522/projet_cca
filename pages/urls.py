from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('a-propos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('formation/', views.formation, name='formation'),
    path('accompagnement/', views.accompagnement, name='accompagnement'),
    path('ebook/', views.ebook, name='ebook'),
]