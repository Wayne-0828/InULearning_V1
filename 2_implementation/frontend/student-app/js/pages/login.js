/**
 * 登入頁面 JavaScript
 */

class LoginPage {
    constructor() {
        this.form = document.getElementById('loginForm') || document.querySelector('form');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.loginButton = document.querySelector('button[type="submit"]');
        this.rememberMeCheckbox = document.getElementById('rememberMe');
        
        this.init();
    }

    /**
     * 初始化
     */
    init() {
        this.bindEvents();
        this.checkIfAlreadyLoggedIn();
        this.updateAuthUI(); // 初始化時更新認證 UI
    }

    /**
     * 檢查是否已經登入
     */
    checkIfAlreadyLoggedIn() {
        // 暫時跳過登入檢查，允許訪問登入頁面進行測試
       
        
        // 原始登入檢查邏輯（暫時註解）
        if (authManager && authManager.isLoggedIn()) {
            // 已登入，重定向到主頁
            window.location.href = '/index.html';
        }
    }

    /**
     * 綁定事件
     */
    bindEvents() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // 輸入驗證
        if (this.emailInput) {
            this.emailInput.addEventListener('blur', () => {
                this.validateEmail();
            });
            this.emailInput.addEventListener('input', () => {
                this.clearError();
            });
        }

        if (this.passwordInput) {
            this.passwordInput.addEventListener('blur', () => {
                this.validatePassword();
            });
            this.passwordInput.addEventListener('input', () => {
                this.clearError();
            });
        }

