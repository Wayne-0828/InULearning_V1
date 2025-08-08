// Dashboard page logic to fetch analytics data and render charts

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Ensure auth existence; if no token, show login links (handled by shared header usually)
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        const radarContainer = document.getElementById('subjectChart');
        const trendContainer = document.getElementById('trendChart');

        if (radarContainer) {
            radarContainer.innerHTML = '<div class="flex items-center justify-center h-full text-gray-500"><span class="material-icons mr-2">bar_chart</span>載入圖表中...</div>';
        }
        if (trendContainer) {
            trendContainer.innerHTML = '<div class="flex items-center justify-center h-full text-gray-500"><span class="material-icons mr-2">trending_up</span>載入圖表中...</div>';
        }

        // Fetch radar and trend in parallel
        const [radarData, trendData] = await Promise.all([
            window.learningAPI.getSubjectRadar({ window: '30d' }),
            window.learningAPI.getSubjectTrend({ metric: 'accuracy', window: '30d', limit: 100 })
        ]);

        // Render charts
        if (radarContainer) {
            await window.renderSubjectRadar('subjectChart', radarData);
        }
        if (trendContainer) {
            await window.renderSubjectTrend('trendChart', trendData);
        }
    } catch (err) {
        console.error('Dashboard init error:', err);
        const radarContainer = document.getElementById('subjectChart');
        const trendContainer = document.getElementById('trendChart');
        if (radarContainer) {
            radarContainer.innerHTML = '<div class="text-red-500">圖表載入失敗</div>';
        }
        if (trendContainer) {
            trendContainer.innerHTML = '<div class="text-red-500">圖表載入失敗</div>';
        }
    }
});


