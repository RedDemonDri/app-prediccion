// dashboard-range.js
// Captura controles de rango y granularidad y recarga el gráfico via AJAX (o por GET si no hay endpoint AJAX)

document.addEventListener('DOMContentLoaded', function() {
    const granSelect = document.getElementById('granularity-select');
    const fromInput = document.getElementById('from-date');
    const toInput = document.getElementById('to-date');
    const applyBtn = document.getElementById('apply-range');
    const presets = document.querySelectorAll('.range-preset');
    const categorySelect = document.getElementById('category-select');
    const metricsSelect = document.getElementById('metrics-select');

    function buildQuery() {
        const q = new URLSearchParams();
        if (granSelect) q.set('granularity', granSelect.value);
        if (fromInput && fromInput.value) q.set('from', fromInput.value);
        if (toInput && toInput.value) q.set('to', toInput.value);
        // append multiple metric_id params
        if (metricsSelect) {
            const opts = Array.from(metricsSelect.selectedOptions).map(o => o.value);
            opts.forEach(v => q.append('metric_id', v));
        }
        return q.toString();
    }

    function renderChartFromData(data) {
        if (!data) return;
        const labels = data.labels || data.labels;
        const seriesRaw = data.series || (data.values ? [{metric_name: 'Registros', values: data.values}] : []);
        const apexSeries = seriesRaw.map(s => ({ name: s.metric_name || s.name || ('m'+(s.metric_id||'')), data: s.values || s.data || [] , type: s.chart_type || 'line' }));
        const colors = seriesRaw.map(s => s.color || undefined).filter(c => c !== undefined);

        if (window.dashboardChart) {
            window.dashboardChart.updateOptions({ xaxis: { categories: labels } });
            if (colors.length) window.dashboardChart.updateOptions({ colors: colors });
            window.dashboardChart.updateSeries(apexSeries);
        } else {
            // create a new chart if not present
            const options = {
                chart: { type: 'area', height: 320, toolbar: { show: false }, zoom: { enabled: false } },
                series: apexSeries,
                xaxis: { categories: labels, labels: { rotate: -45 } },
                stroke: { curve: 'smooth', width: 2 },
                fill: { type: 'gradient', gradient: { shadeIntensity: 0.4, opacityFrom: 0.6, opacityTo: 0.1 } },
                tooltip: { x: { format: 'dd/MM' } },
                grid: { borderColor: '#e6e6e6' },
                colors: colors.length ? colors : ['#2563eb']
            };
            const chart = new ApexCharts(document.querySelector('#chart'), options);
            chart.render();
            window.dashboardChart = chart;
        }
    }

    function reloadWithParams() {
        const qs = buildQuery();
        const url = window.location.pathname + (qs ? '?' + qs : '');
        fetch(window.location.origin + '/dashboard/api/chart-data/?' + qs)
            .then(r => {
                if (!r.ok) throw new Error('No JSON endpoint');
                return r.json();
            })
            .then(data => {
                // update apex chart (supports multiple series)
                renderChartFromData(data);
            })
            .catch(() => { window.location.href = url; });
    }

    // load metrics for a category via AJAX
    function loadMetricsForCategory(catId) {
        const url = window.location.origin + '/dashboard/api/metrics/' + (catId ? '?category=' + encodeURIComponent(catId) : '');
        fetch(url)
            .then(r => r.json())
            .then(list => {
                if (!metricsSelect) return;
                // clear
                metricsSelect.innerHTML = '';
                list.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.id;
                    opt.textContent = m.name;
                    metricsSelect.appendChild(opt);
                });
            })
            .catch(() => {});
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', (e) => {
            loadMetricsForCategory(e.target.value);
        });
        // initial load if category empty -> keep existing options
    }

    if (presets.length) {
        presets.forEach(btn => btn.addEventListener('click', (e) => {
            const p = e.currentTarget.dataset.range;
            const today = new Date();
            let from, to;
            if (p === '7') { to = today; from = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 6); }
            if (p === '30') { to = today; from = new Date(today.getFullYear(), today.getMonth(), today.getDate() - 29); }
            if (p === 'month') { to = today; from = new Date(today.getFullYear(), today.getMonth(), 1); }
            if (p === 'year') { to = today; from = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate()); }
            if (fromInput) fromInput.value = from.toISOString().slice(0,10);
            if (toInput) toInput.value = to.toISOString().slice(0,10);
            reloadWithParams();
        }));
    }

    if (applyBtn) applyBtn.addEventListener('click', reloadWithParams);
});
