from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def home(request):
    return render(request, 'pages/home.html')

def about(request):
    return render(request, 'pages/about.html')

def formation(request):
    return render(request, 'pages/formations.html')
def accompagnement(request):
    return render(request, 'pages/accompagnement.html')

def ebook(request):
    return render(request, 'pages/ebook.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a été envoyé avec succès !")
            return redirect('contact')
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {'form': form})



from django.shortcuts           import render, redirect
from django.contrib.auth        import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib             import messages
from django.views.decorators.http import require_http_methods
from django.core.mail           import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http          import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding      import force_bytes, force_str
from django.template.loader     import render_to_string
from django.conf                import settings

from .models import User
from .forms  import RegisterForm, LoginForm, ForgotPasswordForm
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


# ============================================================
#  VUE PRINCIPALE — page auth (connexion + inscription)
#  GET  → affiche la page avec les deux formulaires
#  POST → traite selon form_type (login | register)
# ============================================================

def auth_view(request):
    """
    Une seule URL, un seul template.
    Le champ caché form_type détermine quelle action traiter.
    """

    # Si déjà connecté → redirige vers l'accueil
    if request.user.is_authenticated:
        return redirect('home')

    register_form = RegisterForm()
    login_form    = LoginForm()
    active_tab    = 'login'   # panneau affiché par défaut

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # ---- CONNEXION ----
        if form_type == 'login':
            active_tab = 'login'
            login_form = LoginForm(request.POST)

            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, f"Bon retour, {user.first_name} 👋")

                next_url = request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect('pages:home')
            else:
                messages.error(request, "Email ou mot de passe incorrect.")

        # ---- INSCRIPTION ----
        elif form_type == 'register':
            active_tab    = 'register'
            register_form = RegisterForm(request.POST)

            if register_form.is_valid():
                user = register_form.save()
                # Connexion automatique après inscription
                login(request, user)
                messages.success(
                    request,
                    f"Bienvenue sur Challenge Code Academy, {user.first_name} 🚀 "
                    f"Ton compte a été créé avec succès."
                )
                return redirect('pages:home')
            else:
                # Affiche les erreurs champ par champ
                for field, errors in register_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")

    context = {
        'register_form': register_form,
        'login_form':    login_form,
        'active_tab':    active_tab,
    }
    return render(request, 'pages/auth.html', context)


# ============================================================
#  DÉCONNEXION
# ============================================================

@require_http_methods(["POST", "GET"])
def logout_view(request):
    logout(request)
    messages.success(request, "Tu as été déconnecté avec succès.")
    return redirect('pages:auth')


# ============================================================
#  MOT DE PASSE OUBLIÉ — envoi du lien par email
# ============================================================

def password_reset_view(request):
    """
    Reçoit l'email, génère un token sécurisé et envoie le lien.
    Ne révèle pas si l'email existe (sécurité anti-enumération).
    """
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                user = User.objects.get(email=email)
                # Génération du token et de l'UID
                uid   = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)

                # Construction du lien
                reset_url = request.build_absolute_uri(
                    f"/auth/password-reset-confirm/{uid}/{token}/"
                )

                # Envoi de l'email
                subject = "Réinitialisation de ton mot de passe — Challenge Code Academy"
                message = render_to_string('emails/password_reset.html', {
                    'user':      user,
                    'reset_url': reset_url,
                })
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                    html_message=message,
                )

            except User.DoesNotExist:
                pass   # silencieux pour ne pas révéler l'existence du compte

            # Message neutre dans tous les cas
            messages.success(
                request,
                "Si cet email est associé à un compte, tu recevras un lien "
                "de réinitialisation dans quelques minutes."
            )
            return redirect('auth')

    return redirect('auth')


# ============================================================
#  CONFIRMATION DU NOUVEAU MOT DE PASSE
#  URL : /auth/password-reset-confirm/<uidb64>/<token>/
# ============================================================

def password_reset_confirm_view(request, uidb64, token):
    """
    Vérifie le token, affiche le formulaire de nouveau mot de passe.
    """
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    token_valid = user is not None and default_token_generator.check_token(user, token)

    if request.method == 'POST' and token_valid:
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if len(password1) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
        elif password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            user.set_password(password1)
            user.save()
            messages.success(
                request,
                "Mot de passe modifié avec succès ! Tu peux maintenant te connecter."
            )
            return redirect('auth')

    context = {
        'token_valid': token_valid,
        'uidb64':      uidb64,
        'token':       token,
    }
    return render(request, 'pages/password_reset_confirm.html', context)


# ============================================================
#  VUE PROFIL UTILISATEUR (protégée)
# ============================================================

