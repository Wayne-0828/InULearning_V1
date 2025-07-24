/**
 * 登入頁面 JavaScript
 */

class LoginPage {
    constructor() {
        this.form = document.getElementById('loginForm');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.loginButton = document.querySelector('button[type="submit"]');
        this.loginButtonText = document.getElementById('loginButtonText');
        this.loginSpinner = document.getElementById('loginSpinner');
        
        this.init();
    }

    /**
     * 初始化
     */
    init() {
        this.bindEvents();
        this.checkRememberedEmail();
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
        }

        if (this.passwordInput) {
            this.passwordInput.addEventListener('blur', () => {
                this.validatePassword();
            });
        }

        // 即時驗證
        if (this.emailInput) {
            this.emailInput.addEventListener('input', () => {
                this.clearFieldError(this.emailInput);
            });
        }

        if (this.passwordInput) {
            this.passwordInput.addEventListener('input', () => {
                this.clearFieldError(this.passwordInput);
            });
        }
    }

    /**
     * 檢查記住的電子郵件
     */
    checkRememberedEmail() {
        const rememberedEmail = localStorage.getItem('rememberedEmail');
        if (rememberedEmail && this.emailInput) {
            this.emailInput.value = rememberedEmail;
        }
    }

    /**
     * 處理登入
     */
    async handleLogin() {
        if (!this.validateForm()) {
            return;
        }

        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;

        try {
            // 設置載入狀態
            authManager.setLoading(true, this.loginButton, '登入');

            // 呼叫登入 API
            const response = await authAPI.login(email, password);

            // 儲存 token 和用戶資訊
            authManager.setToken(response.access_token);
            authManager.setUser(response.user);

            // 記住電子郵件
            localStorage.setItem('rememberedEmail', email);

            // 顯示成功訊息
            authManager.showSuccess('登入成功！正在導向首頁...');

            // 導向首頁
            setTimeout(() => {
                window.location.href = '../index.html';
            }, 1000);

        } catch (error) {
            console.error('登入失敗:', error);
            
            // 顯示錯誤訊息
            const errorMessage = authManager.handleApiError(error);
            authManager.showError(errorMessage);

            // 清除載入狀態
            authManager.setLoading(false, this.loginButton, '登入');
        }
    }

    /**
     * 驗證表單
     */
    validateForm() {
        let isValid = true;

        // 驗證電子郵件
        if (!this.validateEmail()) {
            isValid = false;
        }

        // 驗證密碼
        if (!this.validatePassword()) {
            isValid = false;
        }

        return isValid;
    }

    /**
     * 驗證電子郵件
     */
    validateEmail() {
        const email = this.emailInput.value.trim();
        
        if (!email) {
            this.showFieldError(this.emailInput, '請輸入電子郵件');
            return false;
        }

        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this.showFieldError(this.emailInput, '請輸入有效的電子郵件格式');
            return false;
        }

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
            this.showFieldError(this.passwordInput, '密碼至少需要 6 個字元');
            return false;
        }

        return true;
    }

    /**
     * 顯示欄位錯誤
     */
    showFieldError(field, message) {
        // 移除現有錯誤樣式
        field.classList.remove('error');
        
        // 添加錯誤樣式
        field.classList.add('error');
        
        // 移除現有錯誤訊息
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // 添加錯誤訊息
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = message;
        field.parentNode.appendChild(errorElement);
    }

    /**
     * 清除欄位錯誤
     */
    clearFieldError(field) {
        field.classList.remove('error');
        
        const errorElement = field.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * 處理 Google 登入
     */
    handleGoogleLogin() {
        // TODO: 實作 Google OAuth 登入
        alert('Google 登入功能即將推出！');
    }

    /**
     * 處理忘記密碼
     */
    async handleForgotPassword() {
        const email = this.emailInput.value.trim();
        
        if (!email) {
            authManager.showError('請先輸入電子郵件');
            return;
        }

        if (!this.validateEmail()) {
            return;
        }

        try {
            await authAPI.forgotPassword(email);
            authManager.showSuccess('密碼重置連結已發送到您的電子郵件');
        } catch (error) {
            console.error('忘記密碼錯誤:', error);
            const errorMessage = authManager.handleApiError(error);
            authManager.showError(errorMessage);
        }
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
    // 如果已經登入，導向首頁
    if (authManager.isLoggedIn()) {
        window.location.href = '../index.html';
        return;
    }

    // 初始化登入頁面
    window.loginPage = new LoginPage();

    // 綁定忘記密碼連結
    const forgotPasswordLink = document.querySelector('a[href="#"]');
    if (forgotPasswordLink && forgotPasswordLink.textContent.includes('忘記密碼')) {
        forgotPasswordLink.addEventListener('click', (e) => {
            e.preventDefault();
            window.loginPage.handleForgotPassword();
        });
    }

    // 綁定 Google 登入按鈕
    const googleLoginButton = document.querySelector('a[href="#"]');
    if (googleLoginButton && googleLoginButton.textContent.includes('Google')) {
        googleLoginButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.loginPage.handleGoogleLogin();
        });
    }
}); 