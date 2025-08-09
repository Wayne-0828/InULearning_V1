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

    function hexToRgba(hex, alpha = 0.25) {
        const sanitized = hex.replace('#', '');
        const bigint = parseInt(sanitized, 16);
        const r = (bigint >> 16) & 255;
        const g = (bigint >> 8) & 255;
        const b = bigint & 255;
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // 指標中文對照
    const METRIC_LABELS = {
        accuracy: '正確率',
        qpm: '平均答題速率(題/分)',
        dwell_min: '停留時間(分)',
        growth_rate: '成長率',
        knowledge_mastery: '知識點掌握率',
        time_stability: '作答時間穩定性(秒, 標準差)',
    };

    // 科目顏色
    const SUBJECT_COLORS = {
        '國文': '#6EC1FF',     // 淺藍
        '英文': '#FF4D4F',     // 紅色
        '數學': '#1E3A8A',     // 深藍
        '自然': '#10B981',     // 綠色
        '地理': '#8B4513',     // 咖啡色
        '歷史': '#F6E05E',     // 鵝黃色
        '公民': '#8B5CF6',     // 紫色
    };

    function getSubjectColor(name) {
        return SUBJECT_COLORS[name] || '#3B82F6';
    }

    function formatRawValue(metricKey, rawVal) {
        if (rawVal === null || rawVal === undefined) return '-';
        if (metricKey === 'accuracy' || metricKey === 'knowledge_mastery' || metricKey === 'growth_rate') {
            const percent = Number.parseFloat(rawVal) * 100;
            const sign = metricKey === 'growth_rate' && percent > 0 ? '+' : '';
            return `${sign}${toFixedNumber(percent, 2)}%`;
        }
        if (metricKey === 'qpm') return `${toFixedNumber(rawVal, 2)} 題/分`;
        if (metricKey === 'dwell_min') return `${toFixedNumber(rawVal, 1)} 分鐘`;
        if (metricKey === 'time_stability') return `${toFixedNumber(rawVal, 1)} 秒`;
        return toFixedNumber(rawVal, 2);
    }

    // Render radar charts with subject tabs (single chart, tab to switch)
    async function renderSubjectRadar(containerId, radarResponse) {
        await ensurePlotly();

        const el = document.getElementById(containerId);
        if (!el) return;
        el.style.overflow = 'hidden';

        const metrics = radarResponse?.metrics || [];
        const subjects = radarResponse?.subjects || [];

        if (!metrics.length || !subjects.length) {
            el.innerHTML = '<div class="text-gray-500">暫無資料</div>';
            return;
        }

        // 固定科目順序：透過後端已排序 series/subjects；此處僅處理指標順序按後端回傳即可
        const categories = metrics.map((m) => m);
        const categoriesZh = categories.map((m) => METRIC_LABELS[m] || m);

        // 清空容器，改為標籤切換 + 單一圖表
        el.innerHTML = '';
        const tabs = document.createElement('div');
        tabs.className = 'flex flex-wrap gap-2 mb-3';
        const chart = document.createElement('div');
        chart.style.height = '100%';
        chart.style.width = '100%';
        el.appendChild(tabs);
        el.appendChild(chart);

        let activeIndex = 0;

        const draw = async (idx) => {
            const subj = subjects[idx];
            const normalized = subj.normalized || {};
            const raw = subj.raw || {};
            // normalized 為 0..1，圖上以百分率顯示 -> *100
            const rVals = categories.map((m) => ((normalized[m] ?? 0) * 100));
            rVals.push(rVals[0]);
            const theta = categoriesZh.concat(categoriesZh[0]);
            const hoverText = categories.map((m) => {
                const label = METRIC_LABELS[m] || m;
                return `${label}: ${formatRawValue(m, raw[m])}`;
            });
            hoverText.push(hoverText[0]);

            const trace = {
                type: 'scatterpolar',
                r: rVals,
                theta,
                fill: 'toself',
                name: subj.label || subj.subject_id,
                hoverinfo: 'text',
                text: hoverText,
                line: { color: getSubjectColor(subj.label || subj.subject_id) },
                fillcolor: hexToRgba(getSubjectColor(subj.label || subj.subject_id), 0.25),
            };
            const layout = {
                title: { text: subj.label || subj.subject_id, x: 0.5, y: 0.95, font: { size: 14 } },
                polar: { radialaxis: { visible: true, range: [0, 100] } },
                showlegend: false,
                margin: { t: 40, r: 20, b: 20, l: 20 },
                height: undefined,
                autosize: true,
            };
            if (chart.dataset.plotted) {
                await window.Plotly.react(chart, [trace], layout, { responsive: true, displayModeBar: false });
            } else {
                await window.Plotly.newPlot(chart, [trace], layout, { responsive: true, displayModeBar: false });
                chart.dataset.plotted = '1';
            }
        };

        // 建立 tabs（固定順序：國文/英文/數學/自然/地理/歷史/公民，若後端已排序，此處按原順序渲染）
        subjects.forEach((s, idx) => {
            const btn = document.createElement('button');
            btn.className = 'px-3 py-1 rounded-full text-sm border ' + (idx === activeIndex ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-100 text-gray-700 border-gray-200');
            btn.textContent = s.label || s.subject_id;
            btn.addEventListener('click', async () => {
                if (activeIndex === idx) return;
                activeIndex = idx;
                // 更新樣式
                Array.from(tabs.children).forEach((c, i) => {
                    c.className = 'px-3 py-1 rounded-full text-sm border ' + (i === activeIndex ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-100 text-gray-700 border-gray-200');
                });
                await draw(activeIndex);
            });
            tabs.appendChild(btn);
        });

        await draw(activeIndex);
    }

    // Render trend line charts with subject tabs (single chart, tab to switch)
    async function renderSubjectTrend(containerId, trendResponse) {
        await ensurePlotly();

        const el = document.getElementById(containerId);
        if (!el) return;
        el.style.overflow = 'hidden';

        const series = trendResponse?.series || [];
        if (!series.length) {
            el.innerHTML = '<div class="text-gray-500">暫無資料</div>';
            return;
        }

        // 清空容器，改為標籤切換 + 單一圖表
        el.innerHTML = '';
        const tabs = document.createElement('div');
        tabs.className = 'flex flex-wrap gap-2 mb-3';
        const chart = document.createElement('div');
        chart.style.height = '100%';
        chart.style.width = '100%';
        el.appendChild(tabs);
        el.appendChild(chart);

        let activeIndex = 0;

        const draw = async (idx) => {
            const s = series[idx];
            const x = (s.points || []).map((p) => p.x);
            const y = (s.points || []).map((p) => p.y);
            const color = getSubjectColor(s.label || s.subject_id);
            const trace = {
                type: 'scatter',
                mode: 'lines+markers',
                x,
                y,
                hovertemplate: '%{x}<br>值: %{y:.2f}<extra></extra>',
                line: { color },
                marker: { color },
            };
            const layout = {
                title: { text: s.label || s.subject_id, x: 0.5, y: 0.95, font: { size: 14 } },
                xaxis: { title: '時間' },
                yaxis: { title: trendResponse?.metric === 'score' ? '分數' : '正確率', rangemode: 'tozero' },
                showlegend: false,
                margin: { t: 40, r: 20, b: 40, l: 40 },
                height: undefined,
                autosize: true,
            };
            if (chart.dataset.plotted) {
                await window.Plotly.react(chart, [trace], layout, { responsive: true, displayModeBar: false });
            } else {
                await window.Plotly.newPlot(chart, [trace], layout, { responsive: true, displayModeBar: false });
                chart.dataset.plotted = '1';
            }
        };

        // 建立 tabs（固定順序：國文/英文/數學/自然/地理/歷史/公民，後端已排序）
        series.forEach((s, idx) => {
            const btn = document.createElement('button');
            btn.className = 'px-3 py-1 rounded-full text-sm border ' + (idx === activeIndex ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-100 text-gray-700 border-gray-200');
            btn.textContent = s.label || s.subject_id;
            btn.addEventListener('click', async () => {
                if (activeIndex === idx) return;
                activeIndex = idx;
                Array.from(tabs.children).forEach((c, i) => {
                    c.className = 'px-3 py-1 rounded-full text-sm border ' + (i === activeIndex ? 'bg-blue-600 text-white border-blue-600' : 'bg-gray-100 text-gray-700 border-gray-200');
                });
                await draw(activeIndex);
            });
            tabs.appendChild(btn);
        });

        await draw(activeIndex);
    }

    // expose to global
    window.renderSubjectRadar = renderSubjectRadar;
    window.renderSubjectTrend = renderSubjectTrend;
})();


