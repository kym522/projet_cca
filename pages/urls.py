from django.urls import path
from . import views
app_name = "pages"

urlpatterns = [
    path('', views.home, name='home'),
    path('a-propos/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('formation/', views.formation, name='formation'),
    path('accompagnement/', views.accompagnement, name='accompagnement'),
    path('ebook/', views.ebook, name='ebook'),
    # ---- Page unique connexion / inscription ----
    path(
        'auth/',
        views.auth_view,
        name='auth'
    ),

    # ---- Déconnexion ----
    path(
        'auth/logout/',
        views.logout_view,
        name='logout'
    ),

    # ---- Mot de passe oublié — envoi email ----
    path(
        'auth/password-reset/',
        views.password_reset_view,
        name='password_reset'
    ),

    # ---- Confirmation nouveau mot de passe ----
    path(
        'auth/password-reset-confirm/<str:uidb64>/<str:token>/',
        views.password_reset_confirm_view,
        name='password_reset_confirm'
    ),

    # ---- Profil utilisateur ----
    path(
        'profile/',
        views.profile_view,
        name='profile'
    ),
    path("article_liste", views.article_liste, name="article_liste"),
    path("nouveau/", views.article_creer, name="article_creer"),
    path("<slug:slug>/", views.article_detail, name="article_detail"),
    path(
        "<slug:slug>/commenter/",
        views.commentaire_ajouter,
        name="commentaire_ajouter",
    ),
    path(
        "commentaire/<int:pk>/like/",
        views.commentaire_like_toggle,
        name="commentaire_like_toggle",
    ),
    path('accompagnement/inscription/<str:formule>/', views.inscription_accompagnement, name='inscription_accompagnement'),
    path('accompagnement/inscription/succes/', views.inscription_success, name='inscription_success'),
    path('gestion/inscriptions/', views.dashboard_inscriptions, name='dashboard_inscriptions'),
    path('gestion/inscriptions/<int:pk>/toggle/', views.toggle_inscription_traite, name='toggle_inscription_traite'),
]