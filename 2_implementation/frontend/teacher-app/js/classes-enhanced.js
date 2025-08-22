/**
 * 班級管理增強版模組
 * 整合 relationships.py API，處理班級的創建、編輯、刪除、學生管理等功能
 */
class ClassesManager {
    constructor() {
        this.classes = [];
        this.filteredClasses = [];
        this.currentView = 'list';
        this.editingId = null;
        this.selectedClassId = null;
        
        // API 路徑，對應 relationships.py (不需要 /api/v1 前綴，因為 apiClient.baseUrl 已經包含)
        this.apiPath = '/relationships/teacher-class';
        this.classesApiPath = '/relationships/classes';
        this.studentsApiPath = '/relationships/classes';
        
        // 學生管理相關
        this.students = [];
        this.filteredStudents = [];

        // 自動刷新設定
        this.autoRefreshInterval = null;
        this.autoRefreshEnabled = true;
        this.refreshIntervalMs = 30000; // 30秒自動刷新一次

        this.init();
    }

    async init() {
        try {
            // 延遲初始化以確保 DOM 完全載入
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.initApp());
            } else {
                // 如果 DOM 已經載入，延遲一點執行以確保所有元素都存在
                setTimeout(() => this.initApp(), 100);
            }
        } catch (error) {
            console.error('❌ 班級管理初始化失敗:', error);
        }
    }

    async initApp() {
        try {
            console.log('✅ 開始初始化班級管理...');
            
            // 檢查認證狀態，但不阻止初始化
            if (typeof teacherAuth !== 'undefined' && teacherAuth.isLoggedIn()) {
                console.log('✅ 用戶已登入，載入完整功能');
                await this.loadClasses();
                this.setupEventListeners();
                this.renderClasses();
                this.updateStats();
                this.startAutoRefresh();
            } else {
                console.log('⚠️ 用戶未登入，顯示基本 UI');
                this.setupEventListeners();
                this.renderEmptyState();
            }
            
            console.log('✅ 班級管理初始化完成');
        } catch (error) {
            console.error('❌ 班級管理初始化失敗:', error);
            // 即使出錯也要顯示基本 UI
            this.setupEventListeners();
            this.renderEmptyState();
        }
    }

    async loadClasses(forceRefresh = false) {
        try {
            console.log('🔄 開始載入班級資料...', forceRefresh ? '(強制刷新)' : '');
            
            // 如果需要強制刷新，清除緩存並設置 noCache 選項
            if (forceRefresh) {
                apiClient.clearCache();
            }
            
            // 使用 relationships.py 的 API，強制不使用緩存
            const data = await apiClient.get(`${this.apiPath}?include_deleted=true&t=${Date.now()}`, {
                noCache: forceRefresh
            });
            console.log('📡 API 回應資料:', data);
            
            this.classes = Array.isArray(data) ? data : [];
            console.log('✅ 成功載入班級資料:', this.classes.length, '個班級');
            console.log('📋 班級列表:', this.classes);
        } catch (error) {
            console.error('⚠️ 班級 API 載入失敗:', error.message);
            this.classes = [];
            this.showApiStatus('無法載入班級資料', 'error');
        }
        this.filteredClasses = [...this.classes];
        console.log('🔄 篩選後班級數量:', this.filteredClasses.length);
    }

    async loadClassStudents(classId) {
        try {
            const data = await apiClient.get(`${this.studentsApiPath}/${classId}/students`);
            this.students = Array.isArray(data) ? data : [];
            console.log(`✅ 成功載入班級 ${classId} 的學生資料:`, this.students.length, '位學生');
        } catch (error) {
            console.error('⚠️ 學生資料載入失敗:', error.message);
            this.students = [];
        }
        this.filteredStudents = [...this.students];
    }

    async createClass(payload) {
        try {
            console.log('🆕 開始創建班級，資料:', payload);
            // 使用 relationships.py 的 create-class API
            const response = await apiClient.post(`${this.apiPath}/create-class`, {
                class_name: payload.class_name,
                subject: payload.subject,
                grade: payload.grade || '7',
                school_year: payload.school_year || '2024-2025'
            });
            console.log('✅ 班級創建成功，API回應:', response);
            return response;
        } catch (error) {
            console.error('❌ 班級創建失敗:', error);
            throw error;
        }
    }

    async updateClass(id, payload) {
        try {
            const response = await apiClient.put(`${this.apiPath}/${id}`, payload);
            console.log('✅ 班級更新成功:', response);
            return response;
        } catch (error) {
            console.error('❌ 班級更新失敗:', error);
            throw error;
        }
    }

    async deleteClass(id) {
        try {
            await apiClient.delete(`${this.apiPath}/${id}`);
            console.log('✅ 班級刪除成功:', id);
            return true;
        } catch (error) {
            console.error('❌ 班級刪除失敗:', error);
            throw error;
        }
    }

    async restoreClass(id) {
        try {
            const response = await apiClient.patch(`${this.apiPath}/${id}/restore`);
            console.log('✅ 班級恢復成功:', response);
            return response;
        } catch (error) {
            console.error('❌ 班級恢復失敗:', error);
            throw error;
        }
    }

    async addStudentToClass(classId, studentId, studentNumber = null) {
        try {
            const response = await apiClient.post(`${this.studentsApiPath}/${classId}/students`, { 
                student_id: studentId,
                student_number: studentNumber
            });
            console.log('✅ 學生加入班級成功:', response);
            return response;
        } catch (error) {
            console.error('❌ 學生加入班級失敗:', error);
            throw error;
        }
    }

    async removeStudentFromClass(classId, studentId) {
        try {
            await apiClient.delete(`${this.studentsApiPath}/${classId}/students/${studentId}`);
            console.log('✅ 學生從班級移除成功');
            return true;
        } catch (error) {
            console.error('❌ 學生從班級移除失敗:', error);
            throw error;
        }
    }

    async searchStudents(keyword, limit = 10) {
        try {
            const response = await apiClient.get(`/relationships/students/search?kw=${encodeURIComponent(keyword)}&limit=${limit}`);
            return response || [];
        } catch (error) {
            console.error('❌ 學生搜尋失敗:', error);
            return [];
        }
    }

    setupEventListeners() {
        try {
            // 班級搜尋和篩選
            const searchInput = document.getElementById('classSearchInput');
            const statusFilter = document.getElementById('classStatusFilter');
            const subjectFilter = document.getElementById('classSubjectFilter');
            
            if (searchInput) searchInput.addEventListener('input', () => this.filterClasses());
            if (statusFilter) statusFilter.addEventListener('change', () => this.filterClasses());
            if (subjectFilter) subjectFilter.addEventListener('change', () => this.filterClasses());

            // 視圖切換
            const viewButtons = document.querySelectorAll('.view-btn');
            viewButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.switchView(e.currentTarget.dataset.view);
                });
            });

            // 班級操作按鈕
            document.addEventListener('click', (e) => {
                if (e.target.matches('.btn-create-class')) {
                    e.preventDefault();
                    this.openClassModal();
                } else if (e.target.matches('.btn-edit-class')) {
                    const classId = e.target.getAttribute('data-id');
                    this.editClass(classId);
                } else if (e.target.matches('.btn-delete-class')) {
                    const classId = e.target.getAttribute('data-id');
                    this.deleteClassConfirm(classId);
                } else if (e.target.matches('.btn-restore-class')) {
                    const classId = e.target.getAttribute('data-id');
                    this.restoreClassConfirm(classId);
                } else if (e.target.matches('.btn-manage-students')) {
                    const classId = e.target.getAttribute('data-id');
                    this.openStudentModal(classId);
                }
            });

            // Modal 事件
            const classModalClose = document.getElementById('classModalClose');
            const classModalCancel = document.getElementById('classModalCancel');
            const classModalSave = document.getElementById('classModalSave');
            
            if (classModalClose) classModalClose.addEventListener('click', () => this.closeClassModal());
            if (classModalCancel) classModalCancel.addEventListener('click', () => this.closeClassModal());
            if (classModalSave) classModalSave.addEventListener('click', () => this.handleClassSave());

            // 學生管理 Modal 事件
            const studentModalClose = document.getElementById('studentModalClose');
            const addStudentBtn = document.getElementById('addStudentBtn');
            
            if (studentModalClose) studentModalClose.addEventListener('click', () => this.closeStudentModal());
            if (addStudentBtn) addStudentBtn.addEventListener('click', () => this.openAddStudentModal());

            // 學生搜尋 Modal 事件
            const studentSearchModalClose = document.getElementById('studentSearchModalClose');
            const searchStudentBtn = document.getElementById('searchStudentBtn');
            
            if (studentSearchModalClose) studentSearchModalClose.addEventListener('click', () => this.closeStudentSearchModal());
            if (searchStudentBtn) searchStudentBtn.addEventListener('click', () => this.handleStudentSearch());

            console.log('✅ 班級管理事件綁定完成');
        } catch (error) {
            console.error('❌ 班級管理事件綁定失敗:', error);
        }
    }

    openClassModal(title = '新增班級', classData = null) {
        const modal = document.getElementById('classModal');
        if (!modal) return;

        document.getElementById('classModalTitle').textContent = title;
        modal.style.display = 'flex';

        if (classData) {
            this.editingId = classData.id;
            document.getElementById('className').value = classData.class_name || classData.name || '';
            document.getElementById('classSubject').value = classData.subject || '';
            document.getElementById('classDescription').value = classData.description || '';
            document.getElementById('classGrade').value = classData.grade || '';
        } else {
            this.editingId = null;
            document.getElementById('classForm').reset();
        }
    }

    closeClassModal() {
        const modal = document.getElementById('classModal');
        if (modal) modal.style.display = 'none';
    }

    async handleClassSave() {
        const payload = {
            class_name: document.getElementById('className').value.trim(),
            subject: document.getElementById('classSubject').value,
            description: document.getElementById('classDescription').value.trim(),
            grade: document.getElementById('classGrade').value
        };

        if (!payload.class_name || !payload.subject) {
            alert('請填寫班級名稱和科目');
            return;
        }

        try {
            if (this.editingId) {
                await this.updateClass(this.editingId, payload);
            } else {
                await this.createClass(payload);
            }
            
            // 強制重新載入班級資料（不使用緩存）
            await this.loadClasses(true);
            
            // 清除篩選器，確保新班級能顯示
            this.clearFilters();
            
            // 確保篩選和渲染正確執行
            this.filteredClasses = [...this.classes];
            this.renderClasses();
            this.updateStats();
            
            this.closeClassModal();
            alert('班級儲存成功');
            
            // 添加調試日誌
            console.log('🔄 班級儲存後刷新完成，當前班級數量:', this.classes.length);
        } catch (error) {
            alert('儲存失敗：' + (error.message || '未知錯誤'));
        }
    }

    editClass(classId) {
        const classData = this.classes.find(c => c.id == classId);
        if (classData) {
            this.openClassModal('編輯班級', classData);
        }
    }

    async deleteClassConfirm(classId) {
        if (!confirm('確定要刪除這個班級嗎？此操作無法復原。')) return;
        
        try {
            await this.deleteClass(classId);
            await this.loadClasses(true); // 強制刷新
            this.filterClasses();
            this.updateStats();
            alert('班級刪除成功');
        } catch (error) {
            alert('刪除失敗：' + (error.message || '未知錯誤'));
        }
    }

    async restoreClassConfirm(classId) {
        if (!confirm('確定要恢復這個班級嗎？')) return;
        
        try {
            await this.restoreClass(classId);
            await this.loadClasses(true); // 強制刷新
            this.filterClasses();
            this.updateStats();
            alert('班級恢復成功');
        } catch (error) {
            alert('恢復失敗：' + (error.message || '未知錯誤'));
        }
    }

    openStudentModal(classId) {
        const modal = document.getElementById('studentModal');
        if (!modal) return;

        this.selectedClassId = classId;
        modal.style.display = 'flex';
        
        // 載入班級學生資料
        this.loadClassStudents(classId).then(() => {
            this.renderStudentList();
        });
    }

    closeStudentModal() {
        const modal = document.getElementById('studentModal');
        if (modal) modal.style.display = 'none';
        this.selectedClassId = null;
    }

    openAddStudentModal() {
        // 打開學生搜尋 Modal
        const modal = document.getElementById('studentSearchModal');
        if (modal) {
            modal.style.display = 'flex';
            this.loadTeacherClasses();
        }
    }

    closeStudentSearchModal() {
        const modal = document.getElementById('studentSearchModal');
        if (modal) modal.style.display = 'none';
    }

    async handleStudentSearch() {
        const keyword = document.getElementById('studentSearchInput').value.trim();
        if (!keyword) {
            alert('請輸入搜尋關鍵字');
            return;
        }

        try {
            const students = await this.searchStudents(keyword);
            this.renderSearchResults(students);
        } catch (error) {
            alert('搜尋失敗：' + error.message);
        }
    }

    renderSearchResults(students) {
        const container = document.getElementById('searchResults');
        if (!container) return;

        if (students.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">沒有找到符合條件的學生</p>';
            return;
        }

        container.innerHTML = students.map(student => `
            <div class="flex items-center justify-between p-3 border border-gray-200 rounded-lg mb-2">
                <div>
                    <h4 class="font-semibold">${student.full_name}</h4>
                    <p class="text-sm text-gray-600">${student.email}</p>
                </div>
                <button class="btn btn-primary btn-sm" onclick="addStudentToClass(${student.id})">
                    加入班級
                </button>
            </div>
        `).join('');
    }

    async loadTeacherClasses() {
        try {
            const response = await apiClient.get(`${this.apiPath}?include_deleted=true`);
            const classSelect = document.getElementById('targetClassSelect');
            if (classSelect && response) {
                classSelect.innerHTML = '<option value="">請選擇班級</option>';
                response.forEach(cls => {
                    if (cls.is_active) {
                        const option = document.createElement('option');
                        option.value = cls.class_id;
                        option.textContent = `${cls.class_name} (${cls.subject})`;
                        classSelect.appendChild(option);
                    }
                });
            }
        } catch (error) {
            console.error('載入班級失敗:', error);
        }
    }

    filterClasses() {
        console.log('🔍 開始篩選班級，總數:', this.classes.length);
        
        const searchTerm = (document.getElementById('classSearchInput')?.value || '').toLowerCase();
        const statusFilter = document.getElementById('classStatusFilter')?.value || '';
        const subjectFilter = document.getElementById('classSubjectFilter')?.value || '';

        this.filteredClasses = this.classes.filter(cls => {
            const matchesSearch = (cls.class_name || '').toLowerCase().includes(searchTerm) ||
                (cls.subject || '').toLowerCase().includes(searchTerm);
            const matchesStatus = !statusFilter || 
                (statusFilter === 'active' && cls.is_active) ||
                (statusFilter === 'inactive' && !cls.is_active && !cls.is_deleted) ||
                (statusFilter === 'deleted' && !cls.is_active);
            const matchesSubject = !subjectFilter || cls.subject === subjectFilter;
            return matchesSearch && matchesStatus && matchesSubject;
        });

        console.log('🔍 篩選完成，符合條件的班級數量:', this.filteredClasses.length);
        this.renderClasses();
    }

    switchView(view) {
        this.currentView = view;
        document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
        const activeBtn = document.querySelector(`.view-btn[data-view="${view}"]`);
        activeBtn?.classList.add('active');
        
        if (view === 'list') {
            document.getElementById('listView')?.classList.remove('hidden');
            document.getElementById('gridView')?.classList.add('hidden');
        } else {
            document.getElementById('listView')?.classList.add('hidden');
            document.getElementById('gridView')?.classList.remove('hidden');
        }
        
        this.renderClasses();
    }

    renderClasses() {
        console.log('🎨 開始渲染班級列表，當前視圖:', this.currentView);
        console.log('📊 要渲染的班級數量:', this.filteredClasses.length);
        
        if (this.currentView === 'list') {
            this.renderListView();
        } else {
            this.renderGridView();
        }
        
        console.log('✅ 班級列表渲染完成');
    }

    renderListView() {
        const container = document.getElementById('listView');
        if (!container) return;

        if (this.filteredClasses.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-light);">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                    <p>沒有找到符合條件的班級</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.filteredClasses.map(cls => `
            <div class="class-item">
                <div class="class-header">
                    <div>
                        <div class="class-title">${cls.class_name}</div>
                        <div class="class-meta">
                            <span><i class="fas fa-book"></i> ${cls.subject || '未設定'}</span>
                            <span><i class="fas fa-graduation-cap"></i> ${cls.grade || '未設定'}</span>
                            <span><i class="fas fa-calendar"></i> ${cls.school_year || '未設定'}</span>
                        </div>
                    </div>
                    <div class="class-status ${cls.is_active ? 'active' : 'deleted'}">
                        <i class="fas ${cls.is_active ? 'fa-check-circle' : 'fa-trash'}"></i>
                        ${cls.is_active ? '活躍' : '已刪除'}
                    </div>
                </div>
                <div class="class-actions" style="margin-top: 1rem; display:flex; gap:.5rem;">
                    <button class="action-btn primary btn-edit-class" data-id="${cls.id}">
                        <i class="fas fa-edit"></i> 編輯
                    </button>
                    <button class="action-btn secondary btn-manage-students" data-id="${cls.id}">
                        <i class="fas fa-users"></i> 管理學生
                    </button>
                    ${cls.is_active ? 
                        `<button class="action-btn danger btn-delete-class" data-id="${cls.id}">
                            <i class="fas fa-trash"></i> 刪除
                        </button>` :
                        `<button class="action-btn secondary btn-restore-class" data-id="${cls.id}">
                            <i class="fas fa-undo"></i> 恢復
                        </button>`
                    }
                </div>
            </div>
        `).join('');
    }

    renderGridView() {
        const container = document.getElementById('gridView');
        if (!container) return;

        if (this.filteredClasses.length === 0) {
            container.innerHTML = `
                <div class="classes-grid">
                    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-light);">
                        <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                        <p>沒有找到符合條件的班級</p>
                    </div>
                </div>
            `;
            return;
        }

        const gridContainer = container.querySelector('.classes-grid') || container;
        gridContainer.innerHTML = this.filteredClasses.map(cls => `
            <div class="class-card">
                <div class="class-card-header">
                    <h3 class="class-card-title">${cls.class_name}</h3>
                    <div class="class-status ${cls.is_active ? 'active' : 'deleted'}">
                        ${cls.is_active ? '活躍' : '已刪除'}
                    </div>
                </div>
                <div class="class-card-content">
                    <p class="class-card-info">
                        <span><i class="fas fa-book"></i> 科目：${cls.subject || '未設定'}</span>
                        <span><i class="fas fa-graduation-cap"></i> 年級：${cls.grade || '未設定'}</span>
                        <span><i class="fas fa-calendar"></i> 學年：${cls.school_year || '未設定'}</span>
                    </p>
                </div>
                <div class="class-card-actions">
                    <button class="action-btn primary btn-edit-class" data-id="${cls.id}">
                        <i class="fas fa-edit"></i> 編輯
                    </button>
                    <button class="action-btn secondary btn-manage-students" data-id="${cls.id}">
                        <i class="fas fa-users"></i> 管理學生
                    </button>
                    ${cls.is_active ? 
                        `<button class="action-btn danger btn-delete-class" data-id="${cls.id}">
                            <i class="fas fa-trash"></i> 刪除
                        </button>` :
                        `<button class="action-btn secondary btn-restore-class" data-id="${cls.id}">
                            <i class="fas fa-undo"></i> 恢復
                        </button>`
                    }
                </div>
            </div>
        `).join('');
    }

    renderStudentList() {
        const container = document.getElementById('studentList');
        if (!container) return;

        if (this.students.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--text-light);">
                    <i class="fas fa-users" style="font-size: 2rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                    <p>此班級暫無學生</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.students.map(student => `
            <div class="student-item">
                <div class="student-info">
                    <div class="student-name">${student.student_name || '未知學生'}</div>
                    <div class="student-email">學號：${student.student_number || '未設定'}</div>
                </div>
                <div class="student-actions">
                    <button class="btn btn-danger btn-sm" onclick="classesManager.removeStudentAndRefresh('${this.selectedClassId}', '${student.student_id}')">
                        移除
                    </button>
                </div>
            </div>
        `).join('');
    }

    updateStats() {
        const stats = {
            total: this.classes.length,
            active: this.classes.filter(c => c.is_active).length,
            inactive: this.classes.filter(c => !c.is_active && !c.is_deleted).length,
            deleted: this.classes.filter(c => !c.is_active).length
        };

        const totalElement = document.getElementById('totalClasses');
        const activeElement = document.getElementById('activeClasses');
        const inactiveElement = document.getElementById('inactiveClasses');
        const deletedElement = document.getElementById('deletedClasses');

        if (totalElement) totalElement.textContent = stats.total;
        if (activeElement) activeElement.textContent = stats.active;
        if (inactiveElement) inactiveElement.textContent = stats.inactive;
        if (deletedElement) deletedElement.textContent = stats.deleted;
    }

    showApiStatus(message, type = 'error') {
        const container = document.getElementById('classesList');
        const icon = type === 'error' ? 'fa-exclamation-triangle' : 'fa-info-circle';
        const color = type === 'error' ? 'text-red-500' : 'text-blue-500';
        
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem;">
                    <i class="fas ${icon} ${color}" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p class="${color}">${message}</p>
                    <button onclick="classesManager.loadClasses()" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        重新載入
                    </button>
                </div>
            `;
        }
    }

    renderEmptyState() {
        const container = document.getElementById('classesList');
        if (!container) return;

        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-lock empty-state-icon"></i>
                <p class="empty-state-text">您尚未登入，請先登入以使用班級管理功能。</p>
                <a href="../login.html" class="btn btn-primary mt-4">前往登入</a>
            </div>
        `;
    }

    async removeStudentAndRefresh(classId, studentId) {
        if (!confirm('確定要將此學生從班級中移除嗎？')) return;
        
        try {
            await this.removeStudentFromClass(classId, studentId);
            alert('學生移除成功');
            // 重新載入學生列表
            await this.loadClassStudents(classId);
            this.renderStudentList();
            // 重新載入班級資料並更新統計
            await this.loadClasses(true); // 強制刷新
            this.filterClasses();
            this.updateStats();
        } catch (error) {
            alert('移除失敗：' + (error.message || '未知錯誤'));
        }
    }

    startAutoRefresh() {
        if (this.autoRefreshEnabled && !this.autoRefreshInterval) {
            console.log('✅ 啟動自動刷新機制，間隔：', this.refreshIntervalMs / 1000, '秒');
            this.autoRefreshInterval = setInterval(() => {
                this.silentRefresh();
            }, this.refreshIntervalMs);
        }
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            console.log('⏹️ 停止自動刷新');
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    async silentRefresh() {
        try {
            // 靜默刷新，不顯示錯誤訊息
            const previousCount = this.classes.length;
            await this.loadClasses(true); // 強制刷新，不使用緩存
            this.filterClasses();
            this.updateStats();
            
            // 如果資料有變化，在控制台記錄
            const currentCount = this.classes.length;
            if (previousCount !== currentCount) {
                console.log('🔄 自動刷新檢測到資料變化，班級數量：', previousCount, '→', currentCount);
            }
        } catch (error) {
            console.warn('⚠️ 自動刷新失敗:', error.message);
        }
    }

    // 清除所有篩選器
    clearFilters() {
        console.log('🧹 清除所有篩選器');
        
        // 清除搜尋輸入
        const searchInput = document.getElementById('classSearchInput');
        if (searchInput) searchInput.value = '';
        
        // 清除狀態篩選
        const statusFilter = document.getElementById('classStatusFilter');
        if (statusFilter) statusFilter.value = '';
        
        // 清除科目篩選
        const subjectFilter = document.getElementById('classSubjectFilter');
        if (subjectFilter) subjectFilter.value = '';
        
        console.log('🧹 篩選器已清除');
    }

    // 在頁面卸載時清理定時器
    destroy() {
        this.stopAutoRefresh();
    }
}

// 全域函數
function createClass() { classesManager.openClassModal('新增班級'); }
function editClass(id) { classesManager.editClass(id); }
function deleteClass(id) { classesManager.deleteClassConfirm(id); }
function restoreClass(id) { classesManager.restoreClassConfirm(id); }
function manageStudents(id) { classesManager.openStudentModal(id); }
function switchClassView(view) { classesManager.switchView(view); }
function filterClasses() { classesManager.filterClasses(); }

// 學生管理相關全域函數
function addStudentToClass(studentId) {
    const targetClassId = document.getElementById('targetClassSelect').value;
    if (!targetClassId) {
        alert('請選擇目標班級');
        return;
    }
    
    classesManager.addStudentToClass(targetClassId, studentId).then(() => {
        alert('學生加入班級成功');
        // 關閉搜尋 Modal
        const modal = document.getElementById('studentSearchModal');
        if (modal) modal.style.display = 'none';
        // 重新載入班級資料和更新統計
        classesManager.loadClasses(true).then(() => { // 強制刷新
            classesManager.filterClasses();
            classesManager.updateStats();
        });
    }).catch(error => {
        alert('加入失敗：' + error.message);
    });
}

// 快速操作相關全域函數
function exportClassData() {
    if (!classesManager || !classesManager.classes || classesManager.classes.length === 0) {
        alert('沒有班級資料可以匯出');
        return;
    }
    
    try {
        const dataStr = JSON.stringify(classesManager.classes, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `班級資料_${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        URL.revokeObjectURL(url);
        alert('班級資料匯出成功！');
    } catch (error) {
        alert('匯出失敗：' + error.message);
    }
}

