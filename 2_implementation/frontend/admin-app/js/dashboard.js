/**
 * 管理員儀表板功能 (Admin Dashboard) - InULearning 個人化學習平台
 * 
 * 功能：
 * - 系統統計資料載入
 * - 最近活動顯示
 * - 快速操作處理
 * - 即時資料更新
 */

class AdminDashboard {
    constructor() {
        this.apiClient = new ApiClient();
        this.statsData = {};
        this.activityData = [];
        this.init();
    }
    
    /**
     * 初始化儀表板
     */
    async init() {
        await this.loadDashboardData();
        this.setupEventListeners();
        this.startAutoRefresh();
    }
    
    /**
     * 載入儀表板資料
     */
    async loadDashboardData() {
        try {
            Utils.showLoading();
            
            // 並行載入統計資料和活動資料
            const [statsResponse, activityResponse] = await Promise.all([
                this.loadStats(),
                this.loadRecentActivity()
            ]);
            
            this.updateStatsDisplay(statsResponse);
            this.updateActivityDisplay(activityResponse);
            
        } catch (error) {
            console.error('載入儀表板資料失敗:', error);
            Utils.showAlert('載入資料失敗，請重新整理頁面', 'error');
        } finally {
            Utils.hideLoading();
        }
    }
    
    /**
     * 載入統計資料
     */
    async loadStats() {
        try {
            const response = await this.apiClient.get('/admin/stats');
            return response.success ? response.data : this.getDefaultStats();
        } catch (error) {
            console.error('載入統計資料失敗:', error);
            return this.getDefaultStats();
        }
    }
    
    /**
     * 載入最近活動
     */
    async loadRecentActivity() {
        try {
            const response = await this.apiClient.get('/admin/activity');
            return response.success ? response.data : this.getDefaultActivity();
        } catch (error) {
            console.error('載入活動資料失敗:', error);
            return this.getDefaultActivity();
        }
    }
    
    /**
     * 取得預設統計資料
     */
    getDefaultStats() {
        return {
            total_users: 0,
            total_questions: 0,
            active_sessions: 0,
            system_status: '正常'
        };
    }
    
    /**
     * 取得預設活動資料
     */
    getDefaultActivity() {
        return [
            {
                id: 1,
                type: 'system',
                title: '系統啟動',
                description: '管理員控制台已啟動',
                timestamp: new Date().toISOString()
            }
        ];
    }
    
    /**
     * 更新統計顯示
     */
    updateStatsDisplay(stats) {
        this.statsData = stats;
        
        // 更新統計卡片
        const elements = {
            'total-users': stats.total_users || 0,
            'total-questions': stats.total_questions || 0,
            'active-sessions': stats.active_sessions || 0,
            'system-status': stats.system_status || '正常'
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
        
        // 更新當前日期
        const currentDateElement = document.getElementById('current-date');
        if (currentDateElement) {
            currentDateElement.textContent = new Date().toLocaleDateString('zh-TW', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
            });
        }
    }
    
    /**
     * 更新活動顯示
     */
    updateActivityDisplay(activities) {
        this.activityData = activities;
        const activityList = document.getElementById('activity-list');
        
        if (!activityList) return;
        
        activityList.innerHTML = '';
        
        if (activities.length === 0) {
            activityList.innerHTML = `
                <div class="activity-item">
                    <div class="activity-content">
                        <div class="activity-title">尚無活動記錄</div>
                        <div class="activity-time">系統正在等待活動...</div>
                    </div>
                </div>
            `;
            return;
        }
        
        activities.forEach(activity => {
            const activityElement = this.createActivityElement(activity);
            activityList.appendChild(activityElement);
        });
    }
    
    /**
     * 建立活動元素
     */
    createActivityElement(activity) {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        
        const iconClass = this.getActivityIconClass(activity.type);
        const timeAgo = this.getTimeAgo(activity.timestamp);
        
        activityItem.innerHTML = `
            <div class="activity-icon ${iconClass}">
                <i class="fas ${this.getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-time">${timeAgo}</div>
            </div>
        `;
        
        return activityItem;
    }
    
