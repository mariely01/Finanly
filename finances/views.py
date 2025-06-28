from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction
from .forms import TransactionForm
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

# Vista de login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso.')
            return redirect('dashboard')  
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'finances/login.html')

# Vista para cerrar sesión
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')

# Vista del dashboard
@login_required
def dashboard(request):
    print("🧠 Usuario autenticado:", request.user)  
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    ingresos = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    gastos = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    total_balance = ingresos - gastos

    return render(request, 'finances/dashboard.html', {
        'transactions': transactions,
        'total_balance': total_balance,
        'ingresos': ingresos,   # para el gráfico
        'gastos': gastos,       # para el gráfico
    })

# Vista para agregar transacciones
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transacción guardada correctamente.')
            return redirect('dashboard')
    else:
        form = TransactionForm()

    return render(request, 'finances/add_transaction.html', {'form': form})

@login_required
def borrar_transacciones_periodo(request, periodo):
    user = request.user
    hoy = timezone.now().date()

    if periodo == 'mensual':
        primer_dia = hoy.replace(day=1)
        if hoy.month == 12:
            ultimo_dia = hoy.replace(day=31)
        else:
            siguiente_mes = hoy.replace(month=hoy.month+1, day=1)
            ultimo_dia = siguiente_mes - timedelta(days=1)
    elif periodo == 'quincenal':
        if hoy.day <= 15:
            primer_dia = hoy.replace(day=1)
            ultimo_dia = hoy.replace(day=15)
        else:
            primer_dia = hoy.replace(day=16)
            if hoy.month == 12:
                ultimo_dia = hoy.replace(day=31)
            else:
                siguiente_mes = hoy.replace(month=hoy.month+1, day=1)
                ultimo_dia = siguiente_mes - timedelta(days=1)
    else:
        messages.error(request, "Período inválido.")
        return redirect('dashboard')

    transacciones = Transaction.objects.filter(user=user, date__range=(primer_dia, ultimo_dia))
    cantidad = transacciones.count()
    transacciones.delete()

    messages.success(request, f"Se eliminaron {cantidad} transacciones del período {periodo}.")
    return redirect('dashboard')