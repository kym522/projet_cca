from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)


from .models import Article, Commentaire


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("titre", "auteur", "date_creation", "publie")
    prepopulated_fields = {"slug": ("titre",)}
    list_filter = ("publie", "date_creation")
    search_fields = ("titre", "contenu")


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ("article", "auteur", "parent", "date_creation")
    list_filter = ("date_creation",)
    search_fields = ("contenu",)
    
from django.contrib import admin
from .models import InscriptionAccompagnement

@admin.register(InscriptionAccompagnement)
class InscriptionAccompagnementAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'formule', 'niveau', 'email', 'telephone', 'date_creation', 'traite')
    list_filter = ('formule', 'niveau', 'traite')
    search_fields = ('nom_complet', 'email', 'telephone')
    readonly_fields = ('date_creation',)