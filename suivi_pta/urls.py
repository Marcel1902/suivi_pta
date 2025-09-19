from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.se_connecter, name='login'),
    path('home/', views.home, name="home"),
    # URLs pour la réinitialisation du mot de passe
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', views.se_deconnecter, name="logout"),
    path('rapport', views.faire_un_rapport, name="rapport"),
    path('voir_rapport/<int:rapport_id>/', views.voir_rapport, name="voir_rapport"),
    path('modifier_etat_seance/', views.modifier_etat_seance, name="modifier_etat_seance"),
    path('conseils/<int:seance_id>/', views.conseils_pedagogique, name="conseils_pedagogique"),
]
