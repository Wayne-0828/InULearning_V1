// 作業管理增強版 JavaScript
class AssignmentsManager {
    constructor() {
        this.assignments = [];
        this.filteredAssignments = [];
        this.currentView = 'list';
        this.currentMonth = new Date();

        this.init();
    }

    async init() {
        await this.loadAssignments();
        this.setupEventListeners();
        this.renderAssignments();
        this.updateStats();
        this.renderCalendar();
    }

    async loadAssignments() {
        try {
            // 嘗試從 API 載入真實資料
            const response = await fetch('/api/assignments');
            if (response.ok) {
                this.assignments = await response.json();
                console.log('✅ 成功載入真實作業資料');
            } else {
                throw new Error('API 回應錯誤');
            }
        } catch (error) {
            console.log('⚠️ API 載入失敗，使用模擬資料:', error.message);
            this.assignments = this.getMockAssignments();
        }

        this.filteredAssignments = [...this.assignments];
    }

    getMockAssignments() {
        return [
            {
                id: 1,
                title: '第三章 二次函數練習',
                subject: 'math',
                description: '完成課本第三章所有練習題，包含圖形繪製',
                status: 'active',
                dueDate: '2024-02-28',
                createdDate: '2024-02-15',
                totalStudents: 32,
                submitted: 28,
                graded: 15,
                avgScore: 85.5,
                difficulty: 'medium'
            },
            {
                id: 2,
                title: '作文：我的寒假生活',
                subject: 'chinese',
                description: '以「我的寒假生活」為題，寫一篇不少於600字的作文',
                status: 'grading',
                dueDate: '2024-02-25',
                createdDate: '2024-02-10',
                totalStudents: 32,
                submitted: 32,
                graded: 8,
                avgScore: 78.2,
                difficulty: 'easy'
            },
            {
                id: 3,
                title: 'Unit 5 Grammar Exercise',
                subject: 'english',
                description: '完成第五單元文法練習，包含現在完成式的應用',
                status: 'active',
                dueDate: '2024-03-05',
                createdDate: '2024-02-20',
                totalStudents: 32,
                submitted: 12,
                graded: 0,
                avgScore: 0,
                difficulty: 'hard'
            },
            {
                id: 4,
                title: '光合作用實驗報告',
                subject: 'science',
                description: '根據課堂實驗，撰寫光合作用實驗報告',
                status: 'closed',
                dueDate: '2024-02-20',
                createdDate: '2024-02-05',
                totalStudents: 32,
                submitted: 30,
                graded: 30,
                avgScore: 88.7,
                difficulty: 'medium'
            },
            {
                id: 5,
                title: '歷史人物報告',
                subject: 'history',
                description: '選擇一位歷史人物，製作簡報並進行口頭報告',
                status: 'draft',
                dueDate: '2024-03-10',
                createdDate: '2024-02-22',
                totalStudents: 32,
                submitted: 0,
                graded: 0,
                avgScore: 0,
                difficulty: 'medium'
            },
            {
                id: 6,
                title: '幾何證明題組',
                subject: 'math',
                description: '完成三角形全等性質相關證明題',
                status: 'active',
                dueDate: '2024-02-26',
                createdDate: '2024-02-18',
                totalStudents: 32,
                submitted: 20,
                graded: 5,
                avgScore: 72.3,
                difficulty: 'hard'
            }
        ];
    }

