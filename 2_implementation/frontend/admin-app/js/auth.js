/**
 * 管理員應用程式認證管理 (Admin App Authentication) - InULearning 個人化學習平台
 * 
 * 功能：
 * - JWT Token 管理
 * - 登入狀態檢查
 * - 自動登入
 * - 登出功能
 */

class AdminAuthManager {
    constructor() {
        this.apiClient = new ApiClient();
        this.currentUser = null;
        this.init();
    }

    /**
     * 初始化認證管理器
     */
    init() {
        this.checkAuthStatus();
        this.setupEventListeners();
    }

    /**
     * 設定事件監聽器
     */
    setupEventListeners() {
        // 登出按鈕
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }
    }

    /**
     * 檢查認證狀態
     */
    async checkAuthStatus() {
        // 處理從統一登入頁面傳來的認證資訊
        this.handleAuthFromURL();

        const token = Utils.getStorageItem('auth_token');

        if (!token) {
            this.redirectToLogin();
            return;
        }

        try {
            this.apiClient.setAuthToken(token);
            const response = await this.apiClient.get('/auth/verify');

            if (response.success) {
                this.currentUser = response.data.user;
                this.updateUI();
            } else {
                this.clearAuth();
                this.redirectToLogin();
            }
        } catch (error) {
            console.error('認證檢查失敗:', error);
            this.clearAuth();
            this.redirectToLogin();
        }
    }

    /**
     * 處理URL參數中的認證資訊
     */
    handleAuthFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        const userInfo = urlParams.get('userInfo');

        if (token && userInfo) {
            console.log('從URL接收到認證資訊');

            // 儲存到localStorage
            Utils.setStorageItem('auth_token', token);
            Utils.setStorageItem('user_info', userInfo);

            // 解析用戶資訊
            try {
                this.currentUser = JSON.parse(userInfo);
            } catch (e) {
                console.error('解析用戶資訊失敗:', e);
            }

            // 清除URL參數
            const newURL = window.location.protocol + "//" + window.location.host + window.location.pathname;
            window.history.replaceState({}, document.title, newURL);

            // 更新UI
            this.updateUI();
        }
    }

    /**
     * 更新 UI 顯示
     */
    updateUI() {
        if (this.currentUser) {
            const adminNameElement = document.getElementById('admin-name');
            if (adminNameElement) {
                adminNameElement.textContent = this.currentUser.name || this.currentUser.email;
            }
        }
    }

    /**
     * 登入
     * @param {string} email - 電子郵件
     * @param {string} password - 密碼
     */
    async login(email, password) {
        try {
            Utils.showLoading();

            const response = await this.apiClient.post('/auth/login', {
                email: email,
                password: password,
                role: 'admin'
            });

            if (response.success) {
                const { access_token, user } = response.data;

                // 儲存 Token 和用戶資訊
                Utils.setStorageItem('auth_token', access_token);
                Utils.setStorageItem('user_info', JSON.stringify(user));

                this.currentUser = user;
                this.apiClient.setAuthToken(access_token);

                // 顯示成功訊息
                Utils.showAlert('登入成功！', 'success');

                // 延遲跳轉
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
            } else {
                Utils.showAlert(response.message || '登入失敗', 'error');
            }
        } catch (error) {
            console.error('登入錯誤:', error);
            Utils.showAlert('登入失敗，請檢查網路連線', 'error');
        } finally {
            Utils.hideLoading();
        }
    }

    /**
     * 登出
     */
    async logout() {
        try {
            const token = Utils.getStorageItem('auth_token');
            if (token) {
                // 呼叫登出 API
                await this.apiClient.post('/auth/logout');
            }
        } catch (error) {
            console.error('登出 API 錯誤:', error);
        } finally {
            this.clearAuth();
            Utils.showAlert('已成功登出', 'success');

            setTimeout(() => {
                this.redirectToLogin();
            }, 1000);
        }
    }

    /**
     * 清除認證資訊
     */
    clearAuth() {
        Utils.removeStorageItem('auth_token');
        Utils.removeStorageItem('user_info');
        this.currentUser = null;
        this.apiClient.clearAuthToken();
    }

    /**
     * 跳轉到登入頁面
     */
    redirectToLogin() {
        if (window.location.pathname !== '/admin-app/pages/login.html') {
            const loginUrl = (window?.Utils?.config?.LOGIN_URL) || '/login.html';
            window.location.href = loginUrl;
        }
    }

    /**
     * 檢查是否已登入
     * @returns {boolean}
     */
    isAuthenticated() {
        return !!Utils.getStorageItem('auth_token') && !!this.currentUser;
    }

    /**
     * 取得當前用戶
     * @returns {Object|null}
     */
    getCurrentUser() {
        return this.currentUser;
    }

    /**
     * 取得認證 Token
     * @returns {string|null}
     */
    getToken() {
        return Utils.getStorageItem('auth_token');
    }
}

// 全域認證管理器實例
const adminAuth = new AdminAuthManager(); 