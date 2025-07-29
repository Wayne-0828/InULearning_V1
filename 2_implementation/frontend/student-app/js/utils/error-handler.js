// 全局錯誤處理器
class ErrorHandler {
    constructor() {
        this.setupGlobalErrorHandling();
    }

    // 設置全局錯誤處理
    setupGlobalErrorHandling() {
        // 捕獲未處理的Promise拒絕
        window.addEventListener('unhandledrejection', (event) => {
            console.error('未處理的Promise拒絕:', event.reason);
            this.showError('系統發生錯誤，請稍後再試', 'error');
            event.preventDefault();
        });

        // 捕獲JavaScript錯誤
        window.addEventListener('error', (event) => {
            console.error('JavaScript錯誤:', event.error);
            this.showError('頁面載入發生錯誤，請重新整理', 'error');
        });

        // 捕獲網路錯誤
        this.setupNetworkErrorHandling();
    }

    // 設置網路錯誤處理
    setupNetworkErrorHandling() {
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                // 處理HTTP錯誤狀態
                if (!response.ok) {
                    await this.handleHTTPError(response);
                }
                
                return response;
            } catch (error) {
                this.handleNetworkError(error);
                throw error;
            }
        };
    }

    // 處理HTTP錯誤
    async handleHTTPError(response) {
        const url = response.url;
        const status = response.status;
        
        let errorMessage = '請求失敗';
        let errorType = 'error';

        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
            // 無法解析錯誤回應，使用預設訊息
        }

        switch (status) {
            case 400:
                errorMessage = '請求參數錯誤：' + errorMessage;
                errorType = 'warning';
                break;
            case 401:
                errorMessage = '登入已過期，請重新登入';
                errorType = 'warning';
                this.handleAuthError();
                break;
            case 403:
                errorMessage = '權限不足：' + errorMessage;
                errorType = 'warning';
                break;
            case 404:
                errorMessage = '請求的資源不存在';
                errorType = 'warning';
                break;
            case 422:
                errorMessage = '資料驗證失敗：' + errorMessage;
                errorType = 'warning';
                break;
            case 429:
                errorMessage = '請求過於頻繁，請稍後再試';
                errorType = 'warning';
                break;
            case 500:
                errorMessage = '伺服器內部錯誤，請稍後再試';
                errorType = 'error';
                break;
            case 502:
            case 503:
            case 504:
                errorMessage = '服務暫時不可用，請稍後再試';
                errorType = 'error';
                break;
            default:
                errorMessage = `請求失敗 (${status})：${errorMessage}`;
                errorType = 'error';
        }

        console.error(`HTTP錯誤 ${status} - ${url}:`, errorMessage);
        this.showError(errorMessage, errorType);
    }

    // 處理網路錯誤
    handleNetworkError(error) {
        let errorMessage = '網路連接失敗';
        let errorType = 'error';

        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage = '無法連接到伺服器，請檢查網路連接';
        } else if (error.name === 'AbortError') {
            errorMessage = '請求已取消';
            errorType = 'info';
        } else if (error.message.includes('timeout')) {
            errorMessage = '請求超時，請稍後再試';
        }

        console.error('網路錯誤:', error);
        this.showError(errorMessage, errorType);
    }

    // 處理認證錯誤
    handleAuthError() {
        // 清除認證資訊
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
        
        // 延遲跳轉到登入頁面，讓用戶看到錯誤訊息
        setTimeout(() => {
            window.location.href = 'http://localhost/login.html';
        }, 2000);
    }

    // 顯示錯誤訊息
    showError(message, type = 'error', duration = 5000) {
        this.removeExistingToast();
        
        const toast = document.createElement('div');
        toast.id = 'errorToast';
        toast.className = `fixed top-4 right-4 max-w-sm w-full z-50 transform translate-x-0 transition-all duration-300`;
        
        const bgColor = this.getToastBgColor(type);
        const icon = this.getToastIcon(type);
        
        toast.innerHTML = `
            <div class="${bgColor} text-white p-4 rounded-lg shadow-lg">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        ${icon}
                    </div>
                    <div class="ml-3 flex-1">
                        <p class="text-sm font-medium">${message}</p>
                    </div>
                    <div class="ml-4 flex-shrink-0">
                        <button onclick="errorHandler.removeToast()" class="text-white hover:text-gray-200 focus:outline-none">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // 自動隱藏
        if (duration > 0) {
            setTimeout(() => {
                this.removeToast();
            }, duration);
        }
    }

    // 顯示成功訊息
    showSuccess(message, duration = 3000) {
        this.showError(message, 'success', duration);
    }

    // 顯示警告訊息
    showWarning(message, duration = 4000) {
        this.showError(message, 'warning', duration);
    }

    // 顯示資訊訊息
    showInfo(message, duration = 3000) {
        this.showError(message, 'info', duration);
    }

    // 獲取Toast背景顏色
    getToastBgColor(type) {
        switch (type) {
            case 'success':
                return 'bg-green-500';
            case 'warning':
                return 'bg-yellow-500';
            case 'info':
                return 'bg-blue-500';
            case 'error':
            default:
                return 'bg-red-500';
        }
    }

    // 獲取Toast圖標
    getToastIcon(type) {
        switch (type) {
            case 'success':
                return `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                </svg>`;
            case 'warning':
                return `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                </svg>`;
            case 'info':
                return `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                </svg>`;
            case 'error':
            default:
                return `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                </svg>`;
        }
    }

    // 移除現有的Toast
    removeExistingToast() {
        const existingToast = document.getElementById('errorToast');
        if (existingToast) {
            existingToast.remove();
        }
    }

    // 移除Toast
    removeToast() {
        const toast = document.getElementById('errorToast');
        if (toast) {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }
    }

    // 顯示載入中指示器
    showLoading(message = '載入中...') {
        this.hideLoading(); // 先隱藏現有的載入指示器
        
        const loading = document.createElement('div');
        loading.id = 'globalLoading';
        loading.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        
        loading.innerHTML = `
            <div class="bg-white rounded-lg p-6 flex items-center space-x-4">
                <svg class="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-gray-700 font-medium">${message}</span>
            </div>
        `;
        
        document.body.appendChild(loading);
    }

    // 隱藏載入中指示器
    hideLoading() {
        const loading = document.getElementById('globalLoading');
        if (loading) {
            loading.remove();
        }
    }
}

// 創建全局錯誤處理實例
window.errorHandler = new ErrorHandler(); 