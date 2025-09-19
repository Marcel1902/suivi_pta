from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Equipe, Seance, Rapport, Profil, EtatSeance, ConseilPedagogique
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

# connecter l'utilisateur
def se_connecter(request):
    # Si l'utilisateur est déjà connecté, on le redirige directement
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember')  # vaudra 'on' si coché

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if remember_me != 'on':
                # session expirera à la fermeture du navigateur
                request.session.set_expiry(0)
            else:
                # session persistante (par exemple 2 semaines)
                request.session.set_expiry(1209600)  # 2 semaines en secondes
            return redirect('home')
        else:
            messages.error(request, "Oups ! Mauvais identifiants")
            return render(request, "core/login.html", {"username": username})
    
    return render(request, "core/login.html")


@login_required
def home(request):
    seances = Seance.objects.all().order_by('numero')
    equipe = request.user.profil.equipe

    # Membres de la même équipe
    membres_equipe = Profil.objects.filter(equipe=equipe)

    # Total des séances prévues
    total_seances = Seance.objects.count()

    # Progression pour l'équipe connectée (via EtatSeance)
    seance_termines = EtatSeance.objects.filter(equipe=equipe, etat="done").count()
    reste_a_faire = EtatSeance.objects.filter(equipe=equipe, etat="todo").count()
    seance_en_cours = EtatSeance.objects.filter(equipe=equipe, etat="progress").count()
    etat_seances = EtatSeance.objects.filter(equipe=equipe).select_related("seance")


    progression = int((seance_termines / total_seances) * 100) if total_seances > 0 else 0

    # Stats globales
    equipes = Equipe.objects.count()
    rapports = Rapport.objects.all().order_by('-date')

    # 🔥 Progression par équipe
    equipes_progression = []
    for eq in Equipe.objects.all():
        done = EtatSeance.objects.filter(equipe=eq, etat="done").count()
        progression_equipe = int((done / total_seances) * 100) if total_seances > 0 else 0

        equipes_progression.append({
            "nom": eq.nom,
            "progression": progression_equipe
        })

    return render(request, "core/dashboard.html", {
        "seance_termines": seance_termines,
        "total_seances": total_seances,
        "reste_a_faire": reste_a_faire,
        "seance_en_cours": seance_en_cours,
        "progression": progression,
        "equipes": equipes,
        "seances": seances,
        "rapports": rapports,
        "membres_equipe": membres_equipe,
        "equipes_progression": equipes_progression,
        "etat_seances": etat_seances,
    })

def se_deconnecter(request):
    logout(request)
    return redirect('login')


def ajax_response(success, message, status=200):
    """Utilitaire pour renvoyer des réponses AJAX uniformisées"""
    return JsonResponse({'success': success, 'message': message}, status=status)

@login_required
def faire_un_rapport(request):
    seances = Seance.objects.all()

    if request.method == "POST":
        seance_id = request.POST.get('seance')
        nombre_eleves = request.POST.get('nombre_eleves')
        activites = request.POST.get('activites')
        difficultes = request.POST.get('difficultes')
        commentaires = request.POST.get('commentaires')

        # Vérifier les champs obligatoires
        if not seance_id or not nombre_eleves or not activites:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(False, "Hey ! Tous les champs sont obligatoires 😉", 400)
            messages.error(request, "Hey ! Tous les champs sont obligatoires 😉")
            return redirect('home')

        # Récupérer la séance
        seance = get_object_or_404(Seance, id=seance_id)

        # Récupérer automatiquement l'équipe depuis le profil de l'utilisateur
        equipe = None
        if hasattr(request.user, 'profil') and request.user.profil.equipe:
            equipe = request.user.profil.equipe
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(False, "Oups ! T’es pas encore dans une team 😎", 400)
            messages.error(request, "Oups ! T’es pas encore dans une team 😎")
            return redirect('home')

        # Vérifier doublons
        rapport_existant = Rapport.objects.filter(equipe=equipe, seance=seance).first()
        if rapport_existant:
            auteur = rapport_existant.fait_par
            if auteur == request.user.username:
                message = "eh! t'as déjà fait ce rapport, pas besoin de le faire deux fois 😅"
            else:
                message = f"Pas besoin de doubler, ton team {auteur} l’a déjà fait ! 😅"

            # Vérifier si c'est une requête AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return ajax_response(False, message, 400)

            messages.error(request, message)
            return redirect('home')


        # Créer le rapport
        Rapport.objects.create(
            equipe=equipe,
            seance=seance,
            nombre_eleves=nombre_eleves,
            activites=activites,
            difficultes=difficultes,
            commentaires=commentaires,
            fait_par = request.user.username,
        )

        # Réponse AJAX ou classique
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return ajax_response(True, "Super ! Ton rapport est enregistré 😎")
        messages.success(request, "Super ! Ton rapport est enregistré 😎")
        return redirect('home')

    # GET
    return render(request, "core/ajout_rapport.html", {"seances": seances})

def voir_rapport(request, rapport_id):
    rapport = get_object_or_404(Rapport, id=rapport_id)
    return render(request, "core/voir_rapport.html", {"rapport": rapport})

@login_required
@csrf_exempt
def modifier_etat_seance(request):
    if request.method == "POST":
        data = json.loads(request.body)
        etat_id = data.get("etat_id")
        nouveau_etat = data.get("etat")

        etat = get_object_or_404(EtatSeance, id=etat_id, equipe=request.user.profil.equipe)
        if nouveau_etat in ["todo", "progress", "done"]:
            etat.etat = nouveau_etat
            etat.save()

            # Définir couleurs pour le badge
            colors = {
                "todo": {"bg": "#f3f4f6", "text": "#1f2937", "affichage": "À faire"},
                "progress": {"bg": "#fef3c7", "text": "#78350f", "affichage": "En cours"},
                "done": {"bg": "#d1fae5", "text": "#065f46", "affichage": "Terminée"}
            }
            c = colors[nouveau_etat]

            return JsonResponse({
                "success": True,
                "etat_affichage": c["affichage"],
                "bg_color": c["bg"],
                "text_color": c["text"]
            })

    return JsonResponse({"success": False})

def conseils_pedagogique(request, seance_id):
    # Vérifie que la séance existe
    seance = get_object_or_404(Seance, id=seance_id)
    now_year = datetime.datetime.now().strftime('%Y')

    # Récupère tous les conseils liés à cette séance (peut être vide)
    conseils = ConseilPedagogique.objects.filter(seance=seance).order_by('-date_creation')

    return render(request, "core/conseils.html", {
        "seance": seance,
        "conseils": conseils,
        "now_year": now_year,
    })