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
from .models import Metric, MetricValue, MetricCategory
from .forms import BasicUserCreationForm, SimpleRegistrationForm
from datetime import date
import calendar
from django.utils.dateparse import parse_date

# Limits
MAX_RANGE_DAYS = 365 * 3  # 3 years


def _parse_dates(request):
    """Parsear params GET 'from' y 'to' en fechas (server localdate).

    Si faltan, devuelve rango por defecto: últimos 7 días.
    Devuelve (from_date, to_date, error_message)
    """
    today = timezone.localdate()
    from_str = request.GET.get('from') or request.GET.get('start')
    to_str = request.GET.get('to') or request.GET.get('end')
    if from_str:
        from_date = parse_date(from_str)
    else:
        from_date = today - timedelta(days=6)
    if to_str:
        to_date = parse_date(to_str)
    else:
        to_date = today

    if from_date is None or to_date is None:
        return None, None, 'Fechas inválidas. Usa formato YYYY-MM-DD.'
    if from_date > to_date:
        return None, None, 'La fecha "from" no puede ser posterior a "to".'
    delta = (to_date - from_date).days
    if delta > MAX_RANGE_DAYS:
        return None, None, f'Rango máximo permitido: {MAX_RANGE_DAYS} días.'
    return from_date, to_date, None


def _generate_periods(from_date, to_date, granularity):
    """Genera lista de (period_start, period_end, label) según granularidad."""
    periods = []
    if granularity == 'daily':
        d = from_date
        while d <= to_date:
            periods.append((d, d, d.strftime('%d/%m')))
            d = d + timedelta(days=1)
    elif granularity == 'weekly':
        # weeks starting Monday
        # find first monday on/after from_date's week start
        start = from_date - timedelta(days=from_date.weekday())
        cur = start
        while cur <= to_date:
            week_start = cur
            week_end = cur + timedelta(days=6)
            seg_start = max(week_start, from_date)
            seg_end = min(week_end, to_date)
            label = f"{seg_start.strftime('%d/%m')}-{seg_end.strftime('%d/%m')}"
            periods.append((seg_start, seg_end, label))
            cur = cur + timedelta(days=7)
    elif granularity == 'monthly':
        y = from_date.year
        m = from_date.month
        cur = date(y, m, 1)
        while cur <= to_date:
            last_day = calendar.monthrange(cur.year, cur.month)[1]
            seg_start = cur if cur >= from_date else from_date
            seg_end = date(cur.year, cur.month, last_day)
            seg_end = seg_end if seg_end <= to_date else to_date
            label = cur.strftime('%b %Y')
            periods.append((seg_start, seg_end, label))
            # next month
            if cur.month == 12:
                cur = date(cur.year + 1, 1, 1)
            else:
                cur = date(cur.year, cur.month + 1, 1)
    elif granularity == 'yearly':
        y = from_date.year
        cur = date(y, 1, 1)
        while cur <= to_date:
            seg_start = cur if cur >= from_date else from_date
            seg_end = date(cur.year, 12, 31)
            seg_end = seg_end if seg_end <= to_date else to_date
            label = str(cur.year)
            periods.append((seg_start, seg_end, label))
            cur = date(cur.year + 1, 1, 1)
    else:
        raise ValueError('Granularity inválida')
    return periods


def _aggregate_for_metric(metric, from_date, to_date, granularity):
    labels = []
    values = []
    periods = _generate_periods(from_date, to_date, granularity)
    for seg_start, seg_end, label in periods:
        labels.append(label)
        q = MetricValue.objects.filter(metric=metric, timestamp__date__gte=seg_start, timestamp__date__lte=seg_end)
        total = q.aggregate(total=Sum('value'))['total'] or 0
        values.append(float(total))
    return labels, values


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

    # Parámetros GET: granularidad y rango
    gran = request.GET.get('granularity', 'daily')
    from_date, to_date, err = _parse_dates(request)
    if err:
        # caemos al rango por defecto si hay error
        from_date = timezone.localdate() - timedelta(days=6)
        to_date = timezone.localdate()
        gran = 'daily'

    ventas_metric = Metric.objects.filter(name__iexact='ventas').first()
    metric_for_chart = ventas_metric or Metric.objects.first()
    labels = []
    values = []
    # provide categories and initial metrics for UI selects
    categories = MetricCategory.objects.all()
    metrics_for_category = Metric.objects.filter(category=metric_for_chart.category) if metric_for_chart and metric_for_chart.category else Metric.objects.all()[:50]
    if metric_for_chart:
        try:
            labels, values = _aggregate_for_metric(metric_for_chart, from_date, to_date, gran)
        except Exception:
            labels, values = [], []

    context = {
        "total_registros": total_registros,
        "total_valor": total_valor,
        "nuevas_entradas": nuevas_entradas,
        "chart_labels": labels,
        "chart_values": values,
        "range_from": from_date,
        "range_to": to_date,
        "granularity": gran,
        "categories": categories,
        "metrics_for_category": metrics_for_category,
        "metric_for_chart": metric_for_chart,
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
    # Endpoint JSON para alimentar el gráfico con parámetros de rango/granularidad
    gran = request.GET.get('granularity', 'daily')
    from_date, to_date, err = _parse_dates(request)
    if err:
        return JsonResponse({'error': err}, status=400)
    # Collect metric ids: allow repeated 'metric_id' params or comma-separated 'metrics'
    metric_ids = request.GET.getlist('metric_id') or []
    if not metric_ids:
        metrics_csv = request.GET.get('metrics')
        if metrics_csv:
            metric_ids = [m.strip() for m in metrics_csv.split(',') if m.strip()]

    series = []
    try:
        periods = _generate_periods(from_date, to_date, gran)
    except ValueError:
        return JsonResponse({'error': 'granularity inválida'}, status=400)

    labels = [label for (_s, _e, label) in periods]

    # If no metric specified, default to ventas or first metric
    if not metric_ids:
        ventas_metric = Metric.objects.filter(name__iexact='ventas').first()
        default_metric = ventas_metric or Metric.objects.first()
        if not default_metric:
            return JsonResponse({'labels': labels, 'series': []})
        metric_ids = [str(default_metric.id)]

    try:
        for mid in metric_ids:
            try:
                m = Metric.objects.get(pk=int(mid))
            except Exception:
                # skip invalid ids
                continue
            values = []
            for seg_start, seg_end, _lbl in periods:
                q = MetricValue.objects.filter(metric=m, timestamp__date__gte=seg_start, timestamp__date__lte=seg_end)
                total = q.aggregate(total=Sum('value'))['total'] or 0
                values.append(float(total))
            series.append({
                'metric_id': m.id,
                'metric_name': m.name,
                'chart_type': m.chart_type,
                'color': m.display_color,
                'values': values,
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # Backwards-compatible single-metric shape
    if len(series) == 1:
        return JsonResponse({'labels': labels, 'values': series[0]['values'], 'series': series})
    return JsonResponse({'labels': labels, 'series': series})


def metrics_list(request):
    """Return JSON list of metrics. Optional GET param `category` to filter by category id."""
    category = request.GET.get('category')
    qs = Metric.objects.all().order_by('name')
    if category:
        try:
            qs = qs.filter(category_id=int(category))
        except Exception:
            return JsonResponse({'error': 'category inválida'}, status=400)

    out = []
    for m in qs:
        out.append({
            'id': m.id,
            'name': m.name,
            'slug': m.slug,
            'chart_type': m.chart_type,
            'color': m.display_color,
        })
    return JsonResponse(out, safe=False)

