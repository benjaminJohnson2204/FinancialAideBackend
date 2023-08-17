from django.urls import path

from users.views import *

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('whoami', WhoAmiIView.as_view(), name='whoami'),
]
