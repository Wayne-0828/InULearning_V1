// Plotly charts rendering helpers for dashboard

(function () {
    // Ensure Plotly is loaded; if not, load from CDN once
    const PLOTLY_CDN = 'https://cdn.plot.ly/plotly-2.30.0.min.js';
    let plotlyLoadingPromise = null;

    function ensurePlotly() {
        if (window.Plotly) return Promise.resolve();
        if (plotlyLoadingPromise) return plotlyLoadingPromise;
        plotlyLoadingPromise = new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = PLOTLY_CDN;
            script.async = true;
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load Plotly'));
            document.head.appendChild(script);
        });
        return plotlyLoadingPromise;
    }

    function toFixedNumber(value, digits = 2) {
        if (value === null || value === undefined || isNaN(value)) return 0;
        return Number.parseFloat(value).toFixed(digits);
    }

    // Render radar chart
    async function renderSubjectRadar(containerId, radarResponse) {
        await ensurePlotly();

        const el = document.getElementById(containerId);
        if (!el) return;

        const metrics = radarResponse?.metrics || [];
        const subjects = radarResponse?.subjects || [];

        if (!metrics.length || !subjects.length) {
            el.innerHTML = '<div class="text-gray-500">暫無資料</div>';
            return;
        }

        const categories = metrics.map((m) => m);

        const traces = subjects.map((subj) => {
            const normalized = subj.normalized || {};
            const raw = subj.raw || {};
            // close the radar
            const r = categories.map((m) => (normalized[m] ?? 0));
            r.push(r[0]);
            const theta = categories.concat(categories[0]);

            const hoverText = categories.map((m) => {
                const rawVal = raw[m];
                return `${subj.label || subj.subject_id} - ${m}: ${toFixedNumber(rawVal)}`;
            });
            hoverText.push(hoverText[0]);

            return {
                type: 'scatterpolar',
                r,
                theta,
                fill: 'toself',
                name: subj.label || subj.subject_id,
                hoverinfo: 'text',
                text: hoverText,
            };
        });

        const layout = {
            polar: {
                radialaxis: { visible: true, range: [0, 100] },
            },
            showlegend: true,
            margin: { t: 20, r: 20, b: 20, l: 20 },
            height: 300,
        };

        await window.Plotly.newPlot(el, traces, layout, { responsive: true, displayModeBar: false });
    }

    // Render trend line chart
    async function renderSubjectTrend(containerId, trendResponse) {
        await ensurePlotly();

        const el = document.getElementById(containerId);
        if (!el) return;

        const series = trendResponse?.series || [];
        if (!series.length) {
            el.innerHTML = '<div class="text-gray-500">暫無資料</div>';
            return;
        }

        const traces = series.map((s) => {
            const x = (s.points || []).map((p) => p.x);
            const y = (s.points || []).map((p) => p.y);
            return {
                type: 'scatter',
                mode: 'lines+markers',
                x,
                y,
                name: s.label || s.subject_id,
                hovertemplate: '%{x}<br>值: %{y:.2f}<extra></extra>',
            };
        });

        const layout = {
            xaxis: { title: '時間' },
            yaxis: { title: trendResponse?.metric === 'score' ? '分數' : '正確率', rangemode: 'tozero' },
            showlegend: true,
            margin: { t: 20, r: 20, b: 40, l: 40 },
            height: 300,
        };

        await window.Plotly.newPlot(el, traces, layout, { responsive: true, displayModeBar: false });
    }

    // expose to global
    window.renderSubjectRadar = renderSubjectRadar;
    window.renderSubjectTrend = renderSubjectTrend;
})();


