/**
 * 用戶管理功能 (Users Management) - InULearning 個人化學習平台
 * 
 * 功能：
 * - 用戶列表載入與顯示
 * - 搜尋與篩選
 * - 新增/編輯/刪除用戶
 * - 分頁處理
 * - 批量操作
 */

class UsersManager {
    constructor() {
        this.apiClient = new ApiClient();
        this.users = [];
        this.filteredUsers = [];
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.totalPages = 0;
        this.selectedUsers = new Set();
        this.filters = {
            search: '',
            role: '',
            status: ''
        };
        
        this.init();
    }
    
    /**
     * 初始化用戶管理器
     */
    async init() {
        this.setupEventListeners();
        await this.loadUsers();
        this.updateStats();
    }
    
    /**
     * 設定事件監聽器
     */
    setupEventListeners() {
        // 搜尋和篩選
        const searchInput = document.getElementById('search-input');
        const roleFilter = document.getElementById('role-filter');
        const statusFilter = document.getElementById('status-filter');
        const clearFiltersBtn = document.getElementById('clear-filters-btn');
        
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filters.search = e.target.value;
                this.applyFilters();
            });
        }
        
        if (roleFilter) {
            roleFilter.addEventListener('change', (e) => {
                this.filters.role = e.target.value;
                this.applyFilters();
            });
        }
        
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.applyFilters();
            });
        }
        
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => {
                this.clearFilters();
            });
        }
        
        // 操作按鈕
        const addUserBtn = document.getElementById('add-user-btn');
        const exportUsersBtn = document.getElementById('export-users-btn');
        
        if (addUserBtn) {
            addUserBtn.addEventListener('click', () => {
                this.showUserModal();
            });
        }
        
        if (exportUsersBtn) {
            exportUsersBtn.addEventListener('click', () => {
                this.exportUsers();
            });
        }
        
        // 全選/取消全選
        const selectAllCheckbox = document.getElementById('select-all');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }
        
        // 分頁控制
        const prevPageBtn = document.getElementById('prev-page');
        const nextPageBtn = document.getElementById('next-page');
        
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => {
                this.goToPage(this.currentPage - 1);
            });
        }
        
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => {
                this.goToPage(this.currentPage + 1);
            });
        }
        
        // 模態框事件
        this.setupModalEventListeners();
    }
    
    /**
     * 設定模態框事件監聽器
     */
    setupModalEventListeners() {
        const userModal = document.getElementById('user-modal');
        const deleteModal = document.getElementById('delete-modal');
        
        // 用戶模態框
        if (userModal) {
            const closeModalBtn = document.getElementById('close-modal');
            const cancelBtn = document.getElementById('cancel-btn');
            const saveBtn = document.getElementById('save-btn');
            
            if (closeModalBtn) {
                closeModalBtn.addEventListener('click', () => {
                    this.closeUserModal();
                });
            }
            
            if (cancelBtn) {
                cancelBtn.addEventListener('click', () => {
                    this.closeUserModal();
                });
            }
            
            if (saveBtn) {
                saveBtn.addEventListener('click', () => {
                    this.saveUser();
                });
            }
        }
        
        // 刪除模態框
        if (deleteModal) {
            const closeDeleteModalBtn = document.getElementById('close-delete-modal');
            const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
            const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
            
            if (closeDeleteModalBtn) {
                closeDeleteModalBtn.addEventListener('click', () => {
                    this.closeDeleteModal();
                });
            }
            
            if (cancelDeleteBtn) {
                cancelDeleteBtn.addEventListener('click', () => {
                    this.closeDeleteModal();
                });
            }
            
            if (confirmDeleteBtn) {
                confirmDeleteBtn.addEventListener('click', () => {
                    this.confirmDeleteUsers();
                });
            }
        }
    }
    
    /**
     * 載入用戶資料
     */
    async loadUsers() {
        try {
            Utils.showLoading();
            
            const response = await this.apiClient.get('/admin/users');
            
            if (response.success) {
                this.users = response.data.users || [];
                this.filteredUsers = [...this.users];
                this.renderUsers();
                this.updatePagination();
            } else {
                Utils.showAlert('載入用戶資料失敗', 'error');
            }
        } catch (error) {
            console.error('載入用戶資料錯誤:', error);
            Utils.showAlert('載入用戶資料失敗，請檢查網路連線', 'error');
        } finally {
            Utils.hideLoading();
        }
    }
    
    /**
     * 渲染用戶列表
     */
    renderUsers() {
        const tbody = document.getElementById('users-tbody');
        if (!tbody) return;
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageUsers = this.filteredUsers.slice(startIndex, endIndex);
        
        tbody.innerHTML = '';
        
        if (pageUsers.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center">
                        <div style="padding: 2rem; color: #666;">
                            <i class="fas fa-users" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
                            <p>沒有找到符合條件的用戶</p>
                        </div>
                    </td>
                </tr>
            `;
            return;
        }
        
        pageUsers.forEach(user => {
            const row = this.createUserRow(user);
            tbody.appendChild(row);
        });
        
        this.updateUsersCount();
    }
    
    /**
     * 建立用戶行
     */
    createUserRow(user) {
        const row = document.createElement('tr');
        row.dataset.userId = user.id;
        
        const avatar = this.getUserAvatar(user.name);
        const roleBadge = this.getRoleBadge(user.role);
        const statusBadge = this.getStatusBadge(user.status);
        const isSelected = this.selectedUsers.has(user.id);
        
        row.innerHTML = `
            <td>
                <input type="checkbox" class="user-checkbox" value="${user.id}" ${isSelected ? 'checked' : ''}>
            </td>
            <td>
                <div class="user-info">
                    <div class="user-avatar">${avatar}</div>
                    <div class="user-details">
                        <h4>${user.name}</h4>
                        <p>${user.email}</p>
                    </div>
                </div>
            </td>
            <td>${roleBadge}</td>
            <td>${statusBadge}</td>
            <td>${this.formatDate(user.created_at)}</td>
            <td>${this.formatDate(user.last_login)}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn view" title="查看詳情" onclick="usersManager.viewUser('${user.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn edit" title="編輯用戶" onclick="usersManager.editUser('${user.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" title="刪除用戶" onclick="usersManager.deleteUser('${user.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        // 添加選擇框事件
        const checkbox = row.querySelector('.user-checkbox');
        checkbox.addEventListener('change', (e) => {
            this.toggleUserSelection(user.id, e.target.checked);
        });
        
        return row;
    }
    
    /**
     * 取得用戶頭像
     */
    getUserAvatar(name) {
        if (!name) return '?';
        return name.charAt(0).toUpperCase();
    }
    
    /**
     * 取得角色標籤
     */
    getRoleBadge(role) {
        const roleNames = {
            'student': '學生',
            'parent': '家長',
            'teacher': '教師',
            'admin': '管理員'
        };
        
        return `<span class="role-badge ${role}">${roleNames[role] || role}</span>`;
    }
    
    /**
     * 取得狀態標籤
     */
    getStatusBadge(status) {
        const statusNames = {
            'active': '啟用',
            'inactive': '停用'
        };
        
        return `<span class="status-badge ${status}">${statusNames[status] || status}</span>`;
    }
    
    /**
     * 格式化日期
     */
    formatDate(dateString) {
        if (!dateString) return '-';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-TW', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    /**
     * 應用篩選
     */
    applyFilters() {
        this.filteredUsers = this.users.filter(user => {
            // 搜尋篩選
            if (this.filters.search) {
                const searchTerm = this.filters.search.toLowerCase();
                const matchesSearch = user.name.toLowerCase().includes(searchTerm) ||
                                    user.email.toLowerCase().includes(searchTerm);
                if (!matchesSearch) return false;
            }
            
            // 角色篩選
            if (this.filters.role && user.role !== this.filters.role) {
                return false;
            }
            
            // 狀態篩選
            if (this.filters.status && user.status !== this.filters.status) {
                return false;
            }
            
            return true;
        });
        
        this.currentPage = 1;
        this.renderUsers();
        this.updatePagination();
    }
    
    /**
     * 清除篩選
     */
    clearFilters() {
        this.filters = {
            search: '',
            role: '',
            status: ''
        };
        
        // 重置表單
        const searchInput = document.getElementById('search-input');
        const roleFilter = document.getElementById('role-filter');
        const statusFilter = document.getElementById('status-filter');
        
        if (searchInput) searchInput.value = '';
        if (roleFilter) roleFilter.value = '';
        if (statusFilter) statusFilter.value = '';
        
        this.applyFilters();
    }
    
    /**
     * 更新統計資料
     */
    updateStats() {
        const stats = {
            total: this.users.length,
            students: this.users.filter(u => u.role === 'student').length,
            parents: this.users.filter(u => u.role === 'parent').length,
            teachers: this.users.filter(u => u.role === 'teacher').length
        };
        
        // 更新統計卡片
        const elements = {
            'total-users-count': stats.total,
            'students-count': stats.students,
            'parents-count': stats.parents,
            'teachers-count': stats.teachers
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }
    
    /**
     * 更新分頁
     */
    updatePagination() {
        this.totalPages = Math.ceil(this.filteredUsers.length / this.itemsPerPage);
        
        // 更新分頁控制
        const prevPageBtn = document.getElementById('prev-page');
        const nextPageBtn = document.getElementById('next-page');
        const pageNumbers = document.getElementById('page-numbers');
        const paginationText = document.getElementById('pagination-text');
        
        if (prevPageBtn) {
            prevPageBtn.disabled = this.currentPage <= 1;
        }
        
        if (nextPageBtn) {
            nextPageBtn.disabled = this.currentPage >= this.totalPages;
        }
        
        if (pageNumbers) {
            this.renderPageNumbers(pageNumbers);
        }
        
        if (paginationText) {
            const start = (this.currentPage - 1) * this.itemsPerPage + 1;
            const end = Math.min(this.currentPage * this.itemsPerPage, this.filteredUsers.length);
            paginationText.textContent = `顯示 ${start}-${end} 個用戶，共 ${this.filteredUsers.length} 個`;
        }
    }
    
    /**
     * 渲染頁碼
     */
    renderPageNumbers(container) {
        container.innerHTML = '';
        
        const maxVisiblePages = 5;
        let startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);
        
        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const pageLink = document.createElement('a');
            pageLink.href = '#';
            pageLink.className = `page-number ${i === this.currentPage ? 'active' : ''}`;
            pageLink.textContent = i;
            pageLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.goToPage(i);
            });
            container.appendChild(pageLink);
        }
    }
    
    /**
     * 前往指定頁面
     */
    goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.currentPage = page;
            this.renderUsers();
            this.updatePagination();
        }
    }
    
    /**
     * 更新用戶數量
     */
    updateUsersCount() {
        const usersCountElement = document.getElementById('users-count');
        if (usersCountElement) {
            usersCountElement.textContent = `顯示 ${this.filteredUsers.length} 個用戶`;
        }
    }
    
    /**
     * 切換全選
     */
    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('.user-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            this.toggleUserSelection(checkbox.value, checked);
        });
    }
    
    /**
     * 切換用戶選擇
     */
    toggleUserSelection(userId, selected) {
        if (selected) {
            this.selectedUsers.add(userId);
        } else {
            this.selectedUsers.delete(userId);
        }
        
        this.updateSelectAllState();
    }
    
    /**
     * 更新全選狀態
     */
    updateSelectAllState() {
        const selectAllCheckbox = document.getElementById('select-all');
        const checkboxes = document.querySelectorAll('.user-checkbox');
        
        if (selectAllCheckbox && checkboxes.length > 0) {
            const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
            selectAllCheckbox.checked = checkedCount === checkboxes.length;
            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
        }
    }
    
    /**
     * 顯示用戶模態框
     */
    showUserModal(userId = null) {
        const modal = document.getElementById('user-modal');
        const modalTitle = document.getElementById('modal-title');
        
        if (modal && modalTitle) {
            if (userId) {
                // 編輯模式
                modalTitle.textContent = '編輯用戶';
                this.loadUserData(userId);
            } else {
                // 新增模式
                modalTitle.textContent = '新增用戶';
                this.resetUserForm();
            }
            
            modal.classList.add('show');
        }
    }
    
    /**
     * 關閉用戶模態框
     */
    closeUserModal() {
        const modal = document.getElementById('user-modal');
        if (modal) {
            modal.classList.remove('show');
            this.resetUserForm();
        }
    }
    
    /**
     * 重置用戶表單
     */
    resetUserForm() {
        const form = document.getElementById('user-form');
        if (form) {
            form.reset();
        }
    }
    
    /**
     * 載入用戶資料
     */
    async loadUserData(userId) {
        try {
            const response = await this.apiClient.get(`/admin/users/${userId}`);
            
            if (response.success) {
                const user = response.data.user;
                this.fillUserForm(user);
            }
        } catch (error) {
            console.error('載入用戶資料錯誤:', error);
            Utils.showAlert('載入用戶資料失敗', 'error');
        }
    }
    
    /**
     * 填寫用戶表單
     */
    fillUserForm(user) {
        const form = document.getElementById('user-form');
        if (!form) return;
        
        form.querySelector('[name="name"]').value = user.name || '';
        form.querySelector('[name="email"]').value = user.email || '';
        form.querySelector('[name="role"]').value = user.role || '';
        form.querySelector('[name="status"]').value = user.status || 'active';
        
        // 編輯模式下密碼為選填
        const passwordFields = form.querySelectorAll('[name="password"], [name="confirm_password"]');
        passwordFields.forEach(field => {
            field.required = false;
        });
    }
    
    /**
     * 儲存用戶
     */
    async saveUser() {
        const form = document.getElementById('user-form');
        if (!form) return;
        
        const formData = new FormData(form);
        const userData = Object.fromEntries(formData.entries());
        
        // 驗證表單
        if (!this.validateUserForm(userData)) {
            return;
        }
        
        try {
            Utils.showLoading();
            
            const modalTitle = document.getElementById('modal-title');
            const isEdit = modalTitle.textContent === '編輯用戶';
            
            let response;
            if (isEdit) {
                // 編輯用戶
                const userId = this.getCurrentEditingUserId();
                response = await this.apiClient.put(`/admin/users/${userId}`, userData);
            } else {
                // 新增用戶
                response = await this.apiClient.post('/admin/users', userData);
            }
            
            if (response.success) {
                Utils.showAlert(isEdit ? '用戶更新成功' : '用戶新增成功', 'success');
                this.closeUserModal();
                await this.loadUsers();
            } else {
                Utils.showAlert(response.message || '操作失敗', 'error');
            }
        } catch (error) {
            console.error('儲存用戶錯誤:', error);
            Utils.showAlert('操作失敗，請檢查網路連線', 'error');
        } finally {
            Utils.hideLoading();
        }
    }
    
    /**
     * 驗證用戶表單
     */
    validateUserForm(data) {
        if (!data.name || !data.email || !data.role) {
            Utils.showAlert('請填寫所有必填欄位', 'error');
            return false;
        }
        
        if (!data.password && !this.isEditMode()) {
            Utils.showAlert('請輸入密碼', 'error');
            return false;
        }
        
        if (data.password && data.password !== data.confirm_password) {
            Utils.showAlert('密碼確認不一致', 'error');
            return false;
        }
        
        return true;
    }
    
    /**
     * 檢查是否為編輯模式
     */
    isEditMode() {
        const modalTitle = document.getElementById('modal-title');
        return modalTitle && modalTitle.textContent === '編輯用戶';
    }
    
    /**
     * 取得當前編輯的用戶 ID
     */
    getCurrentEditingUserId() {
        // 這裡需要實作取得當前編輯用戶 ID 的邏輯
        return null;
    }
    
    /**
     * 查看用戶
     */
    viewUser(userId) {
        // 實作查看用戶詳情的邏輯
        console.log('查看用戶:', userId);
    }
    
    /**
     * 編輯用戶
     */
    editUser(userId) {
        this.showUserModal(userId);
    }
    
    /**
     * 刪除用戶
     */
    deleteUser(userId) {
        this.selectedUsers.clear();
        this.selectedUsers.add(userId);
        this.showDeleteModal();
    }
    
    /**
     * 顯示刪除確認模態框
     */
    showDeleteModal() {
        const modal = document.getElementById('delete-modal');
        if (modal) {
            modal.classList.add('show');
        }
    }
    
    /**
     * 關閉刪除模態框
     */
    closeDeleteModal() {
        const modal = document.getElementById('delete-modal');
        if (modal) {
            modal.classList.remove('show');
        }
    }
    
    /**
     * 確認刪除用戶
     */
    async confirmDeleteUsers() {
        const userIds = Array.from(this.selectedUsers);
        
        if (userIds.length === 0) {
            Utils.showAlert('請選擇要刪除的用戶', 'error');
            return;
        }
        
        try {
            Utils.showLoading();
            
            const response = await this.apiClient.delete('/admin/users', {
                data: { user_ids: userIds }
            });
            
            if (response.success) {
                Utils.showAlert('用戶刪除成功', 'success');
                this.closeDeleteModal();
                this.selectedUsers.clear();
                await this.loadUsers();
            } else {
                Utils.showAlert(response.message || '刪除失敗', 'error');
            }
        } catch (error) {
            console.error('刪除用戶錯誤:', error);
            Utils.showAlert('刪除失敗，請檢查網路連線', 'error');
        } finally {
            Utils.hideLoading();
        }
    }
    
    /**
     * 匯出用戶資料
     */
    exportUsers() {
        // 實作匯出用戶資料的邏輯
        console.log('匯出用戶資料');
        Utils.showAlert('匯出功能正在開發中', 'info');
    }
}

// 全域用戶管理器實例
const usersManager = new UsersManager(); 