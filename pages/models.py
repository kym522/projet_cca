from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Adresse e-mail")
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"



from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# ============================================================
#  MANAGER UTILISATEUR PERSONNALISÉ
# ============================================================

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',     True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active',    True)
        return self.create_user(email, password, **extra_fields)


# ============================================================
#  MODÈLE UTILISATEUR — remplace le User Django par défaut
# ============================================================

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField("Prénom",            max_length=60)
    last_name  = models.CharField("Nom",               max_length=60)
    username   = models.CharField("Nom d'utilisateur", max_length=40, unique=True)
    email      = models.EmailField("Email",             unique=True)

    phone_country = models.CharField("Indicatif pays", max_length=6, default="+228")
    phone_number  = models.CharField("Numéro",         max_length=20, blank=True)

    is_active   = models.BooleanField("Actif",  default=True)
    is_staff    = models.BooleanField("Staff",  default=False)
    date_joined = models.DateTimeField("Date inscription", auto_now_add=True)

    # ✅ CES DEUX LIGNES CORRIGENT L'ERREUR
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='pages_user_set',   # ← nom unique, différent du User Django
        related_query_name='pages_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='pages_user_set',   # ← nom unique
        related_query_name='pages_user',
    )

    objects        = UserManager()
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name        = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_phone_full(self):
        return f"{self.phone_country} {self.phone_number}".strip()

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"



from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Article(models.Model):
    titre = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    contenu = models.TextField()
    image = models.ImageField(upload_to="articles/", blank=False, null=False, help_text="Image illustrative obligatoire pour l'article.")
    date_creation = models.DateTimeField(default=timezone.now)
    date_maj = models.DateTimeField(auto_now=True)
    publie = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("pages:article_detail", kwargs={"slug": self.slug})

    @property
    def nb_commentaires(self):
        return self.commentaires.count()

    @property
    def commentaires_racine(self):
        # Seulement les commentaires de premier niveau (les réponses sont
        # accédées via .reponses dans le template, en récursif)
        return self.commentaires.filter(parent__isnull=True).select_related(
            "auteur"
        ).prefetch_related("reponses__auteur", "likes")


class Commentaire(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="commentaires"
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commentaires",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reponses",
    )
    contenu = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="commentaires_likes",
        blank=True,
    )

    class Meta:
        ordering = ["date_creation"]

    def __str__(self):
        return f"{self.auteur} sur {self.article} : {self.contenu[:30]}"

    @property
    def nb_likes(self):
        return self.likes.count()

    def est_like_par(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(pk=user.pk).exists()

    @property
    def est_reponse(self):
        return self.parent_id is not None

from django.db import models


class InscriptionAccompagnement(models.Model):

    FORMULE_CHOICES = [
        ('starter', 'Starter — Gratuit'),
        ('pro', 'Pro — 15 000 FCFA/mois'),
        ('elite', 'Elite — 30 000 FCFA/mois'),
    ]

    NIVEAU_CHOICES = [
        ('debutant', 'Débutant'),
        ('intermediaire', 'Intermédiaire'),
        ('avance', 'Avancé'),
    ]

    DISPONIBILITE_CHOICES = [
        ('matin', 'Matin'),
        ('apres_midi', 'Après-midi'),
        ('soir', 'Soir'),
        ('weekend', 'Weekend'),
    ]

    formule = models.CharField(max_length=20, choices=FORMULE_CHOICES)
    nom_complet = models.CharField(max_length=150)
    email = models.EmailField()
    telephone = models.CharField(max_length=30)
    ville_pays = models.CharField(max_length=150, blank=True)

    domaines = models.CharField(
        max_length=255,
        help_text="Domaines choisis, séparés par des virgules"
    )
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES)
    disponibilite = models.CharField(max_length=20, choices=DISPONIBILITE_CHOICES)

    attentes = models.TextField(
        verbose_name="Attentes et objectifs",
        help_text="Décris tes attentes, tes objectifs et ce que tu souhaites obtenir de cet accompagnement."
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False, verbose_name="Traité par l'équipe")

    class Meta:
        verbose_name = "Inscription accompagnement"
        verbose_name_plural = "Inscriptions accompagnement"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom_complet} — {self.get_formule_display()}"