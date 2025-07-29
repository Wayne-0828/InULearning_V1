/**
 * 學習歷程頁面 JavaScript
 * 實現練習記錄查看功能
 */

class HistoryManager {
    constructor() {
        this.currentPage = 1;
        this.pageSize = 10;
        this.totalRecords = 0;
        this.filters = {
            subject: '',
            edition: '',
            dateRange: '30'
        };
        this.records = [];
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadLearningRecords();
        this.loadStatistics();
    }

    bindEvents() {
        // 篩選按鈕
        const applyFilterBtn = document.getElementById('applyFilter');
        if (applyFilterBtn) {
            applyFilterBtn.addEventListener('click', () => this.applyFilters());
        }

        // 分頁按鈕
        const prevPageBtn = document.getElementById('prevPage');
        const nextPageBtn = document.getElementById('nextPage');
        
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => this.previousPage());
        }
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => this.nextPage());
        }

        // 每頁顯示數量
        const pageSizeSelect = document.getElementById('pageSize');
        if (pageSizeSelect) {
            pageSizeSelect.addEventListener('change', (e) => {
                this.pageSize = parseInt(e.target.value);
                this.currentPage = 1;
                this.loadLearningRecords();
            });
        }

        // 登出按鈕
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                if (typeof authManager !== 'undefined') {
                    authManager.logout();
                }
            });
        }
    }

    async loadLearningRecords() {
        try {
            this.showLoading();

            const params = {
                page: this.currentPage,
                page_size: this.pageSize,
                ...this.getFilterParams()
            };

            const result = await learningAPI.getLearningRecords(params);

            if (result.success && result.data) {
                this.records = result.data.records || [];
                this.totalRecords = result.data.total || 0;
                this.displayRecords();
                this.updatePagination();
            } else {
                throw new Error(result.error || '載入學習記錄失敗');
            }
        } catch (error) {
            console.error('載入學習記錄失敗:', error);
            this.showError('載入學習記錄失敗，請稍後再試');
            this.displayEmptyRecords();
        } finally {
            this.hideLoading();
        }
    }

    async loadStatistics() {
        try {
            const result = await learningAPI.getLearningStatistics(this.getFilterParams());

            if (result.success && result.data) {
                this.displayStatistics(result.data);
            }
        } catch (error) {
            console.error('載入統計資料失敗:', error);
            // 顯示默認統計
            this.displayStatistics({
                total_sessions: 0,
                total_questions: 0,
                average_accuracy: 0,
                total_time_hours: 0
            });
        }
    }

    getFilterParams() {
        const subjectFilter = document.getElementById('subjectFilter')?.value || '';
        const editionFilter = document.getElementById('editionFilter')?.value || '';
        const dateFilter = document.getElementById('dateFilter')?.value || '30';

        const params = {};
        
        if (subjectFilter) params.subject = subjectFilter;
        if (editionFilter) params.edition = editionFilter;
        if (dateFilter && dateFilter !== 'all') {
            const days = parseInt(dateFilter);
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(endDate.getDate() - days);
            
            params.start_date = startDate.toISOString().split('T')[0];
            params.end_date = endDate.toISOString().split('T')[0];
        }

        return params;
    }

    applyFilters() {
        this.currentPage = 1;
        this.loadLearningRecords();
        this.loadStatistics();
    }

    displayStatistics(stats) {
        const totalSessionsEl = document.getElementById('totalSessions');
        const totalQuestionsEl = document.getElementById('totalQuestions');
        const avgAccuracyEl = document.getElementById('avgAccuracy');
        const totalTimeEl = document.getElementById('totalTime');

        if (totalSessionsEl) {
            totalSessionsEl.textContent = stats.total_sessions || 0;
        }
        if (totalQuestionsEl) {
            totalQuestionsEl.textContent = stats.total_questions || 0;
        }
        if (avgAccuracyEl) {
            const accuracy = stats.average_accuracy || 0;
            avgAccuracyEl.textContent = `${Math.round(accuracy)}%`;
        }
        if (totalTimeEl) {
            const hours = stats.total_time_hours || 0;
            totalTimeEl.textContent = `${Math.round(hours)}h`;
        }
    }

    displayRecords() {
        const sessionsList = document.getElementById('sessionsList');
        if (!sessionsList) return;

        if (this.records.length === 0) {
            this.displayEmptyRecords();
            return;
        }

        sessionsList.innerHTML = this.records.map(record => {
            const createdAt = new Date(record.created_at);
            const completedAt = record.completed_at ? new Date(record.completed_at) : null;
            
            // 計算用時
            let duration = '未完成';
            if (completedAt) {
                const durationMs = completedAt.getTime() - createdAt.getTime();
                const minutes = Math.round(durationMs / 1000 / 60);
                duration = `${minutes} 分鐘`;
            }

            // 計算正確率
            let accuracy = '未完成';
            let scoreDisplay = '未完成';
            if (record.total_questions > 0 && record.correct_count !== undefined) {
                const accuracyPercent = Math.round((record.correct_count / record.total_questions) * 100);
                accuracy = `${accuracyPercent}%`;
                scoreDisplay = `${record.correct_count}/${record.total_questions}`;
            }

            return `
                <div class="px-6 py-4 hover:bg-gray-50 cursor-pointer" onclick="historyManager.viewRecordDetails('${record.id}')">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <div class="flex items-center space-x-4">
                                <div class="flex-shrink-0">
                                    <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <span class="material-icons text-blue-600">quiz</span>
                                    </div>
                                </div>
                                <div class="flex-1">
                                    <div class="flex items-center space-x-2">
                                        <h4 class="text-sm font-medium text-gray-900">
                                            ${record.subject || '未分類'} - ${record.session_type === 'exercise' ? '練習測驗' : '學習會話'}
                                        </h4>
                                        ${record.difficulty ? `<span class="px-2 py-1 text-xs rounded-full ${this.getDifficultyColor(record.difficulty)}">${this.getDifficultyDisplayName(record.difficulty)}</span>` : ''}
                                        ${record.grade ? `<span class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">${this.getGradeDisplayName(record.grade)}</span>` : ''}
                                    </div>
                                    <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                                        <span class="flex items-center">
                                            <span class="material-icons text-sm mr-1">schedule</span>
                                            ${this.formatDate(createdAt)}
                                        </span>
                                        <span class="flex items-center">
                                            <span class="material-icons text-sm mr-1">timer</span>
                                            ${duration}
                                        </span>
                                        <span class="flex items-center">
                                            <span class="material-icons text-sm mr-1">assignment</span>
                                            ${record.total_questions || 0} 題
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center space-x-6">
                            <div class="text-right">
                                <div class="text-sm font-medium text-gray-900">${scoreDisplay}</div>
                                <div class="text-sm text-gray-500">正確率</div>
                            </div>
                            <div class="text-right">
                                <div class="text-lg font-bold ${this.getAccuracyColor(accuracy)}">${accuracy}</div>
                                <div class="text-sm text-gray-500">得分</div>
                            </div>
                            <div class="flex-shrink-0">
                                <span class="material-icons text-gray-400">chevron_right</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    displayEmptyRecords() {
        const sessionsList = document.getElementById('sessionsList');
        if (sessionsList) {
            sessionsList.innerHTML = `
                <div class="flex flex-col items-center justify-center py-12 text-gray-500">
                    <span class="material-icons text-4xl mb-2">history_edu</span>
                    <p class="text-lg font-medium">暫無練習記錄</p>
                    <p class="text-sm mt-1">開始您的第一次練習吧！</p>
                    <a href="exercise.html" class="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        開始練習
                    </a>
                </div>
            `;
        }
    }

    viewRecordDetails(recordId) {
        // 這裡可以實現查看詳細記錄的功能
        // 暫時使用alert來顯示
        const record = this.records.find(r => r.id === recordId);
        if (record) {
            alert(`練習記錄詳情：\n科目：${record.subject}\n題數：${record.total_questions}\n正確：${record.correct_count}\n時間：${this.formatDate(new Date(record.created_at))}`);
        }
    }

    updatePagination() {
        const totalPages = Math.ceil(this.totalRecords / this.pageSize);
        
        const prevPageBtn = document.getElementById('prevPage');
        const nextPageBtn = document.getElementById('nextPage');
        const pageInfoEl = document.getElementById('pageInfo');

        if (prevPageBtn) {
            prevPageBtn.disabled = this.currentPage <= 1;
        }
        if (nextPageBtn) {
            nextPageBtn.disabled = this.currentPage >= totalPages;
        }
        if (pageInfoEl) {
            pageInfoEl.textContent = `第 ${this.currentPage} 頁，共 ${Math.max(1, totalPages)} 頁`;
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.loadLearningRecords();
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.totalRecords / this.pageSize);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.loadLearningRecords();
        }
    }

    getDifficultyDisplayName(difficulty) {
        const difficultyMap = {
            'easy': '簡單',
            'normal': '中等',
            'hard': '困難'
        };
        return difficultyMap[difficulty] || difficulty;
    }

    getGradeDisplayName(grade) {
        const gradeMap = {
            '7A': '國一',
            '7B': '國二',
            '7C': '國三'
        };
        return gradeMap[grade] || grade;
    }

    getDifficultyColor(difficulty) {
        const colorMap = {
            'easy': 'bg-green-100 text-green-600',
            'normal': 'bg-yellow-100 text-yellow-600',
            'hard': 'bg-red-100 text-red-600'
        };
        return colorMap[difficulty] || 'bg-gray-100 text-gray-600';
    }

    getAccuracyColor(accuracy) {
        if (accuracy === '未完成') return 'text-gray-500';
        
        const percent = parseInt(accuracy);
        if (percent >= 80) return 'text-green-600';
        if (percent >= 60) return 'text-yellow-600';
        return 'text-red-600';
    }

    formatDate(date) {
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
            return `今天 ${date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}`;
        } else if (diffDays === 1) {
            return `昨天 ${date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}`;
        } else if (diffDays < 7) {
            return `${diffDays} 天前`;
        } else {
            return date.toLocaleDateString('zh-TW', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }

    showLoading() {
        const sessionsList = document.getElementById('sessionsList');
        if (sessionsList) {
            sessionsList.innerHTML = `
                <div class="flex items-center justify-center py-12 text-gray-500">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    載入練習記錄中...
                </div>
            `;
        }
    }

    hideLoading() {
        // Loading會被displayRecords或displayEmptyRecords替換
    }

    showError(message) {
        console.error(message);
        // 可以在這裡添加錯誤提示的UI
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
    // 確保authManager已初始化
    if (typeof authManager !== 'undefined') {
        authManager.init();
    }
    
    window.historyManager = new HistoryManager();
});