# dashboard/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group, User
from django.contrib import messages
from datetime import timedelta
from .models import Metric, MetricValue
from .forms import BasicUserCreationForm, SimpleRegistrationForm


def public_landing(request):
    """Página pública mínima para usuarios no autenticados.
    Si el usuario está autenticado redirige al dashboard (home).
    """
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'public_only_login.html')


def register(request):
    """Crear un usuario básico (is_staff=False, is_superuser=False) y añadirlo al grupo BasicUsers.
    Si el grupo no existe se crea.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            # Crear usuario manualmente para evitar validadores globales
            user = User(username=username, email=email)
            user.is_staff = False
            user.is_superuser = False
            user.set_password(password)
            user.save()
            group, created = Group.objects.get_or_create(name='BasicUsers')
            user.groups.add(group)
            auth_login(request, user)
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('home')
    else:
        form = SimpleRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    # KPIs
    total_registros = MetricValue.objects.count()

    # Suma total de todos los valores (total_valor para compatibilidad con plantillas)
    total_valor = MetricValue.objects.aggregate(total=Sum('value'))['total'] or 0.0

    # nuevas entradas (últimas 24h)
    nuevas_entradas = MetricValue.objects.filter(timestamp__gte=timezone.now() - timedelta(days=1)).count()

    # Gráfico: últimos 7 días para una métrica principal (ventas si existe, sino primera métrica)
    ventas_metric = Metric.objects.filter(name__iexact='ventas').first()
    metric_for_chart = ventas_metric or Metric.objects.first()
    labels = []
    values = []
    if metric_for_chart:
        today = timezone.localdate()
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            labels.append(d.strftime("%d/%m"))
            # usamos filter por fecha (timestamp__date) para evitar problemas de timezone
            day_total = MetricValue.objects.filter(metric=metric_for_chart, timestamp__date=d).aggregate(total=Sum('value'))['total'] or 0
            values.append(float(day_total))

    context = {
        "total_registros": total_registros,
        "total_valor": total_valor,
        "nuevas_entradas": nuevas_entradas,
        "chart_labels": labels,
        "chart_values": values,
    }
    return render(request, "dashboard/home.html", context)


@login_required
def tabla(request):
    # Proveer lista de valores recientes para la tabla
    qs = MetricValue.objects.select_related('metric').all().order_by('-timestamp')[:200]
    registros = [
        {
            'id': v.id,
            'name': v.metric.name,
            'value': v.value,
            'recorded_at': v.timestamp,
        }
        for v in qs
    ]
    return render(request, 'dashboard/tabla.html', {'registros': registros})


@login_required
def chart_data(request):
    # Endpoint JSON para alimentar el gráfico (últimos 7 días)
    ventas_metric = Metric.objects.filter(name__iexact='ventas').first()
    metric_for_chart = ventas_metric or Metric.objects.first()
    labels = []
    values = []
    if metric_for_chart:
        today = timezone.localdate()
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            labels.append(d.strftime('%d/%m'))
            day_total = MetricValue.objects.filter(metric=metric_for_chart, timestamp__date=d).aggregate(total=Sum('value'))['total'] or 0
            values.append(float(day_total))
    return JsonResponse({'labels': labels, 'values': values})

