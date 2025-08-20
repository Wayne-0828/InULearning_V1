/**
 * 教師儀表板模組 - 增強版
 * 顯示課程統計、學生進度、最近活動等資訊
 */

// 全域變數
let dashboardData = {
    stats: {},
    classes: [],
    activities: [],
    highlights: {}
};

let apiConnected = false;

// 初始化
document.addEventListener('DOMContentLoaded', async function () {
    setupCurrentDate();
    await loadDashboardData();
});

/**
 * 設定當前日期
 */
function setupCurrentDate() {
    const currentDateEl = document.getElementById('current-date');
    if (currentDateEl) {
        const now = new Date();
        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
        };
        currentDateEl.textContent = now.toLocaleDateString('zh-TW', options);
    }
}

/**
 * 載入儀表板資料
 */
async function loadDashboardData() {
    showApiStatus('載入儀表板資料...');

    try {
        // 測試 API 連接
        await testApiConnection();

        // 載入各種資料
        await Promise.all([
            loadStats(),
            loadClasses(),
            loadRecentActivities(),
            loadTodayHighlights()
        ]);

        showApiStatus('資料載入完成', 'connected');

    } catch (error) {
        console.warn('API 連接失敗，使用模擬資料:', error);
        apiConnected = false;
        loadMockData();
        showApiStatus('API 無法連接，顯示模擬資料', 'error');
    }
}

/**
 * 測試 API 連接
 */
async function testApiConnection() {
    try {
        await apiClient.get('/learning/health');
        apiConnected = true;
        console.log('✅ API 連接成功');
    } catch (error) {
        apiConnected = false;
        throw error;
    }
}

/**
 * 載入統計資料
 */
async function loadStats() {
    try {
        if (!apiConnected) throw new Error('API 未連接');

        // 嘗試從學習記錄獲取統計
        const response = await apiClient.get('/learning/records');

        if (response && response.sessions) {
            processStatsFromSessions(response.sessions);
        } else {
            throw new Error('無統計資料');
        }

    } catch (error) {
        console.warn('載入統計資料失敗:', error.message);
        generateMockStats();
    }
}

/**
 * 從會話資料處理統計
 */
function processStatsFromSessions(sessions) {
    const uniqueStudents = new Set();
    const uniqueClasses = new Set();
    let totalScore = 0;
    let scoreCount = 0;

    sessions.forEach(session => {
        if (session.user_id) uniqueStudents.add(session.user_id);
        if (session.class) uniqueClasses.add(session.class);
        if (session.score !== undefined && session.score !== null) {
            totalScore += session.score;
            scoreCount++;
        }
    });

    dashboardData.stats = {
        totalClasses: uniqueClasses.size,
        totalStudents: uniqueStudents.size,
        activeSessions: sessions.length,
        avgScore: scoreCount > 0 ? Math.round(totalScore / scoreCount) : 0
    };

    renderStats();
}

/**
 * 生成模擬統計資料
 */
function generateMockStats() {
    dashboardData.stats = {
        totalClasses: Math.floor(Math.random() * 5) + 3, // 3-7 個班級
        totalStudents: Math.floor(Math.random() * 50) + 80, // 80-130 個學生
        activeSessions: Math.floor(Math.random() * 20) + 10, // 10-30 個活躍會話
        avgScore: Math.floor(Math.random() * 20) + 75 // 75-95 分
    };

    renderStats();
}

/**
 * 載入班級資料
 */
async function loadClasses() {
    try {
        if (!apiConnected) throw new Error('API 未連接');

        // 嘗試載入班級資料
                    const response = await apiClient.get('/relationships/teacher-class');

        if (response && (response.data || response.items || response.length > 0)) {
            dashboardData.classes = response.data || response.items || response || [];
        } else {
            throw new Error('無班級資料');
        }

    } catch (error) {
        console.warn('載入班級資料失敗:', error.message);
        generateMockClasses();
    }

    renderClasses();
}

/**
 * 生成模擬班級資料
 */
function generateMockClasses() {
    const classNames = ['七年一班', '七年二班', '七年三班', '八年一班', '八年二班'];

    dashboardData.classes = classNames.map((name, index) => ({
        id: index + 1,
        class_name: name,
        name: name,
        student_count: Math.floor(Math.random() * 15) + 25, // 25-40 學生
        avg_score: Math.floor(Math.random() * 20) + 75, // 75-95 分
        last_activity: generateLastActivity()
    }));
}

