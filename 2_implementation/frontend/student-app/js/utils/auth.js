/**
 * 認證工具函數
 * 處理 JWT token 和用戶狀態管理
 */

class AuthManager {
    constructor() {
        this.tokenKey = 'auth_token';
        this.userKey = 'user_info';
        this.baseURL = 'http://localhost:8001'; // auth-service 的預設端口
    }

    /**
     * 檢查用戶是否已登入
     */
    isLoggedIn() {
        return !!this.getToken();
    }

    /**
     * 獲取 JWT token
     */
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    /**
     * 設置 JWT token
     */
    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    /**
     * 移除 JWT token
     */
    removeToken() {
        localStorage.removeItem(this.tokenKey);
    }

    /**
     * 獲取用戶資訊
     */
    getUser() {
        try {
            return JSON.parse(localStorage.getItem(this.userKey));
        } catch {
            return null;
        }
    }

    /**
     * 設置用戶資訊
     */
    setUser(user) {
        localStorage.setItem('user_info', JSON.stringify(user));
    }

    /**
     * 移除用戶資訊
     */
    removeUser() {
        localStorage.removeItem(this.userKey);
    }

    /**
     * 解析 JWT token
     */
    parseToken(token) {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    }

    /**
     * 登出
     */
    logout() {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
        this.updateAuthUI();
        window.location.href = 'http://localhost/login.html';
    }

    /**
     * 更新頁面認證狀態
     */
    updateAuthUI() {
        const userInfo = document.getElementById('userInfo');
        const authButtons = document.getElementById('authButtons');
        const userName = document.getElementById('userName');
        const logoutBtn = document.getElementById('logoutBtn');

        if (this.isLoggedIn()) {
            const user = this.getUser();
            if (userInfo) userInfo.classList.remove('hidden');
            if (userName) userName.textContent = user?.email || '用戶';
            if (authButtons) authButtons.classList.add('hidden');
            if (logoutBtn) logoutBtn.classList.remove('hidden');
        } else {
            if (userInfo) userInfo.classList.add('hidden');
            if (authButtons) authButtons.classList.remove('hidden');
            if (logoutBtn) logoutBtn.classList.add('hidden');
        }
    }

    /**
     * 獲取認證標頭
     */
    getAuthHeaders() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    /**
     * 處理 API 錯誤
     */
    handleApiError(error) {
        console.error('API 錯誤:', error);

        if (error.status === 401) {
            // Token 過期或無效
            this.logout();
            return '登入已過期，請重新登入';
        } else if (error.status === 403) {
            return '權限不足';
        } else if (error.status === 404) {
            return '資源不存在';
        } else if (error.status >= 500) {
            return '伺服器錯誤，請稍後再試';
        } else {
            return error.message || '發生未知錯誤';
        }
    }

    /**
     * 顯示錯誤訊息
     */
    showError(message, elementId = 'errorMessage') {
        const errorElement = document.getElementById(elementId);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');

            // 5秒後自動隱藏
            setTimeout(() => {
                errorElement.classList.add('hidden');
            }, 5000);
        }
    }

    /**
     * 顯示成功訊息
     */
    showSuccess(message, elementId = 'successMessage') {
        const successElement = document.getElementById(elementId);
        if (successElement) {
            successElement.textContent = message;
            successElement.classList.remove('hidden');

            // 3秒後自動隱藏
            setTimeout(() => {
                successElement.classList.add('hidden');
            }, 3000);
        }
    }

    /**
     * 設置載入狀態
     */
    setLoading(isLoading, buttonElement, originalText) {
        if (buttonElement) {
            const spinner = buttonElement.querySelector('.loading-spinner') ||
                buttonElement.querySelector('[id$="Spinner"]');
            const text = buttonElement.querySelector('[id$="ButtonText"]') ||
                buttonElement.querySelector('span:not(.loading-spinner)');

            if (isLoading) {
                buttonElement.disabled = true;
                buttonElement.classList.add('opacity-50');
                if (spinner) spinner.classList.remove('hidden');
                if (text) text.textContent = '處理中...';
            } else {
                buttonElement.disabled = false;
                buttonElement.classList.remove('opacity-50');
                if (spinner) spinner.classList.add('hidden');
                if (text && originalText) text.textContent = originalText;
            }
        }
    }
}

// 創建全域認證管理器實例
const authManager = new AuthManager();

// 立即導出認證管理器到全域
window.authManager = authManager;

// 頁面載入時更新認證狀態
document.addEventListener('DOMContentLoaded', () => {
    authManager.updateAuthUI();

    // 綁定登出按鈕事件
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            authManager.logout();
        });
    }
}); 