/**
 * 家長儀表板模組
 * 顯示子女學習統計、進度追蹤、最近活動等資訊
 */
class ParentDashboard {
    constructor() {
        this.currentPage = 'dashboard';
        this.refreshInterval = null;
        this.statsData = {};
        this.childrenData = [];
        this.activitiesData = [];
        this.notificationsData = [];
        
        this.init();
    }

    init() {
        this.loadDashboardData();
        this.setupAutoRefresh();
        this.bindEvents();
    }

    async loadDashboardData() {
        try {
            // 顯示載入狀態
            this.showLoading(true);
            
            // 並行加載所有數據
            await Promise.all([
                this.loadStats(),
                this.loadChildrenData(),
                this.loadRecentActivities(),
                this.loadNotifications()
            ]);
            
            // 渲染所有數據
            this.renderAllData();
            
        } catch (error) {
            console.error('載入儀表板數據失敗:', error);
            this.showNotification('載入數據失敗，請稍後重試', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async loadStats() {
        try {
            const response = await apiClient.get('/api/v1/parents/dashboard/stats');
            this.statsData = response.data;
        } catch (error) {
            console.error('載入統計數據失敗:', error);
            // 使用模擬數據
            this.statsData = {
                totalChildren: 2,
                activeCourses: 8,
                completedAssignments: 45,
                averageScore: 85.5,
                studyTime: 12.5,
                attendanceRate: 95.2
            };
        }
    }

    async loadChildrenData() {
        try {
            const response = await apiClient.get('/api/v1/parents/children');
            this.childrenData = response.data;
        } catch (error) {
            console.error('載入子女數據失敗:', error);
            // 使用模擬數據
            this.childrenData = [
                {
                    id: 1,
                    name: '小明',
                    grade: '三年級',
                    avatar: '/assets/images/avatar-child-1.jpg',
                    currentCourse: '數學',
                    progress: 75,
                    lastActive: '2024-01-15T10:30:00Z',
                    status: 'online'
                },
                {
                    id: 2,
                    name: '小華',
                    grade: '一年級',
                    avatar: '/assets/images/avatar-child-2.jpg',
                    currentCourse: '國語',
                    progress: 60,
                    lastActive: '2024-01-15T09:15:00Z',
                    status: 'offline'
                }
            ];
        }
    }

    async loadRecentActivities() {
        try {
            const response = await apiClient.get('/api/v1/parents/activities');
            this.activitiesData = response.data;
        } catch (error) {
            console.error('載入最近活動失敗:', error);
            // 使用模擬數據
            this.activitiesData = [
                {
                    id: 1,
                    childName: '小明',
                    type: 'assignment_completed',
                    title: '完成數學作業',
                    description: '完成了第三章的練習題',
                    timestamp: '2024-01-15T10:30:00Z',
                    score: 95
                },
                {
                    id: 2,
                    childName: '小華',
                    type: 'course_started',
                    title: '開始新課程',
                    description: '開始學習國語第二單元',
                    timestamp: '2024-01-15T09:15:00Z'
                },
                {
                    id: 3,
                    childName: '小明',
                    type: 'achievement',
                    title: '獲得成就',
                    description: '連續學習7天',
                    timestamp: '2024-01-14T16:45:00Z'
                }
            ];
        }
    }

    async loadNotifications() {
        try {
            const response = await apiClient.get('/api/v1/parents/notifications');
            this.notificationsData = response.data;
        } catch (error) {
            console.error('載入通知失敗:', error);
            // 使用模擬數據
            this.notificationsData = [
                {
                    id: 1,
                    type: 'assignment_due',
                    title: '作業提醒',
                    message: '小明的數學作業將於明天到期',
                    timestamp: '2024-01-15T08:00:00Z',
                    read: false
                },
                {
                    id: 2,
                    type: 'progress_report',
                    title: '學習報告',
                    message: '小華的週學習報告已生成',
                    timestamp: '2024-01-14T18:00:00Z',
                    read: true
                }
            ];
        }
    }

    renderAllData() {
        this.renderStats();
        this.renderChildrenOverview();
        this.renderRecentActivities();
        this.renderNotifications();
    }

    renderStats() {
        const statsContainer = document.getElementById('stats-grid');
        if (!statsContainer) return;

        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-users"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.statsData.totalChildren || 0}</h3>
                    <p>子女數量</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-book"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.statsData.activeCourses || 0}</h3>
                    <p>進行中課程</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.statsData.completedAssignments || 0}</h3>
                    <p>已完成作業</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-chart-line"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.statsData.averageScore || 0}%</h3>
                    <p>平均分數</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.statsData.studyTime || 0}h</h3>
                    <p>本週學習時數</p>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-calendar-check"></i>
                </div>
                <div class="stat-content">
                    <h3>${this.statsData.attendanceRate || 0}%</h3>
                    <p>出勤率</p>
                </div>
            </div>
        `;
    }

    renderChildrenOverview() {
        const childrenContainer = document.getElementById('children-overview');
        if (!childrenContainer) return;

        childrenContainer.innerHTML = `
            <div class="children-grid">
                ${this.childrenData.map(child => `
                    <div class="child-card" data-child-id="${child.id}">
                        <div class="child-header">
                            <div class="child-avatar">
                                <img src="${child.avatar}" alt="${child.name}" onerror="this.src='/assets/images/default-avatar.jpg'">
                                <span class="status-indicator ${child.status}"></span>
                            </div>
                            <div class="child-info">
                                <h4>${child.name}</h4>
                                <p>${child.grade}</p>
                            </div>
                            <div class="child-actions">
                                <button class="btn btn-sm btn-outline-primary" onclick="parentDashboard.viewChildProgress(${child.id})">
                                    <i class="fas fa-chart-bar"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="parentDashboard.viewChildDetails(${child.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </div>
                        </div>
                        <div class="child-progress">
                            <div class="progress-info">
                                <span>${child.currentCourse}</span>
                                <span>${child.progress}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${child.progress}%"></div>
                            </div>
                        </div>
                        <div class="child-footer">
                            <small>最後活動: ${this.formatTime(child.lastActive)}</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderRecentActivities() {
        const activitiesContainer = document.getElementById('recent-activities');
        if (!activitiesContainer) return;

        activitiesContainer.innerHTML = `
            <div class="activities-list">
                ${this.activitiesData.map(activity => `
                    <div class="activity-item">
                        <div class="activity-icon ${this.getActivityIconClass(activity.type)}">
                            <i class="${this.getActivityIcon(activity.type)}"></i>
                        </div>
                        <div class="activity-content">
                            <div class="activity-header">
                                <h5>${activity.title}</h5>
                                <span class="activity-time">${this.formatTime(activity.timestamp)}</span>
                            </div>
                            <p>${activity.childName} - ${activity.description}</p>
                            ${activity.score ? `<span class="activity-score">分數: ${activity.score}</span>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderNotifications() {
        const notificationsContainer = document.getElementById('notifications-list');
        if (!notificationsContainer) return;

        const unreadCount = this.notificationsData.filter(n => !n.read).length;
        
        // 更新通知計數
        const notificationBadge = document.querySelector('.notification-badge');
        if (notificationBadge) {
            notificationBadge.textContent = unreadCount;
            notificationBadge.style.display = unreadCount > 0 ? 'block' : 'none';
        }

        notificationsContainer.innerHTML = `
            ${this.notificationsData.map(notification => `
                <div class="notification-item ${notification.read ? 'read' : 'unread'}" data-notification-id="${notification.id}">
                    <div class="notification-icon">
                        <i class="${this.getNotificationIcon(notification.type)}"></i>
                    </div>
                    <div class="notification-content">
                        <h6>${notification.title}</h6>
                        <p>${notification.message}</p>
                        <small>${this.formatTime(notification.timestamp)}</small>
                    </div>
                    <div class="notification-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="parentDashboard.markAsRead(${notification.id})">
                            <i class="fas fa-check"></i>
                        </button>
                    </div>
                </div>
            `).join('')}
        `;
    }

    getActivityIcon(type) {
        const icons = {
            'assignment_completed': 'fas fa-check-circle',
            'course_started': 'fas fa-play-circle',
            'achievement': 'fas fa-trophy',
            'exam_completed': 'fas fa-file-alt',
            'course_completed': 'fas fa-graduation-cap',
            'login': 'fas fa-sign-in-alt'
        };
        return icons[type] || 'fas fa-info-circle';
    }

    getActivityIconClass(type) {
        const classes = {
            'assignment_completed': 'success',
            'course_started': 'primary',
            'achievement': 'warning',
            'exam_completed': 'info',
            'course_completed': 'success',
            'login': 'secondary'
        };
        return classes[type] || 'secondary';
    }

    getNotificationIcon(type) {
        const icons = {
            'assignment_due': 'fas fa-exclamation-triangle',
            'progress_report': 'fas fa-chart-bar',
            'achievement': 'fas fa-trophy',
            'system': 'fas fa-cog',
            'message': 'fas fa-envelope'
        };
        return icons[type] || 'fas fa-bell';
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return '剛剛';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}分鐘前`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}小時前`;
        if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
        
        return date.toLocaleDateString('zh-TW');
    }

    setupAutoRefresh() {
        // 每5分鐘自動刷新數據
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
    }

    bindEvents() {
        // 快速操作按鈕事件
        document.addEventListener('click', (e) => {
            if (e.target.matches('.quick-action-btn')) {
                const action = e.target.dataset.action;
                this.handleQuickAction(action);
            }
        });

        // 子女卡片點擊事件
        document.addEventListener('click', (e) => {
            const childCard = e.target.closest('.child-card');
            if (childCard) {
                const childId = childCard.dataset.childId;
                this.viewChildDetails(parseInt(childId));
            }
        });
    }

    handleQuickAction(actionType) {
        switch (actionType) {
            case 'view_progress':
                this.openProgress();
                break;
            case 'view_reports':
                this.openReports();
                break;
            case 'contact_teacher':
                this.openCommunication();
                break;
            case 'view_schedule':
                this.openSchedule();
                break;
            default:
                console.log('未知的快速操作:', actionType);
        }
    }

    viewChildProgress(childId) {
        parentApp.navigateTo('progress', { childId });
    }

    viewChildDetails(childId) {
        parentApp.navigateTo('children', { childId });
    }

    openProgress() {
        parentApp.navigateTo('progress');
    }

    openReports() {
        parentApp.navigateTo('reports');
    }

    openCommunication() {
        parentApp.navigateTo('communication');
    }

    openSchedule() {
        parentApp.navigateTo('schedule');
    }

    async markAsRead(notificationId) {
        try {
            await apiClient.put(`/api/v1/parents/notifications/${notificationId}/read`);
            
            // 更新本地數據
            const notification = this.notificationsData.find(n => n.id === notificationId);
            if (notification) {
                notification.read = true;
                this.renderNotifications();
            }
        } catch (error) {
            console.error('標記通知為已讀失敗:', error);
        }
    }

    showLoading(show) {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = show ? 'block' : 'none';
        }
    }

    showNotification(message, type = 'info') {
        if (window.parentApp) {
            parentApp.showNotification(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    refresh() {
        this.loadDashboardData();
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

// 初始化儀表板
const parentDashboard = new ParentDashboard();
window.parentDashboard = parentDashboard; 