from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda request: redirect('dashboard'), name='home'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('borrar/<str:periodo>/', views.borrar_transacciones_periodo, name='borrar_transacciones_periodo'), 
]