/**
 * 家長應用程式 - 子女管理模組
 * 負責子女列表管理、詳細資訊顯示、學習進度監控
 */

class ChildrenManager {
    constructor() {
        this.children = [];
        this.currentChild = null;
        this.init();
    }

    async init() {
        await this.loadChildren();
        this.bindEvents();
        this.renderChildrenList();
    }

    async loadChildren() {
        try {
            const response = await fetch('/api/v1/parent/children', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                this.children = await response.json();
                console.log('子女資料載入成功:', this.children);
            } else {
                throw new Error('載入子女資料失敗');
            }
        } catch (error) {
            console.error('載入子女資料錯誤:', error);
            this.showError('載入子女資料失敗，請稍後再試');
        }
    }

    bindEvents() {
        // 子女列表點擊事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('.child-card')) {
                const childId = e.target.closest('.child-card').dataset.childId;
                this.selectChild(childId);
            }

            if (e.target.closest('.view-details-btn')) {
                const childId = e.target.closest('.view-details-btn').dataset.childId;
                this.showChildDetails(childId);
            }

            if (e.target.closest('.view-progress-btn')) {
                const childId = e.target.closest('.view-progress-btn').dataset.childId;
                this.showChildProgress(childId);
            }
        });

        // 搜尋功能
        const searchInput = document.getElementById('children-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterChildren(e.target.value);
            });
        }
    }

    renderChildrenList() {
        const container = document.getElementById('children-list');
        if (!container) return;

        if (this.children.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-child fa-3x text-muted mb-3"></i>
                    <h5>尚未添加子女</h5>
                    <p class="text-muted">請聯繫管理員添加子女資訊</p>
                </div>
            `;
            return;
        }

        const childrenHTML = this.children.map(child => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card child-card h-100" data-child-id="${child.id}">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="avatar avatar-lg me-3">
                                <img src="${child.avatar || '/assets/images/default-avatar.png'}" 
                                     alt="${child.name}" class="rounded-circle">
                            </div>
                            <div>
                                <h6 class="card-title mb-1">${child.name}</h6>
                                <small class="text-muted">${child.grade}年級</small>
                            </div>
                        </div>
                        
                        <div class="row text-center mb-3">
                            <div class="col-4">
                                <div class="stat-item">
                                    <h6 class="mb-1">${child.total_exercises || 0}</h6>
                                    <small class="text-muted">練習題數</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="stat-item">
                                    <h6 class="mb-1">${child.accuracy_rate || 0}%</h6>
                                    <small class="text-muted">正確率</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="stat-item">
                                    <h6 class="mb-1">${child.study_days || 0}</h6>
                                    <small class="text-muted">學習天數</small>
                                </div>
                            </div>
                        </div>

                        <div class="progress mb-3" style="height: 6px;">
                            <div class="progress-bar bg-primary" 
                                 style="width: ${child.overall_progress || 0}%"></div>
                        </div>
                        <small class="text-muted">整體進度: ${child.overall_progress || 0}%</small>

                        <div class="d-flex gap-2 mt-3">
                            <button class="btn btn-outline-primary btn-sm flex-fill view-details-btn" 
                                    data-child-id="${child.id}">
                                <i class="fas fa-info-circle me-1"></i>詳細資訊
                            </button>
                            <button class="btn btn-primary btn-sm flex-fill view-progress-btn" 
                                    data-child-id="${child.id}">
                                <i class="fas fa-chart-line me-1"></i>學習進度
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = childrenHTML;
    }

    async selectChild(childId) {
        this.currentChild = this.children.find(child => child.id === parseInt(childId));
        if (this.currentChild) {
            // 更新當前選中的子女
            document.querySelectorAll('.child-card').forEach(card => {
                card.classList.remove('selected');
            });
            document.querySelector(`[data-child-id="${childId}"]`).classList.add('selected');
            
            // 更新儀表板顯示
            this.updateDashboard();
        }
    }

    async showChildDetails(childId) {
        try {
            const response = await fetch(`/api/v1/parent/children/${childId}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const childDetails = await response.json();
                this.renderChildDetails(childDetails);
            } else {
                throw new Error('載入子女詳細資訊失敗');
            }
        } catch (error) {
            console.error('載入子女詳細資訊錯誤:', error);
            this.showError('載入子女詳細資訊失敗');
        }
    }

    renderChildDetails(child) {
        const modal = document.getElementById('childDetailsModal');
        if (!modal) return;

        modal.querySelector('.modal-title').textContent = `${child.name} 的詳細資訊`;
        modal.querySelector('.modal-body').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>基本資訊</h6>
                    <ul class="list-unstyled">
                        <li><strong>姓名:</strong> ${child.name}</li>
                        <li><strong>年級:</strong> ${child.grade}年級</li>
                        <li><strong>班級:</strong> ${child.class_name || '未分配'}</li>
                        <li><strong>學號:</strong> ${child.student_id || '未設定'}</li>
                        <li><strong>註冊日期:</strong> ${new Date(child.created_at).toLocaleDateString()}</li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>學習統計</h6>
                    <ul class="list-unstyled">
                        <li><strong>總練習題數:</strong> ${child.total_exercises || 0}</li>
                        <li><strong>平均正確率:</strong> ${child.accuracy_rate || 0}%</li>
                        <li><strong>學習天數:</strong> ${child.study_days || 0}天</li>
                        <li><strong>總學習時數:</strong> ${child.total_study_hours || 0}小時</li>
                        <li><strong>連續學習:</strong> ${child.streak_days || 0}天</li>
                    </ul>
                </div>
            </div>
            
            <div class="mt-4">
                <h6>最近學習活動</h6>
                <div class="timeline">
                    ${this.renderRecentActivities(child.recent_activities || [])}
                </div>
            </div>
        `;

        // 顯示模態框
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }

    renderRecentActivities(activities) {
        if (activities.length === 0) {
            return '<p class="text-muted">尚無學習活動記錄</p>';
        }

        return activities.map(activity => `
            <div class="timeline-item">
                <div class="timeline-marker"></div>
                <div class="timeline-content">
                    <h6 class="mb-1">${activity.title}</h6>
                    <p class="mb-1">${activity.description}</p>
                    <small class="text-muted">${new Date(activity.created_at).toLocaleString()}</small>
                </div>
            </div>
        `).join('');
    }

    async showChildProgress(childId) {
        try {
            const response = await fetch(`/api/v1/parent/children/${childId}/progress`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const progressData = await response.json();
                this.renderChildProgress(progressData);
            } else {
                throw new Error('載入學習進度失敗');
            }
        } catch (error) {
            console.error('載入學習進度錯誤:', error);
            this.showError('載入學習進度失敗');
        }
    }

    renderChildProgress(progressData) {
        const modal = document.getElementById('childProgressModal');
        if (!modal) return;

        modal.querySelector('.modal-title').textContent = `${progressData.child_name} 的學習進度`;
        modal.querySelector('.modal-body').innerHTML = `
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="progress-card text-center">
                        <h4 class="text-primary">${progressData.overall_progress || 0}%</h4>
                        <small class="text-muted">整體進度</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="progress-card text-center">
                        <h4 class="text-success">${progressData.accuracy_rate || 0}%</h4>
                        <small class="text-muted">正確率</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="progress-card text-center">
                        <h4 class="text-info">${progressData.study_days || 0}</h4>
                        <small class="text-muted">學習天數</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="progress-card text-center">
                        <h4 class="text-warning">${progressData.streak_days || 0}</h4>
                        <small class="text-muted">連續學習</small>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <h6>科目進度</h6>
                    ${this.renderSubjectProgress(progressData.subjects || [])}
                </div>
                <div class="col-md-6">
                    <h6>學習趨勢</h6>
                    <canvas id="progressChart" width="400" height="200"></canvas>
                </div>
            </div>

            <div class="mt-4">
                <h6>學習弱點分析</h6>
                ${this.renderWeaknessAnalysis(progressData.weaknesses || [])}
            </div>
        `;

        // 顯示模態框
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();

        // 渲染圖表
        this.renderProgressChart(progressData.trend_data || []);
    }

    renderSubjectProgress(subjects) {
        if (subjects.length === 0) {
            return '<p class="text-muted">尚無科目進度資料</p>';
        }

        return subjects.map(subject => `
            <div class="subject-progress mb-3">
                <div class="d-flex justify-content-between mb-1">
                    <span>${subject.name}</span>
                    <span>${subject.progress}%</span>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar" style="width: ${subject.progress}%"></div>
                </div>
            </div>
        `).join('');
    }

    renderWeaknessAnalysis(weaknesses) {
        if (weaknesses.length === 0) {
            return '<p class="text-muted">尚無弱點分析資料</p>';
        }

        return weaknesses.map(weakness => `
            <div class="weakness-item mb-3 p-3 border rounded">
                <h6 class="text-danger">${weakness.topic}</h6>
                <p class="mb-2">${weakness.description}</p>
                <div class="d-flex justify-content-between">
                    <small class="text-muted">錯誤率: ${weakness.error_rate}%</small>
                    <small class="text-muted">建議練習題數: ${weakness.recommended_exercises}</small>
                </div>
            </div>
        `).join('');
    }

    renderProgressChart(trendData) {
        const canvas = document.getElementById('progressChart');
        if (!canvas || trendData.length === 0) return;

        const ctx = canvas.getContext('2d');
        const labels = trendData.map(item => item.date);
        const data = trendData.map(item => item.progress);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '學習進度',
                    data: data,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    filterChildren(searchTerm) {
        const filteredChildren = this.children.filter(child => 
            child.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            child.grade.toString().includes(searchTerm)
        );
        
        this.renderFilteredChildren(filteredChildren);
    }

    renderFilteredChildren(filteredChildren) {
        const container = document.getElementById('children-list');
        if (!container) return;

        if (filteredChildren.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5>未找到符合的子女</h5>
                    <p class="text-muted">請嘗試其他搜尋條件</p>
                </div>
            `;
            return;
        }

        // 使用相同的渲染邏輯
        const childrenHTML = filteredChildren.map(child => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card child-card h-100" data-child-id="${child.id}">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="avatar avatar-lg me-3">
                                <img src="${child.avatar || '/assets/images/default-avatar.png'}" 
                                     alt="${child.name}" class="rounded-circle">
                            </div>
                            <div>
                                <h6 class="card-title mb-1">${child.name}</h6>
                                <small class="text-muted">${child.grade}年級</small>
                            </div>
                        </div>
                        
                        <div class="row text-center mb-3">
                            <div class="col-4">
                                <div class="stat-item">
                                    <h6 class="mb-1">${child.total_exercises || 0}</h6>
                                    <small class="text-muted">練習題數</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="stat-item">
                                    <h6 class="mb-1">${child.accuracy_rate || 0}%</h6>
                                    <small class="text-muted">正確率</small>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="stat-item">
                                    <h6 class="mb-1">${child.study_days || 0}</h6>
                                    <small class="text-muted">學習天數</small>
                                </div>
                            </div>
                        </div>

                        <div class="progress mb-3" style="height: 6px;">
                            <div class="progress-bar bg-primary" 
                                 style="width: ${child.overall_progress || 0}%"></div>
                        </div>
                        <small class="text-muted">整體進度: ${child.overall_progress || 0}%</small>

                        <div class="d-flex gap-2 mt-3">
                            <button class="btn btn-outline-primary btn-sm flex-fill view-details-btn" 
                                    data-child-id="${child.id}">
                                <i class="fas fa-info-circle me-1"></i>詳細資訊
                            </button>
                            <button class="btn btn-primary btn-sm flex-fill view-progress-btn" 
                                    data-child-id="${child.id}">
                                <i class="fas fa-chart-line me-1"></i>學習進度
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = childrenHTML;
    }

    updateDashboard() {
        if (!this.currentChild) return;

        // 更新儀表板顯示當前選中的子女資訊
        const dashboard = document.getElementById('current-child-info');
        if (dashboard) {
            dashboard.innerHTML = `
                <div class="current-child-card">
                    <div class="d-flex align-items-center">
                        <img src="${this.currentChild.avatar || '/assets/images/default-avatar.png'}" 
                             alt="${this.currentChild.name}" class="rounded-circle me-3" style="width: 50px; height: 50px;">
                        <div>
                            <h6 class="mb-1">${this.currentChild.name}</h6>
                            <small class="text-muted">${this.currentChild.grade}年級</small>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    showError(message) {
        // 顯示錯誤訊息
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-danger border-0';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        const toastContainer = document.getElementById('toast-container');
        if (toastContainer) {
            toastContainer.appendChild(toast);
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }
}

// 初始化子女管理模組
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('children-list')) {
        window.childrenManager = new ChildrenManager();
    }
}); 