// 現代化教師儀表板 JavaScript
class ModernTeacherDashboard {
    constructor() {
        this.data = {
            teacher: {
                name: '王老師',
                displayName: '王老師',
                subject: '數學',
                classes: []
            },
            stats: {
                totalClasses: 0,
                totalStudents: 0,
                activeSessions: 0,
                avgScore: 0
            },
            highlights: {
                todayClasses: [],
                pendingAssignments: 0,
                attentionNeeded: 0
            },
            recentActivity: []
        };

        this.init();
    }

    async init() {
        this.showLoading();
        await this.loadDashboardData();
        this.setupEventListeners();
        this.renderDashboard();
        this.startAutoRefresh();
        this.hideLoading();
        this.addAnimations();
    }

    async loadDashboardData() {
        try {
            // 嘗試從 API 載入真實資料
            const [statsResponse, classesResponse, activityResponse] = await Promise.allSettled([
                fetch('/api/teacher/stats'),
                fetch('/api/teacher/classes'),
                fetch('/api/teacher/activity')
            ]);

            if (statsResponse.status === 'fulfilled' && statsResponse.value.ok) {
                const stats = await statsResponse.value.json();
                this.data.stats = { ...this.data.stats, ...stats };
                console.log('✅ 成功載入統計資料');
            }

            if (classesResponse.status === 'fulfilled' && classesResponse.value.ok) {
                const classes = await classesResponse.value.json();
                this.data.teacher.classes = classes.classes || [];
                console.log('✅ 成功載入班級資料');
            }

            if (activityResponse.status === 'fulfilled' && activityResponse.value.ok) {
                const activity = await activityResponse.value.json();
                this.data.recentActivity = activity.activities || [];
                console.log('✅ 成功載入活動資料');
            }

        } catch (error) {
            console.log('⚠️ API 載入失敗，使用模擬資料:', error.message);
        }

        // 使用模擬資料補充
        this.loadMockData();
    }

    loadMockData() {
        // 統計資料
        this.data.stats = {
            totalClasses: 3,
            totalStudents: 96,
            activeSessions: 24,
            avgScore: 85.7
        };

        // 今日重點
        this.data.highlights = {
            todayClasses: [
                { time: '09:00', class: '三年一班', subject: '數學' },
                { time: '14:00', class: '三年二班', subject: '數學' },
                { time: '15:30', class: '三年三班', subject: '數學' }
            ],
            pendingAssignments: 12,
            attentionNeeded: 3
        };

        // 班級資料
        this.data.teacher.classes = [
            {
                id: 1,
                name: '三年一班',
                students: 32,
                avgScore: 87.5,
                activeStudents: 28,
                lastActivity: '2小時前'
            },
            {
                id: 2,
                name: '三年二班',
                students: 30,
                avgScore: 84.2,
                activeStudents: 25,
                lastActivity: '1小時前'
            },
            {
                id: 3,
                name: '三年三班',
                students: 34,
                avgScore: 85.8,
                activeStudents: 30,
                lastActivity: '30分鐘前'
            }
        ];

        // 最近活動
        this.data.recentActivity = [
            {
                type: 'assignment',
                icon: 'fas fa-tasks',
                title: '新作業已發布',
                description: '三年一班 - 二次函數練習',
                time: '10分鐘前'
            },
            {
                type: 'grade',
                icon: 'fas fa-star',
                title: '成績已更新',
                description: '李小華在數學測驗中獲得95分',
                time: '25分鐘前'
            },
            {
                type: 'student',
                icon: 'fas fa-user-graduate',
                title: '學生提問',
                description: '王小明對三角函數有疑問',
                time: '1小時前'
            },
            {
                type: 'system',
                icon: 'fas fa-bell',
                title: '系統通知',
                description: '本週學習報告已生成',
                time: '2小時前'
            },
            {
                type: 'achievement',
                icon: 'fas fa-trophy',
                title: '學習成就',
                description: '三年二班整體進步顯著',
                time: '3小時前'
            }
        ];
    }

    setupEventListeners() {
        // 用戶下拉選單
        const userToggle = document.querySelector('.user-dropdown-toggle');
        const userMenu = document.querySelector('.user-dropdown-menu');

        if (userToggle && userMenu) {
            userToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                userMenu.classList.toggle('show');
            });