/**
 * 載入最近活動
 */
async function loadRecentActivities() {
    try {
        if (!apiConnected) throw new Error('API 未連接');

        const response = await apiClient.get('/learning/recent');

        if (response && response.sessions) {
            processActivitiesFromSessions(response.sessions);
        } else {
            throw new Error('無活動資料');
        }

    } catch (error) {
        console.warn('載入活動資料失敗:', error.message);
        generateMockActivities();
    }

    renderRecentActivities();
}

/**
 * 從會話資料處理活動
 */
function processActivitiesFromSessions(sessions) {
    dashboardData.activities = sessions.slice(0, 5).map(session => ({
        type: 'quiz_completed',
        description: `${session.user_name || '學生'} 完成了 ${session.subject || '練習'}`,
        timestamp: session.created_at || new Date().toISOString(),
        user: session.user_name || '學生'
    }));
}

/**
 * 生成模擬活動資料
 */
function generateMockActivities() {
    const activities = [
        { type: 'quiz_completed', description: '王小明完成了數學練習', user: '王小明' },
        { type: 'assignment_submitted', description: '李小華提交了英文作業', user: '李小華' },
        { type: 'student_joined', description: '張小美加入了七年三班', user: '張小美' },
        { type: 'assignment_graded', description: '批改了陳小強的自然作業', user: '陳小強' },
        { type: 'quiz_completed', description: '林小芳完成了國文測驗', user: '林小芳' }
    ];

    dashboardData.activities = activities.map(activity => ({
        ...activity,
        timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
    }));
}

/**
 * 載入今日重點
 */
async function loadTodayHighlights() {
    // 生成今日重點資料
    dashboardData.highlights = {
        todayClasses: `${Math.floor(Math.random() * 3) + 2} 堂課程`,
        pendingAssignments: `${Math.floor(Math.random() * 8) + 2} 份作業`,
        attentionNeeded: `${Math.floor(Math.random() * 3) + 1} 位學生`
    };

    renderTodayHighlights();
}

/**
 * 載入模擬資料
 */
function loadMockData() {
    generateMockStats();
    generateMockClasses();
    generateMockActivities();
    loadTodayHighlights();
}

/**
 * 渲染統計資料
 */
function renderStats() {
    const stats = dashboardData.stats;

    document.getElementById('total-classes').textContent = stats.totalClasses || 0;
    document.getElementById('total-students').textContent = stats.totalStudents || 0;
    document.getElementById('active-sessions').textContent = stats.activeSessions || 0;
    document.getElementById('avg-score').textContent = `${stats.avgScore || 0}%`;

    // 更新趨勢指示器
    updateTrendIndicators();
}

/**
 * 更新趨勢指示器
 */
function updateTrendIndicators() {
    const trends = {
        'classes-trend': Math.floor(Math.random() * 3),
        'students-trend': Math.floor(Math.random() * 10) + 5,
        'sessions-trend': Math.floor(Math.random() * 15) + 5,
        'score-trend': Math.floor(Math.random() * 5) + 2
    };

    Object.entries(trends).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = `<i class="fas fa-arrow-up"></i> +${value}${id.includes('score') ? '%' : ''}`;
        }
    });
}

/**
 * 渲染班級概覽
 */