function importClassData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                if (Array.isArray(data)) {
                    alert(`成功讀取 ${data.length} 筆班級資料\n注意：匯入功能需要後端API支援`);
                } else {
                    alert('檔案格式不正確，請選擇有效的JSON檔案');
                }
            } catch (error) {
                alert('檔案讀取失敗：' + error.message);
            }
        };
        reader.readAsText(file);
    };
    input.click();
}

function bulkActions() {
    alert('批次操作功能開發中...\n將包含：批量啟用/停用班級、批量刪除、批量匯出等功能');
}

function manualRefresh() {
    console.log('🔄 手動刷新開始...');
    if (classesManager) {
        // 清除緩存並強制刷新
        apiClient.clearCache();
        classesManager.loadClasses(true).then(() => {
            classesManager.filterClasses();
            classesManager.updateStats();
            console.log('✅ 手動刷新完成');
            alert('資料已刷新！');
        }).catch(error => {
            console.error('❌ 手動刷新失敗:', error);
            alert('刷新失敗：' + error.message);
        });
    } else {
        alert('班級管理器未初始化');
    }
}

// 初始化
let classesManager;
document.addEventListener('DOMContentLoaded', () => {
    classesManager = new ClassesManager();
});

// 頁面卸載時清理資源
window.addEventListener('beforeunload', () => {
    if (classesManager) {
        classesManager.destroy();
    }
});
