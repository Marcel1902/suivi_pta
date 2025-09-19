# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Seance, Equipe, EtatSeance

# Quand une séance est créée → créer EtatSeance pour chaque équipe
@receiver(post_save, sender=Seance)
def creer_etat_seance_pour_equipes(sender, instance, created, **kwargs):
    if created:  # uniquement à la création
        for equipe in Equipe.objects.all():
            EtatSeance.objects.create(
                seance=instance,
                equipe=equipe,
                etat="todo"  # valeur par défaut
            )

# Quand une équipe est créée → créer EtatSeance pour chaque séance existante
@receiver(post_save, sender=Equipe)
def creer_etat_seance_pour_seances(sender, instance, created, **kwargs):
    if created:  # uniquement à la création
        for seance in Seance.objects.all():
            EtatSeance.objects.create(
                seance=seance,
                equipe=instance,
                etat="todo"  # valeur par défaut
            )