        // 註冊連結
        const registerLinks = document.querySelectorAll('a[href*="register"]');
        registerLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = 'register.html';
            });
        });
    }

    /**
     * 驗證電子郵件
     */
    validateEmail() {
        const email = this.emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email) {
            this.showFieldError(this.emailInput, '請輸入電子郵件');
            return false;
        }
        
        if (!emailRegex.test(email)) {
            this.showFieldError(this.emailInput, '請輸入有效的電子郵件格式');
            return false;
        }
        
        this.clearFieldError(this.emailInput);
        return true;
    }

    /**
     * 驗證密碼
     */
    validatePassword() {
        const password = this.passwordInput.value;
        
        if (!password) {
            this.showFieldError(this.passwordInput, '請輸入密碼');
            return false;
        }
        
        if (password.length < 6) {
            this.showFieldError(this.passwordInput, '密碼至少需要6個字符');
            return false;
        }
        
        this.clearFieldError(this.passwordInput);
        return true;
    }

    /**
     * 處理登入
     */
    async handleLogin() {
        // 清除之前的錯誤
        this.clearError();
        
        // 驗證表單
        const isEmailValid = this.validateEmail();
        const isPasswordValid = this.validatePassword();
        
        if (!isEmailValid || !isPasswordValid) {
            return;
        }
        
        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;
        
        try {
            // 設置載入狀態
            this.setLoading(true);
            
            // 調用真實的登入 API
            const response = await authAPI.login(email, password);
            
            // 儲存認證資訊
            if (typeof authManager !== 'undefined') {
                authManager.setToken(response.access_token);
                authManager.setUser(response.user);
            } else {
                localStorage.setItem('auth_token', response.access_token);
                localStorage.setItem('user_info', JSON.stringify(response.user));
            }
            
            // 記住登入狀態（如果勾選）
            if (this.rememberMeCheckbox && this.rememberMeCheckbox.checked) {
                localStorage.setItem('rememberLogin', 'true');
                localStorage.setItem('rememberedEmail', email);
            }
            
            // 顯示成功訊息
            this.showSuccess('登入成功！正在跳轉...');
            
            // 根據用戶角色進行跳轉
            this.redirectByRole(response.user.role);
            
            // 更新認證UI
            if (typeof authManager !== 'undefined' && typeof authManager.updateAuthUI === 'function') {
                authManager.updateAuthUI();
            } else {
                // 如果 authManager 不存在，手動更新 UI
                this.updateAuthUI();
            }
            
            // 延遲跳轉，讓用戶看到成功訊息
            setTimeout(() => {
                console.log('準備跳轉到首頁...');
                console.log('當前路徑:', window.location.pathname);
                console.log('當前URL:', window.location.href);
                
                // 嘗試多種跳轉路徑
                const currentPath = window.location.pathname;
                let targetPath;
                
                if (currentPath.includes('/pages/')) {
                    // 如果在 pages 目錄下，跳轉到上一層的 index.html
                    targetPath = '../index.html';
                } else {
                    // 否則使用絕對路徑
                    targetPath = '/index.html';
                }
                
                console.log('目標路徑:', targetPath);
                
                // 跳轉到學生主頁
                try {
                    window.location.href = targetPath;
                } catch (e) {
                    console.log('href 跳轉失敗，嘗試 replace...');
                    window.location.replace(targetPath);
                }
                
                // 如果 3 秒後還沒跳轉成功，強制跳轉
                setTimeout(() => {
                    if (window.location.pathname !== '/index.html' && !window.location.pathname.endsWith('index.html')) {
                        console.log('強制跳轉到首頁...');
                        try {
                            window.location.replace('/index.html');
                        } catch (e) {
                            console.log('replace 失敗，嘗試 assign...');
                            window.location.assign('/index.html');
                        }
                    }
                }, 3000);
            }, 1500);
            
        } catch (error) {
            console.error('登入失敗:', error);
            this.showError(error.message || '登入失敗，請檢查您的帳號密碼');
        } finally {
            this.setLoading(false);
        }
    }

    /**
     * 設置載入狀態
     */
    setLoading(isLoading) {
        if (this.loginButton) {
            if (isLoading) {
                this.loginButton.disabled = true;
                this.loginButton.innerHTML = `
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    登入中...
                `;
            } else {
                this.loginButton.disabled = false;
                this.loginButton.innerHTML = '登入';
            }
        }
    }

    /**
     * 顯示錯誤訊息
     */
    showError(message) {
        // 移除舊的錯誤訊息
        this.clearError();
        
        // 創建錯誤訊息元素
        const errorDiv = document.createElement('div');
        errorDiv.id = 'loginError';
        errorDiv.className = 'mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded';
        errorDiv.textContent = message;
        
        // 插入到表單前面
        if (this.form) {
            this.form.insertBefore(errorDiv, this.form.firstChild);
        }
    }

    /**
     * 顯示成功訊息
     */
    showSuccess(message) {
        // 移除舊的錯誤訊息
        this.clearError();
        
        // 創建成功訊息元素
        const successDiv = document.createElement('div');
        successDiv.id = 'loginSuccess';
        successDiv.className = 'mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded';
        successDiv.textContent = message;
        
        // 插入到表單前面
        if (this.form) {
            this.form.insertBefore(successDiv, this.form.firstChild);
        }
    }

    /**
     * 清除錯誤訊息
     */
    clearError() {
        const errorDiv = document.getElementById('loginError');
        const successDiv = document.getElementById('loginSuccess');
        
        if (errorDiv) {
            errorDiv.remove();
        }
        
        if (successDiv) {
            successDiv.remove();
        }
    }

    /**
     * 顯示欄位錯誤
     */
    showFieldError(inputElement, message) {
        this.clearFieldError(inputElement);
        
        const errorSpan = document.createElement('span');
        errorSpan.className = 'field-error text-red-500 text-sm mt-1 block';
        errorSpan.textContent = message;
        
        inputElement.classList.add('border-red-500');
        inputElement.parentNode.appendChild(errorSpan);
    }

    /**
     * 清除欄位錯誤
     */
    clearFieldError(inputElement) {
        inputElement.classList.remove('border-red-500');
        const errorSpan = inputElement.parentNode.querySelector('.field-error');
        if (errorSpan) {
            errorSpan.remove();
        }
    }

    /**
     * 更新認證 UI
     */
    updateAuthUI() {
        const userInfo = document.getElementById('userInfo');
        const authButtons = document.getElementById('authButtons');
        const userName = document.getElementById('userName');
        const logoutBtn = document.getElementById('logoutBtn');

        // 檢查是否有登入狀態
        const token = localStorage.getItem('auth_token') || localStorage.getItem('inulearning_token');
        const userStr = localStorage.getItem('user_info') || localStorage.getItem('inulearning_user');
        
        if (token && userStr) {
            try {
                const user = JSON.parse(userStr);
                
                // 顯示用戶資訊
                if (userInfo) {
                    userInfo.classList.remove('hidden');
                }
                
                if (userName) {
                    userName.textContent = user.email || '用戶';
                }
                
                // 隱藏登入按鈕
                if (authButtons) {
                    authButtons.classList.add('hidden');
                }
                
                // 顯示登出按鈕
                if (logoutBtn) {
                    logoutBtn.classList.remove('hidden');
                }
            } catch (error) {
                console.error('解析用戶資訊失敗:', error);
            }
        } else {
            // 隱藏用戶資訊
            if (userInfo) {
                userInfo.classList.add('hidden');
            }
            
            // 顯示登入按鈕
            if (authButtons) {
                authButtons.classList.remove('hidden');
            }
            
            // 隱藏登出按鈕
            if (logoutBtn) {
                logoutBtn.classList.add('hidden');
            }
        }
    }

    /**
     * 根據用戶角色進行跳轉
     */
    redirectByRole(role) {
        console.log('根據角色跳轉:', role);
        
        // 角色對應的前端應用端口
        const roleRedirectMap = {
            'student': 'http://localhost:8080',           // 學生前端
            'parent': 'http://localhost:8082',            // 家長前端  
            'teacher': 'http://localhost:8083',           // 教師前端
            'admin': 'http://localhost:8081',             // 管理員前端
            'manager': 'http://localhost:8081'            // 管理員前端 (別名)
        };
        
        const targetURL = roleRedirectMap[role];
        
        if (targetURL) {
            console.log('跳轉到:', targetURL);
            setTimeout(() => {
                window.location.href = targetURL;
            }, 1000);
        } else {
            console.error('未知的用戶角色:', role);
            this.showError('未知的用戶角色，請聯繫系統管理員');
        }
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
    new LoginPage();
}); 