    setupEventListeners() {
        // 搜尋功能
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.filterAssignments();
        });

        // 狀態篩選
        document.getElementById('statusFilter').addEventListener('change', (e) => {
            this.filterAssignments();
        });

        // 科目篩選
        document.getElementById('subjectFilter').addEventListener('change', (e) => {
            this.filterAssignments();
        });

        // 視圖切換
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchView(e.target.closest('.view-btn').dataset.view);
            });
        });
    }

    filterAssignments() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const statusFilter = document.getElementById('statusFilter').value;
        const subjectFilter = document.getElementById('subjectFilter').value;

        this.filteredAssignments = this.assignments.filter(assignment => {
            const matchesSearch = assignment.title.toLowerCase().includes(searchTerm) ||
                assignment.description.toLowerCase().includes(searchTerm);
            const matchesStatus = !statusFilter || assignment.status === statusFilter;
            const matchesSubject = !subjectFilter || assignment.subject === subjectFilter;

            return matchesSearch && matchesStatus && matchesSubject;
        });

        this.renderAssignments();
    }

    switchView(view) {
        this.currentView = view;

        // 更新按鈕狀態
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`).classList.add('active');

        // 切換視圖
        if (view === 'list') {
            document.getElementById('listView').classList.remove('hidden');
            document.getElementById('gridView').classList.add('hidden');
        } else {
            document.getElementById('listView').classList.add('hidden');
            document.getElementById('gridView').classList.remove('hidden');
        }

        this.renderAssignments();
    }

    renderAssignments() {
        if (this.currentView === 'list') {
            this.renderListView();
        } else {
            this.renderGridView();
        }
    }

    renderListView() {
        const container = document.getElementById('listView');

        if (this.filteredAssignments.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-light);">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                    <p>沒有找到符合條件的作業</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.filteredAssignments.map(assignment => `
            <div class="assignment-item">
                <div class="assignment-header">
                    <div>
                        <div class="assignment-title">${assignment.title}</div>
                        <div class="assignment-meta">
                            <span><i class="fas fa-book"></i> ${this.getSubjectName(assignment.subject)}</span>
                            <span><i class="fas fa-calendar"></i> 截止：${this.formatDate(assignment.dueDate)}</span>
                            <span><i class="fas fa-users"></i> ${assignment.totalStudents} 人</span>
                        </div>
                    </div>
                    <div class="assignment-status ${assignment.status}">
                        <i class="fas ${this.getStatusIcon(assignment.status)}"></i>
                        ${this.getStatusText(assignment.status)}
                    </div>
                </div>
                
                <p style="color: var(--text-light); margin-bottom: 1rem;">${assignment.description}</p>
                
                <div class="assignment-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(assignment.submitted / assignment.totalStudents) * 100}%"></div>
                    </div>
                    <div class="progress-text">
                        ${assignment.submitted}/${assignment.totalStudents} 已繳交
                        ${assignment.graded > 0 ? `(${assignment.graded} 已批改)` : ''}
                    </div>
                </div>
                
                <div class="assignment-actions" style="margin-top: 1rem;">
                    <button class="action-btn primary" onclick="viewAssignment(${assignment.id})">
                        <i class="fas fa-eye"></i> 查看
                    </button>
                    <button class="action-btn secondary" onclick="editAssignment(${assignment.id})">
                        <i class="fas fa-edit"></i> 編輯
                    </button>
                    <button class="action-btn secondary" onclick="gradeAssignment(${assignment.id})">
                        <i class="fas fa-check"></i> 批改
                    </button>
                    <button class="action-btn secondary" onclick="duplicateAssignment(${assignment.id})">
                        <i class="fas fa-copy"></i> 複製
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderGridView() {
        const container = document.getElementById('gridView');

        if (this.filteredAssignments.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-light);">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                    <p>沒有找到符合條件的作業</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.filteredAssignments.map(assignment => {
            const progressPercent = (assignment.submitted / assignment.totalStudents) * 100;
            const isOverdue = new Date(assignment.dueDate) < new Date() && assignment.status === 'active';
            const cardClass = isOverdue ? 'danger' : (assignment.status === 'grading' ? 'warning' : '');

            return `
                <div class="assignment-card ${cardClass}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                        <h3 style="margin: 0; font-size: 1.1rem;">${assignment.title}</h3>
                        <div class="assignment-status ${assignment.status}">
                            ${this.getStatusText(assignment.status)}
                        </div>
                    </div>
                    
                    <p style="color: var(--text-light); font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.4;">
                        ${assignment.description.length > 80 ? assignment.description.substring(0, 80) + '...' : assignment.description}
                    </p>
                    
                    <div style="margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="font-size: 0.9rem; color: var(--text-light);">繳交進度</span>
                            <span style="font-size: 0.9rem; font-weight: 600;">${assignment.submitted}/${assignment.totalStudents}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${progressPercent}%"></div>
                        </div>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-light);">
                        <span><i class="fas fa-book"></i> ${this.getSubjectName(assignment.subject)}</span>
                        <span><i class="fas fa-calendar"></i> ${this.formatDate(assignment.dueDate)}</span>
                    </div>
                    
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="action-btn primary" onclick="viewAssignment(${assignment.id})" style="flex: 1; font-size: 0.8rem;">
                            查看
                        </button>
                        <button class="action-btn secondary" onclick="gradeAssignment(${assignment.id})" style="flex: 1; font-size: 0.8rem;">
                            批改
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    updateStats() {
        const stats = {
            total: this.assignments.length,
            active: this.assignments.filter(a => a.status === 'active').length,
            completed: this.assignments.filter(a => a.status === 'closed').length,
            overdue: this.assignments.filter(a =>
                a.status === 'active' && new Date(a.dueDate) < new Date()
            ).length
        };

        document.getElementById('totalAssignments').textContent = stats.total;
        document.getElementById('activeAssignments').textContent = stats.active;
        document.getElementById('completedAssignments').textContent = stats.completed;
        document.getElementById('overdueAssignments').textContent = stats.overdue;
    }

    renderCalendar() {
        const grid = document.getElementById('calendarGrid');
        const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];

        document.getElementById('currentMonth').textContent =
            `${this.currentMonth.getFullYear()}年${monthNames[this.currentMonth.getMonth()]}`;

        const firstDay = new Date(this.currentMonth.getFullYear(), this.currentMonth.getMonth(), 1);
        const lastDay = new Date(this.currentMonth.getFullYear(), this.currentMonth.getMonth() + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());

        const days = ['日', '一', '二', '三', '四', '五', '六'];
        let html = days.map(day => `<div style="font-weight: 600; text-align: center; padding: 0.5rem;">${day}</div>`).join('');

        const deadlines = this.assignments.reduce((acc, assignment) => {
            const date = assignment.dueDate;
            if (!acc[date]) acc[date] = [];
            acc[date].push(assignment);
            return acc;
        }, {});

        for (let i = 0; i < 42; i++) {
            const currentDate = new Date(startDate);
            currentDate.setDate(startDate.getDate() + i);

            const dateStr = currentDate.toISOString().split('T')[0];
            const isCurrentMonth = currentDate.getMonth() === this.currentMonth.getMonth();
            const isToday = dateStr === new Date().toISOString().split('T')[0];
            const hasDeadline = deadlines[dateStr];

            let classes = ['calendar-day'];
            if (isToday) classes.push('today');
            if (hasDeadline) classes.push('has-deadline');
            if (!isCurrentMonth) classes.push('other-month');

            html += `<div class="${classes.join(' ')}" title="${hasDeadline ? hasDeadline.map(a => a.title).join(', ') : ''}">${currentDate.getDate()}</div>`;
        }

        grid.innerHTML = html;
    }

    getSubjectName(subject) {
        const subjects = {
            math: '數學',
            chinese: '國文',
            english: '英文',
            science: '自然',
            history: '歷史',
            geography: '地理'
        };
        return subjects[subject] || subject;
    }

    getStatusText(status) {
        const statuses = {
            active: '進行中',
            draft: '草稿',
            closed: '已結束',
            grading: '批改中'
        };
        return statuses[status] || status;
    }

    getStatusIcon(status) {
        const icons = {
            active: 'fa-play-circle',
            draft: 'fa-edit',
            closed: 'fa-check-circle',
            grading: 'fa-clock'
        };
        return icons[status] || 'fa-question-circle';
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        return `${date.getMonth() + 1}/${date.getDate()}`;
    }
}

// 全域函數
function createAssignment() {
    alert('新增作業功能開發中...');
}

function viewAssignment(id) {
    alert(`查看作業 ID: ${id}`);
}

function editAssignment(id) {
    alert(`編輯作業 ID: ${id}`);
}

function gradeAssignment(id) {
    alert(`批改作業 ID: ${id}`);
}

function duplicateAssignment(id) {
    alert(`複製作業 ID: ${id}`);
}

function exportAssignments() {
    alert('匯出報告功能開發中...');
}

function importAssignments() {
    alert('匯入作業功能開發中...');
}

function bulkGrade() {
    alert('批量批改功能開發中...');
}

function sendReminders() {
    alert('發送提醒功能開發中...');
}

function viewAnalytics() {
    window.location.href = 'analytics.html';
}

function previousMonth() {
    assignmentsManager.currentMonth.setMonth(assignmentsManager.currentMonth.getMonth() - 1);
    assignmentsManager.renderCalendar();
}

function nextMonth() {
    assignmentsManager.currentMonth.setMonth(assignmentsManager.currentMonth.getMonth() + 1);
    assignmentsManager.renderCalendar();
}

// 初始化
let assignmentsManager;
document.addEventListener('DOMContentLoaded', () => {
    assignmentsManager = new AssignmentsManager();
});