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