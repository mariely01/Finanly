from django.contrib import admin
from django.urls import path, include
from finances import views  # 👈 Importá tus propias vistas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),      
    path('logout/', views.logout_view, name='logout'),   
    path('', include('finances.urls')),
]