function renderClasses() {
    const classesGrid = document.getElementById('classes-grid');
    if (!classesGrid) return;

    if (dashboardData.classes.length === 0) {
        classesGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-users"></i>
                <h3>尚未建立班級</h3>
                <p>點擊「班級管理」開始建立您的第一個班級</p>
            </div>
        `;
        return;
    }

    classesGrid.innerHTML = dashboardData.classes.slice(0, 6).map(cls => `
        <div class="class-card" onclick="location.href='pages/students-enhanced.html?classId=${cls.id}&class=${encodeURIComponent(cls.class_name || cls.name)}'">
            <div class="class-header">
                <h3>${cls.class_name || cls.name}</h3>
                <div class="class-badge">${cls.student_count || 0} 人</div>
            </div>
            <div class="class-stats">
                <div class="class-stat">
                    <span class="stat-label">平均分數</span>
                    <span class="stat-value">${cls.avg_score || 0}</span>
                </div>
                <div class="class-stat">
                    <span class="stat-label">最後活動</span>
                    <span class="stat-value">${cls.last_activity || '今天'}</span>
                </div>
            </div>
            <div class="class-actions">
                <button class="btn-sm" onclick="event.stopPropagation(); viewClassDetails('${cls.id}')">
                    <i class="fas fa-eye"></i> 查看
                </button>
                <button class="btn-sm" onclick="event.stopPropagation(); manageClass('${cls.id}')">
                    <i class="fas fa-cog"></i> 管理
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * 渲染今日重點
 */
function renderTodayHighlights() {
    const highlights = dashboardData.highlights;

    document.getElementById('today-classes').textContent = highlights.todayClasses || '載入中...';
    document.getElementById('pending-assignments').textContent = highlights.pendingAssignments || '載入中...';
    document.getElementById('attention-needed').textContent = highlights.attentionNeeded || '載入中...';
}

/**
 * 渲染最近活動
 */
function renderRecentActivities() {
    const activitiesList = document.getElementById('activity-list');
    if (!activitiesList) return;

    if (dashboardData.activities.length === 0) {
        activitiesList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-history"></i>
                <h3>暫無最近活動</h3>
                <p>學生開始學習後，活動記錄會顯示在這裡</p>
            </div>
        `;
        return;
    }

    activitiesList.innerHTML = dashboardData.activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon ${getActivityIconClass(activity.type)}">
                <i class="${getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <p class="activity-text">${activity.description}</p>
                <span class="activity-time">${formatTimeAgo(activity.timestamp)}</span>
            </div>
        </div>
    `).join('');
}

/**
 * 獲取活動圖標
 */
function getActivityIcon(type) {
    const icons = {
        'assignment_submitted': 'fas fa-file-alt',
        'assignment_graded': 'fas fa-check-circle',
        'student_joined': 'fas fa-user-plus',
        'course_created': 'fas fa-plus-circle',
        'quiz_completed': 'fas fa-question-circle'
    };
    return icons[type] || 'fas fa-info-circle';
}

/**
 * 獲取活動圖標樣式
 */
function getActivityIconClass(type) {
    const classes = {
        'assignment_submitted': 'info',
        'assignment_graded': 'success',
        'student_joined': 'primary',
        'course_created': 'warning',
        'quiz_completed': 'secondary'
    };
    return classes[type] || 'secondary';
}

/**
 * 格式化時間
 */
function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));

    if (diffInMinutes < 1) return '剛剛';
    if (diffInMinutes < 60) return `${diffInMinutes} 分鐘前`;

    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours} 小時前`;

    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays} 天前`;

    return time.toLocaleDateString('zh-TW');
}

/**
 * 生成最後活動時間
 */
function generateLastActivity() {
    const activities = ['今天', '昨天', '2 天前', '3 天前', '1 週前'];
    return activities[Math.floor(Math.random() * activities.length)];
}

/**
 * 顯示 API 狀態
 */
function showApiStatus(message, type = 'warning') {
    const statusEl = document.getElementById('apiStatus');
    const textEl = document.getElementById('statusText');

    if (statusEl && textEl) {
        statusEl.style.display = 'block';
        statusEl.className = `api-status ${type}`;
        textEl.textContent = message;

        // 3秒後隱藏狀態訊息（除非是錯誤狀態）
        if (type !== 'error') {
            setTimeout(() => {
                statusEl.style.display = 'none';
            }, 3000);
        }
    }
}

/**
 * 重新整理儀表板
 */
function refreshDashboard() {
    loadDashboardData();
}

/**
 * 查看班級詳情
 */
function viewClassDetails(classId) {
    const cls = dashboardData.classes.find(c => c.id == classId);
    if (cls) {
        location.href = `pages/students-enhanced.html?classId=${classId}&class=${encodeURIComponent(cls.class_name || cls.name)}`;
    }
}

/**
 * 管理班級
 */
function manageClass(classId) {
    location.href = `pages/classes.html?classId=${classId}`;
}