from django.contrib import admin
from .models import Lycee, Rapport, Equipe, Seance, Profil, EtatSeance, ConseilPedagogique

# Register your models here.

admin.site.register(Lycee)
admin.site.register(Rapport)
admin.site.register(Equipe)
admin.site.register(Seance)
admin.site.register(Profil)
admin.site.register(EtatSeance)
admin.site.register(ConseilPedagogique)
admin.site.site_header = "Administration du suivi PTA"
admin.site.site_title = "Suivi PTA"
admin.site.index_title = "Tableau de bord"
admin.site.empty_value_display = "-vide-"


