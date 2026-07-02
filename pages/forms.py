from django import forms
from pages.models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre adresse e-mail'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet du message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Votre message',
                'rows': 5
            }),
        }
        labels = {
            'name': 'Nom complet',
            'email': 'Adresse e-mail',
            'subject': 'Sujet',
            'message': 'Message',
        }
        

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


# ============================================================
#  CONSTANTES — liste des indicatifs pays
# ============================================================

PHONE_COUNTRY_CHOICES = [
    ("+228", "🇹🇬 Togo (+228)"),
    ("+225", "🇨🇮 Côte d'Ivoire (+225)"),
    ("+221", "🇸🇳 Sénégal (+221)"),
    ("+233", "🇬🇭 Ghana (+233)"),
    ("+234", "🇳🇬 Nigeria (+234)"),
    ("+237", "🇨🇲 Cameroun (+237)"),
    ("+226", "🇧🇫 Burkina Faso (+226)"),
    ("+223", "🇲🇱 Mali (+223)"),
    ("+229", "🇧🇯 Bénin (+229)"),
    ("+227", "🇳🇪 Niger (+227)"),
    ("+224", "🇬🇳 Guinée (+224)"),
    ("+245", "🇬🇼 Guinée-Bissau (+245)"),
    ("+222", "🇲🇷 Mauritanie (+222)"),
    ("+232", "🇸🇱 Sierra Leone (+232)"),
    ("+231", "🇱🇷 Liberia (+231)"),
    ("+235", "🇹🇩 Tchad (+235)"),
    ("+236", "🇨🇫 Centrafrique (+236)"),
    ("+241", "🇬🇦 Gabon (+241)"),
    ("+242", "🇨🇬 Congo (+242)"),
    ("+243", "🇨🇩 RD Congo (+243)"),
    ("+250", "🇷🇼 Rwanda (+250)"),
    ("+257", "🇧🇮 Burundi (+257)"),
    ("+256", "🇺🇬 Ouganda (+256)"),
    ("+255", "🇹🇿 Tanzanie (+255)"),
    ("+254", "🇰🇪 Kenya (+254)"),
    ("+251", "🇪🇹 Éthiopie (+251)"),
    ("+212", "🇲🇦 Maroc (+212)"),
    ("+213", "🇩🇿 Algérie (+213)"),
    ("+216", "🇹🇳 Tunisie (+216)"),
    ("+20",  "🇪🇬 Égypte (+20)"),
    ("+33",  "🇫🇷 France (+33)"),
    ("+32",  "🇧🇪 Belgique (+32)"),
    ("+41",  "🇨🇭 Suisse (+41)"),
    ("+1",   "🇺🇸 États-Unis (+1)"),
    ("+44",  "🇬🇧 Royaume-Uni (+44)"),
    ("+49",  "🇩🇪 Allemagne (+49)"),
    ("+351", "🇵🇹 Portugal (+351)"),
    ("+34",  "🇪🇸 Espagne (+34)"),
]


# ============================================================
#  FORMULAIRE D'INSCRIPTION
# ============================================================

class RegisterForm(forms.ModelForm):

    phone_country = forms.ChoiceField(
        choices=PHONE_COUNTRY_CHOICES,
        initial="+228",
        label="Indicatif",
    )

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput,
        min_length=8,
        error_messages={'min_length': "Le mot de passe doit contenir au moins 8 caractères."},
    )

    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput,
    )

    class Meta:
        model  = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone_country',
            'phone_number',
        ]

    # Widgets pour appliquer les classes CSS CCA
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        css = 'field-input'
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = css

    # ---- Validations ----

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Seuls les lettres, chiffres et _ sont autorisés.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cet email existe déjà.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError(e.messages)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Les mots de passe ne correspondent pas.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


# ============================================================
#  FORMULAIRE DE CONNEXION
# ============================================================

class LoginForm(forms.Form):

    email    = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={
            'class':       'field-input',
            'placeholder': 'ton@email.com',
            'autocomplete':'email',
        }),
    )

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class':       'field-input',
            'placeholder': '••••••••',
            'autocomplete':'current-password',
        }),
    )

    def clean(self):
        cleaned  = super().clean()
        email    = cleaned.get('email', '').lower()
        password = cleaned.get('password')

        if email and password:
            self.user = authenticate(username=email, password=password)
            if self.user is None:
                raise ValidationError("Email ou mot de passe incorrect.")
            if not self.user.is_active:
                raise ValidationError("Ce compte est désactivé.")
        return cleaned

    def get_user(self):
        return getattr(self, 'user', None)


# ============================================================
#  FORMULAIRE MOT DE PASSE OUBLIÉ (email only)
# ============================================================

class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(
        label="Adresse email du compte",
        widget=forms.EmailInput(attrs={
            'class':       'field-input',
            'placeholder': 'ton@email.com',
            'autocomplete':'email',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        # On ne révèle pas si l'email existe ou non (sécurité)
        return email
from django import forms

from .models import Article, Commentaire


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["titre", "slug", "contenu", "image", "publie"]
        widgets = {
            "titre": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "contenu": forms.Textarea(
                attrs={"class": "form-control", "rows": 10}
            ),
        }


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ["contenu"]
        widgets = {
            "contenu": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Écrire un commentaire...",
                }
            )
        }


from django import forms
from .models import InscriptionAccompagnement


DOMAINE_CHOICES = [
    ('windev', 'WINDEV'),
    ('algorithmes', 'Algorithmes'),
    ('poo', 'POO'),
    ('bdd', 'Bases de données'),
    ('ia', 'IA & Accélération'),
]


class InscriptionAccompagnementForm(forms.ModelForm):

    domaines = forms.MultipleChoiceField(
        choices=DOMAINE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Domaine(s) souhaité(s)",
    )

    class Meta:
        model = InscriptionAccompagnement
        fields = [
            'formule', 'nom_complet', 'email', 'telephone', 'ville_pays',
            'domaines', 'niveau', 'disponibilite', 'attentes',
        ]
        widgets = {
            'formule': forms.HiddenInput(),
            'nom_complet': forms.TextInput(attrs={
                'class': 'input-cca', 'placeholder': 'Ton nom complet'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input-cca', 'placeholder': 'ton@email.com'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'input-cca', 'placeholder': '+228 90 00 00 00'
            }),
            'ville_pays': forms.TextInput(attrs={
                'class': 'input-cca', 'placeholder': 'Ville, Pays'
            }),
            'niveau': forms.RadioSelect,
            'disponibilite': forms.RadioSelect,
            'attentes': forms.Textarea(attrs={
                'class': 'textarea-cca',
                'rows': 6,
                'placeholder': "Décris tes attentes, tes objectifs, ce que tu veux apprendre ou améliorer grâce à cet accompagnement…"
            }),
        }

    def clean_domaines(self):
        # Stocke la sélection sous forme de chaîne séparée par des virgules
        return ",".join(self.cleaned_data['domaines'])