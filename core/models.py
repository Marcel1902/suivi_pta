from django.db import models
from django.contrib.auth.models import User

# --- Lycée ---
class Lycee(models.Model):
    nom = models.CharField(max_length=150)
    adresse = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nom


# --- Equipe (chaque lycée a une équipe CoderDojo assignée) ---
class Equipe(models.Model):
    nom = models.CharField(max_length=100)
    lycee = models.OneToOneField(Lycee, on_delete=models.CASCADE, related_name="equipe")

    def __str__(self):
        return f"{self.nom} ({self.lycee.nom})"

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profil")
    equipe = models.ForeignKey(Equipe, on_delete=models.SET_NULL, null=True, blank=True, related_name="membres")
    role = models.CharField(max_length=50, blank=True)
    chef_equipe = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.equipe.nom if self.equipe else 'Aucune équipe'})"



# --- Séances du PTA ---
class Seance(models.Model):
    numero = models.IntegerField()           # Séance 1, 2, 3...
    titre = models.CharField(max_length=200) # Ex: "Liens et images"
    objectif = models.TextField()

    def __str__(self):
        return f"Séance {self.numero} - {self.titre}"

class EtatSeance(models.Model):
    STATUS_CHOICES = [
        ("todo", "À faire"),
        ("progress", "En cours"),
        ("done", "Terminé"),
    ]

    equipe = models.ForeignKey("Equipe", on_delete=models.CASCADE, related_name="etats")
    seance = models.ForeignKey("Seance", on_delete=models.CASCADE, related_name="etats")
    etat = models.CharField(max_length=10, choices=STATUS_CHOICES, default="todo")

    class Meta:
        unique_together = ("equipe", "seance")  # Une seule ligne par équipe-séance

    def __str__(self):
        return f"{self.equipe.nom} - {self.seance.titre} ({self.etat})"



# --- Rapports des équipes ---
class Rapport(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name="rapports")
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name="rapports")
    date = models.DateField(auto_now_add=True)
    nombre_eleves = models.IntegerField(default=1)
    activites = models.TextField()
    difficultes = models.TextField(blank=True, null=True)
    commentaires = models.TextField(blank=True, null=True)
    fait_par = models.CharField(max_length=30)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"Rapport {self.equipe.nom} - Séance {self.seance.numero}"

from django.db import models

class ConseilPedagogique(models.Model):
    seance = models.ForeignKey(
        Seance,
        on_delete=models.CASCADE,
        related_name="conseils_pedagogiques"
    )
    
    recommandations = models.TextField(
        "Conseils pour animer la séance",
        help_text="Indiquez les points clés, la méthode, le déroulement."
    )
    exercices_pratiques = models.TextField(
        "Exercices pratiques",
        help_text="Liste d'exercices ou d'activités à proposer aux élèves."
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "Conseil pédagogique"
        verbose_name_plural = "Conseils pédagogiques"

    def __str__(self):
        return f"Conseil pour la séance : {self.seance.titre}"