            document.addEventListener('click', () => {
                userMenu.classList.remove('show');
            });
        }

        // 登出功能
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });
        }

        // 重新整理按鈕
        const refreshBtn = document.querySelector('.refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshDashboard();
            });
        }
    }

    renderDashboard() {
        this.updateTeacherInfo();
        this.updateStats();
        this.updateHighlights();
        this.renderClasses();
        this.renderRecentActivity();
        this.updateCurrentDate();
    }

    updateTeacherInfo() {
        const teacherNameElements = document.querySelectorAll('#teacher-name, #teacher-display-name');
        teacherNameElements.forEach(element => {
            if (element) {
                element.textContent = this.data.teacher.displayName;
            }
        });
    }

    updateStats() {
        const stats = this.data.stats;

        this.updateStatElement('total-classes', stats.totalClasses, '+2');
        this.updateStatElement('total-students', stats.totalStudents, '+8');
        this.updateStatElement('active-sessions', stats.activeSessions, '+5');
        this.updateStatElement('avg-score', `${stats.avgScore}%`, '+2.3%');
    }

    updateStatElement(id, value, trend) {
        const element = document.getElementById(id);
        const trendElement = document.getElementById(id.replace('total-', '').replace('avg-', '') + '-trend');

        if (element) {
            this.animateNumber(element, value);
        }

        if (trendElement) {
            trendElement.innerHTML = `<i class="fas fa-arrow-up"></i> ${trend}`;
        }
    }

    animateNumber(element, targetValue) {
        const isPercentage = typeof targetValue === 'string' && targetValue.includes('%');
        const numericValue = parseFloat(targetValue);
        const startValue = 0;
        const duration = 1500;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // 使用緩動函數
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = startValue + (numericValue - startValue) * easeOutQuart;

            if (isPercentage) {
                element.textContent = `${Math.round(currentValue * 10) / 10}%`;
            } else {
                element.textContent = Math.round(currentValue);
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    updateHighlights() {
        const highlights = this.data.highlights;

        // 今日課程
        const todayClassesElement = document.getElementById('today-classes');
        if (todayClassesElement) {
            if (highlights.todayClasses.length > 0) {
                const classesText = highlights.todayClasses
                    .map(c => `${c.time} ${c.class}`)
                    .join(', ');
                todayClassesElement.textContent = classesText;
            } else {
                todayClassesElement.textContent = '今日無課程安排';
            }
        }

        // 待批改作業
        const pendingElement = document.getElementById('pending-assignments');
        if (pendingElement) {
            pendingElement.textContent = `${highlights.pendingAssignments} 份作業待批改`;
        }

        // 需要關注
        const attentionElement = document.getElementById('attention-needed');
        if (attentionElement) {
            attentionElement.textContent = `${highlights.attentionNeeded} 位學生需要關注`;
        }
    }

    renderClasses() {
        const classesGrid = document.getElementById('classes-grid');
        if (!classesGrid) return;

        if (this.data.teacher.classes.length === 0) {
            classesGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: rgba(255, 255, 255, 0.7);">
                    <i class="fas fa-users" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>尚未有班級資料</p>
                </div>
            `;
            return;
        }

        classesGrid.innerHTML = this.data.teacher.classes.map(classData => `
            <div class="class-card fade-in-up" onclick="location.href='pages/students-enhanced.html?classId=${classData.id}&class=${encodeURIComponent(classData.name)}'">
                <h4>${classData.name}</h4>
                <p>${classData.students} 位學生</p>
                <p>平均分數: ${classData.avgScore}%</p>
                <p>活躍學生: ${classData.activeStudents}/${classData.students}</p>
                <p style="font-size: 0.8rem; margin-top: 0.5rem;">最後活動: ${classData.lastActivity}</p>
            </div>
        `).join('');
    }

    renderRecentActivity() {
        const activityList = document.getElementById('activity-list');
        if (!activityList) return;

        if (this.data.recentActivity.length === 0) {
            activityList.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: rgba(255, 255, 255, 0.7);">
                    <i class="fas fa-clock" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                    <p>暫無最近活動</p>
                </div>
            `;
            return;
        }

        activityList.innerHTML = this.data.recentActivity.map(activity => `
            <div class="activity-item fade-in-up">
                <div class="activity-icon">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <h5>${activity.title}</h5>
                    <p>${activity.description}</p>
                </div>
                <div class="activity-time">${activity.time}</div>
            </div>
        `).join('');
    }

    updateCurrentDate() {
        const dateElement = document.getElementById('current-date');
        if (dateElement) {
            const now = new Date();
            const options = {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
            };
            dateElement.textContent = now.toLocaleDateString('zh-TW', options);
        }
    }

    addAnimations() {
        // 為元素添加淡入動畫
        const elements = document.querySelectorAll('.stat-card, .highlight-card, .action-card');
        elements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.1}s`;
            element.classList.add('fade-in-up');
        });
    }

    showLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 500);
        }
    }

    async refreshDashboard() {
        this.showLoading();
        await this.loadDashboardData();
        this.renderDashboard();
        this.hideLoading();

        // 顯示刷新成功提示
        this.showNotification('儀表板已更新', 'success');
    }

    showNotification(message, type = 'info') {
        // 創建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            color: white;
            box-shadow: var(--shadow-soft);
            z-index: 10000;
            transform: translateX(100%);
            transition: var(--transition);
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // 顯示動畫
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // 自動隱藏
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    handleLogout() {
        if (confirm('確定要登出嗎？')) {
            // 清除本地存儲
            localStorage.removeItem('teacher_token');
            sessionStorage.clear();

            // 重定向到登入頁面
            window.location.href = '../shared/auth/login.html';
        }
    }

    startAutoRefresh() {
        // 每5分鐘自動刷新一次數據
        setInterval(() => {
            this.loadDashboardData().then(() => {
                this.renderDashboard();
            });
        }, 5 * 60 * 1000);
    }
}

// 全域函數
function refreshDashboard() {
    if (window.modernDashboard) {
        window.modernDashboard.refreshDashboard();
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    window.modernDashboard = new ModernTeacherDashboard();
});