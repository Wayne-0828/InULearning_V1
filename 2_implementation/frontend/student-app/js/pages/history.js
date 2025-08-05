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
                this.records = result.data.sessions || [];
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
            const result = await learningAPI.getLearningStatistics();

            if (result.success && result.data) {
                this.displayStatistics(result.data);
            }
        } catch (error) {
            console.error('載入統計資料失敗:', error);
            // 顯示默認統計
            this.displayStatistics({
                total_sessions: 0,
                total_questions: 0,
                overall_accuracy: 0,
                total_time_spent: 0
            });
        }
    }

    getFilterParams() {
        const subjectFilter = document.getElementById('subjectFilter')?.value || '';
        const gradeFilter = document.getElementById('gradeFilter')?.value || '';
        const editionFilter = document.getElementById('editionFilter')?.value || '';
        const dateFilter = document.getElementById('dateFilter')?.value || '30';

        const params = {};

        if (subjectFilter) params.subject = subjectFilter;
        if (gradeFilter) params.grade = gradeFilter;
        if (editionFilter) params.publisher = editionFilter; // 更新為 publisher
        if (dateFilter && dateFilter !== 'all') {
            const days = parseInt(dateFilter);
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(endDate.getDate() - days);

            params.start_date = startDate.toISOString();
            params.end_date = endDate.toISOString();
        }

        return params;
    }

    quickFilter(filterType, value) {
        if (filterType === 'subject') {
            const subjectFilter = document.getElementById('subjectFilter');
            if (subjectFilter) subjectFilter.value = value;
        } else if (filterType === 'dateRange') {
            const dateFilter = document.getElementById('dateFilter');
            if (dateFilter) dateFilter.value = value;
        }
        this.applyFilters();
    }

    clearFilters() {
        const subjectFilter = document.getElementById('subjectFilter');
        const gradeFilter = document.getElementById('gradeFilter');
        const editionFilter = document.getElementById('editionFilter');
        const dateFilter = document.getElementById('dateFilter');

        if (subjectFilter) subjectFilter.value = '';
        if (gradeFilter) gradeFilter.value = '';
        if (editionFilter) editionFilter.value = '';
        if (dateFilter) dateFilter.value = '30';

        this.applyFilters();
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
            const accuracy = stats.overall_accuracy || 0;
            avgAccuracyEl.textContent = `${Math.round(accuracy)}%`;
        }
        if (totalTimeEl) {
            const timeSpent = stats.total_time_spent || 0;
            const hours = Math.round(timeSpent / 3600 * 10) / 10; // 秒轉小時，保留一位小數
            totalTimeEl.textContent = `${hours}h`;
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
            const startTime = new Date(record.start_time);

            // 計算用時
            let duration = '未記錄';
            if (record.time_spent) {
                const minutes = Math.floor(record.time_spent / 60);
                const seconds = record.time_spent % 60;
                duration = `${minutes}分${seconds}秒`;
            }

            // 計算正確率和分數
            let accuracy = '未完成';
            let scoreDisplay = '未完成';
            if (record.question_count > 0) {
                const correctCount = record.correct_count || 0;
                const accuracyPercent = Math.round(record.accuracy_rate || 0);
                accuracy = `${accuracyPercent}%`;
                scoreDisplay = `${correctCount}/${record.question_count}`;
            }

            // 構建標籤
            const tags = [];
            if (record.grade) {
                tags.push(`<span class="px-2 py-1 text-xs bg-blue-100 text-blue-600 rounded-full">${this.getGradeDisplayName(record.grade)}</span>`);
            }
            if (record.publisher) {
                tags.push(`<span class="px-2 py-1 text-xs bg-green-100 text-green-600 rounded-full">${record.publisher}</span>`);
            }
            if (record.chapter) {
                tags.push(`<span class="px-2 py-1 text-xs bg-purple-100 text-purple-600 rounded-full">${this.truncateText(record.chapter, 10)}</span>`);
            }
            if (record.difficulty) {
                const difficultyText = this.getDifficultyText(record.difficulty);
                const difficultyColor = this.getDifficultyColor(record.difficulty);
                tags.push(`<span class="px-2 py-1 text-xs ${difficultyColor} rounded-full">${difficultyText}</span>`);
            }

            // 知識點標籤
            const knowledgePointsDisplay = (record.knowledge_points || []).slice(0, 2).map(kp =>
                `<span class="px-2 py-1 text-xs bg-yellow-100 text-yellow-600 rounded-full">${this.truncateText(kp, 8)}</span>`
            ).join('');
            if (record.knowledge_points && record.knowledge_points.length > 2) {
                tags.push(`<span class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">+${record.knowledge_points.length - 2}</span>`);
            }

            return `
                <div class="px-6 py-4 hover:bg-gray-50 cursor-pointer" onclick="historyManager.viewRecordDetails('${record.session_id}')">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <div class="flex items-center space-x-4">
                                <div class="flex-shrink-0">
                                    <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <span class="material-icons text-blue-600">quiz</span>
                                    </div>
                                </div>
                                <div class="flex-1">
                                    <div class="flex items-center space-x-2 mb-1">
                                        <h4 class="text-sm font-medium text-gray-900">
                                            ${record.session_name || `${record.subject || '未分類'} 練習測驗`}
                                        </h4>
                                        ${tags.join('')}
                                    </div>
                                    <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                                        <span class="flex items-center">
                                            <span class="material-icons text-sm mr-1">schedule</span>
                                            ${this.formatDate(startTime)}
                                        </span>
                                        <span class="flex items-center">
                                            <span class="material-icons text-sm mr-1">timer</span>
                                            ${duration}
                                        </span>
                                        <span class="flex items-center">
                                            <span class="material-icons text-sm mr-1">assignment</span>
                                            ${record.question_count || 0} 題
                                        </span>
                                    </div>
                                    ${knowledgePointsDisplay ? `<div class="mt-2 flex items-center space-x-1">${knowledgePointsDisplay}</div>` : ''}
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center space-x-6">
                            <div class="text-right">
                                <div class="text-sm font-medium text-gray-900">${scoreDisplay}</div>
                                <div class="text-sm text-gray-500">正確題數</div>
                            </div>
                            <div class="text-right">
                                <div class="text-lg font-bold ${this.getAccuracyColor(accuracy)}">${accuracy}</div>
                                <div class="text-sm text-gray-500">正確率</div>
                            </div>
                            <div class="text-right">
                                <div class="text-sm font-medium text-gray-900">${Math.round(record.total_score || 0)}</div>
                                <div class="text-sm text-gray-500">總分</div>
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
                    <span class="material-icons text-6xl mb-4">history_edu</span>
                    <h3 class="text-lg font-medium mb-2">尚無練習記錄</h3>
                    <p class="text-sm">開始您的第一次練習吧！</p>
                    <a href="exercise.html" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        開始練習
                    </a>
                </div>
            `;
        }
    }

    getGradeDisplayName(grade) {
        const gradeMap = {
            '7A': '七上',
            '7B': '七下',
            '8A': '八上',
            '8B': '八下',
            '9A': '九上',
            '9B': '九下'
        };
        return gradeMap[grade] || grade;
    }

    getDifficultyText(difficulty) {
        const difficultyMap = {
            'easy': '簡單',
            'normal': '普通',
            'hard': '困難'
        };
        return difficultyMap[difficulty] || difficulty;
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

    truncateText(text, maxLength) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    formatDate(date) {
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 1) {
            return '今天';
        } else if (diffDays === 2) {
            return '昨天';
        } else if (diffDays <= 7) {
            return `${diffDays - 1} 天前`;
        } else {
            return date.toLocaleDateString('zh-TW');
        }
    }

    async viewRecordDetails(sessionId) {
        try {
            // 顯示載入中
            const loadingToast = this.showToast('載入詳細資料中...', 'info');

            // 獲取會話詳細資料
            const result = await learningAPI.getSessionDetail(sessionId);

            if (!result.success || !result.data) {
                throw new Error(result.error || '獲取詳細資料失敗');
            }

            const sessionDetail = result.data;
            const session = sessionDetail.session;
            const exerciseRecords = sessionDetail.exercise_records || [];

            // 將記錄資料存儲到 sessionStorage 並跳轉到結果頁面
            const resultData = {
                score: Math.round(session.total_score || 0),
                accuracy: Math.round(session.accuracy_rate || 0),
                totalQuestions: session.question_count || 0,
                correctAnswers: session.correct_count || 0,
                wrongAnswers: (session.question_count || 0) - (session.correct_count || 0),
                timeSpent: session.time_spent || 0,
                submittedAt: session.end_time || session.start_time,
                sessionData: {
                    sessionId: session.session_id,
                    sessionName: session.session_name,
                    grade: session.grade,
                    publisher: session.publisher,
                    subject: session.subject,
                    chapter: session.chapter,
                    difficulty: session.difficulty,
                    knowledgePoints: session.knowledge_points || []
                },
                detailedResults: exerciseRecords.map(record => ({
                    questionId: record.question_id,
                    questionContent: record.question_content,
                    answerChoices: record.answer_choices,
                    userAnswer: record.user_answer,
                    correctAnswer: record.correct_answer,
                    isCorrect: record.is_correct,
                    score: record.score,
                    explanation: record.explanation,
                    timeSpent: record.time_spent,
                    knowledgePoints: record.knowledge_points || [],
                    difficulty: record.difficulty,
                    questionTopic: record.question_topic
                })),
                questions: exerciseRecords.map(record => ({
                    id: record.question_id,
                    content: record.question_content,
                    choices: record.answer_choices,
                    correctAnswer: record.correct_answer,
                    explanation: record.explanation,
                    knowledgePoints: record.knowledge_points || [],
                    difficulty: record.difficulty,
                    topic: record.question_topic
                })),
                userAnswers: exerciseRecords.map(record => ({
                    questionId: record.question_id,
                    answer: record.user_answer,
                    isCorrect: record.is_correct,
                    timeSpent: record.time_spent
                }))
            };

            // 隱藏載入提示
            this.hideToast(loadingToast);

            sessionStorage.setItem('examResults', JSON.stringify(resultData));
            window.location.href = 'result.html';

        } catch (error) {
            console.error('查看記錄詳情失敗:', error);
            this.showToast('載入詳細資料失敗，請稍後再試', 'error');
        }
    }

    updatePagination() {
        const totalPages = Math.ceil(this.totalRecords / this.pageSize);

        // 更新分頁資訊
        const pageInfo = document.getElementById('pageInfo');
        if (pageInfo) {
            pageInfo.textContent = `第 ${this.currentPage} 頁，共 ${totalPages} 頁`;
        }

        // 更新按鈕狀態
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');

        if (prevBtn) {
            prevBtn.disabled = this.currentPage <= 1;
            prevBtn.classList.toggle('opacity-50', this.currentPage <= 1);
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= totalPages;
            nextBtn.classList.toggle('opacity-50', this.currentPage >= totalPages);
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

    showLoading() {
        const sessionsList = document.getElementById('sessionsList');
        if (sessionsList) {
            sessionsList.innerHTML = `
                <div class="flex items-center justify-center py-12 text-gray-500">
                    <span class="material-icons animate-spin mr-2">refresh</span>
                    載入中...
                </div>
            `;
        }
    }

    hideLoading() {
        // Loading 狀態由 displayRecords 或 displayEmptyRecords 覆蓋
    }

    showError(message) {
        console.error(message);
        const sessionsList = document.getElementById('sessionsList');
        if (sessionsList) {
            sessionsList.innerHTML = `
                <div class="flex flex-col items-center justify-center py-12 text-red-500">
                    <span class="material-icons text-6xl mb-4">error</span>
                    <p>${message}</p>
                    <button onclick="historyManager.loadLearningRecords()" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        重新載入
                    </button>
                </div>
            `;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const colors = {
            'info': 'bg-blue-500',
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'warning': 'bg-yellow-500'
        };

        toast.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform transition-all duration-300 translate-x-full`;
        toast.textContent = message;

        document.body.appendChild(toast);

        // 動畫顯示
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // 自動隱藏（除了載入中的提示）
        if (type !== 'info') {
            setTimeout(() => {
                this.hideToast(toast);
            }, 3000);
        }

        return toast;
    }

    hideToast(toast) {
        if (toast && toast.parentNode) {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
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