    /**
     * 取得活動圖示類別
     */
    getActivityIconClass(type) {
        const iconMap = {
            'user': 'user',
            'question': 'question',
            'system': 'system'
        };
        return iconMap[type] || 'system';
    }
    
    /**
     * 取得活動圖示
     */
    getActivityIcon(type) {
        const iconMap = {
            'user': 'fa-user',
            'question': 'fa-question-circle',
            'system': 'fa-cog'
        };
        return iconMap[type] || 'fa-cog';
    }
    
    /**
     * 取得時間差
     */
    getTimeAgo(timestamp) {
        const now = new Date();
        const activityTime = new Date(timestamp);
        const diffInSeconds = Math.floor((now - activityTime) / 1000);
        
        if (diffInSeconds < 60) {
            return '剛剛';
        } else if (diffInSeconds < 3600) {
            return `${Math.floor(diffInSeconds / 60)} 分鐘前`;
        } else if (diffInSeconds < 86400) {
            return `${Math.floor(diffInSeconds / 3600)} 小時前`;
        } else {
            return `${Math.floor(diffInSeconds / 86400)} 天前`;
        }
    }
    
    /**
     * 設定事件監聽器
     */
    setupEventListeners() {
        // 快速操作卡片點擊事件
        const actionCards = document.querySelectorAll('.action-card');
        actionCards.forEach(card => {
            card.addEventListener('click', (e) => {
                const href = card.getAttribute('href');
                if (href) {
                    e.preventDefault();
                    window.location.href = href;
                }
            });
        });
        
        // 統計卡片點擊事件
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach(card => {
            card.addEventListener('click', () => {
                this.handleStatCardClick(card);
            });
        });
    }
    
    /**
     * 處理統計卡片點擊
     */
    handleStatCardClick(card) {
        const statType = this.getStatTypeFromCard(card);
        
        switch (statType) {
            case 'users':
                window.location.href = 'pages/users.html';
                break;
            case 'questions':
                window.location.href = 'pages/questions.html';
                break;
            case 'sessions':
                window.location.href = 'pages/sessions.html';
                break;
            case 'system':
                window.location.href = 'pages/system.html';
                break;
        }
    }
    
    /**
     * 從卡片取得統計類型
     */
    getStatTypeFromCard(card) {
        const icon = card.querySelector('.stat-icon i');
        if (!icon) return 'system';
        
        const iconClass = icon.className;
        if (iconClass.includes('fa-users')) return 'users';
        if (iconClass.includes('fa-question-circle')) return 'questions';
        if (iconClass.includes('fa-chart-line')) return 'sessions';
        if (iconClass.includes('fa-server')) return 'system';
        
        return 'system';
    }
    
    /**
     * 開始自動重新整理
     */
    startAutoRefresh() {
        // 每 30 秒重新整理一次活動資料
        setInterval(async () => {
            try {
                const activityResponse = await this.loadRecentActivity();
                this.updateActivityDisplay(activityResponse);
            } catch (error) {
                console.error('自動重新整理失敗:', error);
            }
        }, 30000);
        
        // 每 5 分鐘重新整理一次統計資料
        setInterval(async () => {
            try {
                const statsResponse = await this.loadStats();
                this.updateStatsDisplay(statsResponse);
            } catch (error) {
                console.error('自動重新整理統計失敗:', error);
            }
        }, 300000);
    }
    
    /**
     * 手動重新整理
     */
    async refresh() {
        await this.loadDashboardData();
        Utils.showAlert('資料已重新整理', 'success');
    }
    
    /**
     * 取得統計資料
     */
    getStats() {
        return this.statsData;
    }
    
    /**
     * 取得活動資料
     */
    getActivity() {
        return this.activityData;
    }
}

// 全域儀表板實例
const adminDashboard = new AdminDashboard(); 