@login_required(login_url='auth')
def profile_view(request):
    """
    Profil de l'utilisateur connecté.
    Permet aussi de modifier les informations.
    """
    user = request.user

    if request.method == 'POST':
        first_name    = request.POST.get('first_name', '').strip()
        last_name     = request.POST.get('last_name',  '').strip()
        phone_country = request.POST.get('phone_country', user.phone_country)
        phone_number  = request.POST.get('phone_number',  '').strip()

        if first_name:
            user.first_name    = first_name
        if last_name:
            user.last_name     = last_name
        user.phone_country = phone_country
        user.phone_number  = phone_number
        user.save()
        messages.success(request, "Profil mis à jour avec succès.")
        return redirect('profile')

    return render(request, 'pages/profile.html', {'user': user})
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ArticleForm, CommentaireForm
from .models import Article, Commentaire


def article_liste(request):
    articles = Article.objects.filter(publie=True).select_related("auteur")
    return render(request, "blog/article_liste.html", {"articles": articles})


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("auteur"), slug=slug, publie=True
    )
    form = CommentaireForm()
    return render(
        request,
        "blog/article_detail.html",
        {
            "article": article,
            "commentaires": article.commentaires_racine,
            "form": form,
        },
    )


@login_required
def article_creer(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            article.save()
            return redirect(article.get_absolute_url())
    else:
        form = ArticleForm()
    return render(request, "blog/article_form.html", {"form": form})


@login_required
@require_POST
def commentaire_ajouter(request, slug):
    """Ajoute un commentaire racine ou une réponse (si parent_id fourni)."""
    article = get_object_or_404(Article, slug=slug, publie=True)
    form = CommentaireForm(request.POST)

    parent = None
    parent_id = request.POST.get("parent_id")
    if parent_id:
        parent = get_object_or_404(Commentaire, pk=parent_id, article=article)

    if form.is_valid():
        commentaire = form.save(commit=False)
        commentaire.article = article
        commentaire.auteur = request.user
        commentaire.parent = parent
        commentaire.save()

    return redirect(article.get_absolute_url())


@login_required
@require_POST
def commentaire_like_toggle(request, pk):
    """Toggle like/unlike sur un commentaire, réponse JSON pour l'AJAX."""
    commentaire = get_object_or_404(Commentaire, pk=pk)
    user = request.user

    if commentaire.likes.filter(pk=user.pk).exists():
        commentaire.likes.remove(user)
        liked = False
    else:
        commentaire.likes.add(user)
        liked = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"liked": liked, "nb_likes": commentaire.nb_likes})

    return redirect(commentaire.article.get_absolute_url())



from django.shortcuts import render, redirect
from .forms import InscriptionAccompagnementForm


FORMULE_INFO = {
    'starter': {'nom': 'Starter', 'prix': 'Gratuit'},
    'pro': {'nom': 'Pro', 'prix': '15 000 FCFA / mois'},
    'elite': {'nom': 'Elite', 'prix': '30 000 FCFA / mois'},
}

def inscription_success(request):
    return render(request, 'pages/inscription_success.html')


def inscription_accompagnement(request, formule):
    if formule not in FORMULE_INFO:
        formule = 'starter'

    if request.method == 'POST':
        form = InscriptionAccompagnementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pages:inscription_success')
    else:
        form = InscriptionAccompagnementForm(initial={'formule': formule})

    context = {
        'form': form,
        'formule': formule,
        'formule_info': FORMULE_INFO[formule],
    }
    return render(request, 'pages/inscription_accompagnement.html', context)



from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import InscriptionAccompagnement


@staff_member_required
def dashboard_inscriptions(request):
    inscriptions = InscriptionAccompagnement.objects.all()

    formule_filter = request.GET.get('formule')
    if formule_filter:
        inscriptions = inscriptions.filter(formule=formule_filter)

    statut_filter = request.GET.get('statut')
    if statut_filter == 'traite':
        inscriptions = inscriptions.filter(traite=True)
    elif statut_filter == 'non_traite':
        inscriptions = inscriptions.filter(traite=False)

    context = {
        'inscriptions': inscriptions,
        'total': InscriptionAccompagnement.objects.count(),
        'total_non_traite': InscriptionAccompagnement.objects.filter(traite=False).count(),
        'total_starter': InscriptionAccompagnement.objects.filter(formule='starter').count(),
        'total_pro': InscriptionAccompagnement.objects.filter(formule='pro').count(),
        'total_elite': InscriptionAccompagnement.objects.filter(formule='elite').count(),
        'formule_filter': formule_filter,
        'statut_filter': statut_filter,
    }
    return render(request, 'pages/dashboard_inscriptions.html', context)


@staff_member_required
def toggle_inscription_traite(request, pk):
    inscription = get_object_or_404(InscriptionAccompagnement, pk=pk)
    if request.method == 'POST':
        inscription.traite = not inscription.traite
        inscription.save()
        messages.success(request, f"Statut mis à jour pour {inscription.nom_complet}.")
    return redirect('pages:dashboard_inscriptions')
