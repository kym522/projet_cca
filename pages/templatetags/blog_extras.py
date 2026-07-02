import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def initiales(user):
    """
    Génère les initiales d'un utilisateur (ex: "Jean Dupont" -> "JD"),
    en repli sur le username si pas de prénom/nom renseigné.
    Même logique que sur la page profil.
    """
    if not user:
        return "?"

    first = (getattr(user, "first_name", "") or "").strip()
    last = (getattr(user, "last_name", "") or "").strip()

    if first and last:
        return (first[0] + last[0]).upper()
    if first:
        return first[:2].upper()
    if last:
        return last[:2].upper()

    username = getattr(user, "username", "") or getattr(user, "email", "") or "?"
    return username[:2].upper()


@register.filter
def avatar_color(user):
    """
    Couleur de fond déterministe basée sur l'id/username, pour que
    chaque utilisateur ait toujours la même couleur d'avatar.
    """
    palette = [
        "#F87171", "#FB923C", "#FBBF24", "#A3E635",
        "#34D399", "#22D3EE", "#60A5FA", "#A78BFA",
        "#F472B6", "#FB7185",
    ]
    key = getattr(user, "id", None) or getattr(user, "username", "x")
    index = hash(str(key)) % len(palette)
    return palette[index]


@register.filter
def est_like_par(commentaire, user):
    """
    Indique si un commentaire est liké par l'utilisateur donné.
    Permet d'écrire {{ commentaire|est_like_par:user }} dans les templates,
    car Django ne permet pas d'appeler une méthode avec un argument
    directement (ex: commentaire.est_like_par:user est invalide).
    """
    return commentaire.est_like_par(user)


@register.filter
def formater_article(texte):
    """
    Met en forme le contenu brut d'un article :
    - une ligne entièrement en **gras** devient un sous-titre <h3>
    - **gras** au milieu d'une phrase devient <strong>
    - les lignes commençant par "- " deviennent une vraie liste à puces <ul><li>
    - les lignes vides séparent les paragraphes <p>
    Permet de coller du texte (ex. exporté depuis Word) sans souci de mise en forme.
    """
    if not texte:
        return ""

    lignes = texte.replace("\r\n", "\n").split("\n")
    html_parts = []
    buffer_liste = []

    def vider_liste():
        if buffer_liste:
            items = "".join(f"<li>{l}</li>" for l in buffer_liste)
            html_parts.append(f"<ul class=\"article-liste\">{items}</ul>")
            buffer_liste.clear()

    def gerer_gras(ligne):
        morceaux = re.split(r"\*\*(.+?)\*\*", ligne)
        rendu = ""
        for i, morceau in enumerate(morceaux):
            if i % 2 == 1:
                rendu += f"<strong>{escape(morceau)}</strong>"
            else:
                rendu += escape(morceau)
        return rendu

    for ligne_brute in lignes:
        ligne = ligne_brute.strip()

        if not ligne:
            vider_liste()
            continue

        if ligne.startswith("- ") or ligne.startswith("• "):
            contenu_item = ligne[2:].strip()
            buffer_liste.append(gerer_gras(contenu_item))
            continue

        vider_liste()

        match_titre = re.fullmatch(r"\*\*(.+?)\*\*\s*:?\s*", ligne)
        if match_titre:
            html_parts.append(f"<h3>{escape(match_titre.group(1))}</h3>")
            continue

        if ligne.startswith("«") and ligne.endswith("»"):
            html_parts.append(f"<blockquote>{gerer_gras(ligne)}</blockquote>")
            continue

        html_parts.append(f"<p>{gerer_gras(ligne)}</p>")

    vider_liste()

    return mark_safe("".join(html_parts))