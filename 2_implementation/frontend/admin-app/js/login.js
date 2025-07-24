/**
 * 管理員登入頁面功能 (Admin Login) - InULearning 個人化學習平台
 * 
 * 功能：
 * - 登入表單處理
 * - 密碼顯示/隱藏
 * - 快速登入
 * - 表單驗證
 * - 錯誤處理
 */

class AdminLogin {
    constructor() {
        this.form = document.getElementById('login-form');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.passwordToggle = document.getElementById('password-toggle');
        this.rememberMeCheckbox = document.getElementById('remember-me');
        this.forgotPasswordLink = document.getElementById('forgot-password');
        this.quickLoginButtons = document.querySelectorAll('.quick-login-btn');
        
        this.init();
    }
    
    /**
     * 初始化登入頁面
     */
    init() {
        this.setupEventListeners();
        this.loadSavedCredentials();
        this.focusEmailInput();
    }
    
    /**
     * 設定事件監聽器
     */
    setupEventListeners() {
        // 表單提交
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }
        
        // 密碼顯示/隱藏
        if (this.passwordToggle) {
            this.passwordToggle.addEventListener('click', () => {
                this.togglePasswordVisibility();
            });
        }
        
        // 忘記密碼
        if (this.forgotPasswordLink) {
            this.forgotPasswordLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleForgotPassword();
            });
        }
        
        // 快速登入按鈕
        this.quickLoginButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.handleQuickLogin(button);
            });
        });
        
        // 輸入框驗證
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
        
        // 鍵盤快捷鍵
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }
    
    /**
     * 處理登入
     */
    async handleLogin() {
        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;
        const rememberMe = this.rememberMeCheckbox.checked;
        
        // 驗證表單
        if (!this.validateForm(email, password)) {
            return;
        }
        
        try {
            // 顯示載入狀態
            this.setLoadingState(true);
            
            // 呼叫登入 API
            await adminAuth.login(email, password);
            
            // 儲存記住我選項
            if (rememberMe) {
                this.saveCredentials(email, password);
            } else {
                this.clearSavedCredentials();
            }
            
        } catch (error) {
            console.error('登入處理錯誤:', error);
            Utils.showAlert('登入失敗，請檢查您的帳號密碼', 'error');
        } finally {
            this.setLoadingState(false);
        }
    }
    
    /**
     * 驗證表單
     */
    validateForm(email, password) {
        let isValid = true;
        
        // 驗證電子郵件
        if (!this.validateEmail(email)) {
            isValid = false;
        }
        
        // 驗證密碼
        if (!this.validatePassword(password)) {
            isValid = false;
        }
        
        return isValid;
    }
    
    /**
     * 驗證電子郵件
     */
    validateEmail(email = null) {
        const emailToValidate = email || this.emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailToValidate) {
            this.showFieldError(this.emailInput, '請輸入電子郵件');
            return false;
        }
        
        if (!emailRegex.test(emailToValidate)) {
            this.showFieldError(this.emailInput, '請輸入有效的電子郵件格式');
            return false;
        }
        
        this.clearFieldError(this.emailInput);
        return true;
    }
    
    /**
     * 驗證密碼
     */
    validatePassword(password = null) {
        const passwordToValidate = password || this.passwordInput.value;
        
        if (!passwordToValidate) {
            this.showFieldError(this.passwordInput, '請輸入密碼');
            return false;
        }
        
        if (passwordToValidate.length < 6) {
            this.showFieldError(this.passwordInput, '密碼至少需要 6 個字元');
            return false;
        }
        
        this.clearFieldError(this.passwordInput);
        return true;
    }
    
    /**
     * 顯示欄位錯誤
     */
    showFieldError(input, message) {
        input.classList.add('is-invalid');
        
        // 移除現有的錯誤訊息
        const existingError = input.parentNode.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
        
        // 添加新的錯誤訊息
        const errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        errorElement.textContent = message;
        input.parentNode.appendChild(errorElement);
    }
    
    /**
     * 清除欄位錯誤
     */
    clearFieldError(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        
        const errorElement = input.parentNode.querySelector('.form-error');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    /**
     * 切換密碼顯示/隱藏
     */
    togglePasswordVisibility() {
        const type = this.passwordInput.type === 'password' ? 'text' : 'password';
        this.passwordInput.type = type;
        
        const icon = this.passwordToggle.querySelector('i');
        if (type === 'text') {
            icon.className = 'fas fa-eye-slash';
        } else {
            icon.className = 'fas fa-eye';
        }
    }
    
    /**
     * 處理快速登入
     */
    async handleQuickLogin(button) {
        const email = button.dataset.email;
        const password = button.dataset.password;
        
        if (email && password) {
            this.emailInput.value = email;
            this.passwordInput.value = password;
            
            // 自動觸發登入
            await this.handleLogin();
        }
    }
    
    /**
     * 處理忘記密碼
     */
    handleForgotPassword() {
        Utils.showAlert('忘記密碼功能正在開發中，請聯繫系統管理員', 'info');
    }
    
    /**
     * 處理鍵盤快捷鍵
     */
    handleKeyboardShortcuts(e) {
        // Enter 鍵提交表單
        if (e.key === 'Enter' && !e.ctrlKey) {
            if (document.activeElement === this.emailInput) {
                this.passwordInput.focus();
            } else if (document.activeElement === this.passwordInput) {
                this.handleLogin();
            }
        }
        
        // Ctrl + Enter 快速登入
        if (e.ctrlKey && e.key === 'Enter') {
            const quickLoginBtn = this.quickLoginButtons[0];
            if (quickLoginBtn) {
                this.handleQuickLogin(quickLoginBtn);
            }
        }
    }
    
    /**
     * 設定載入狀態
     */
    setLoadingState(loading) {
        const loginBtn = this.form.querySelector('.login-btn');
        
        if (loading) {
            loginBtn.disabled = true;
            loginBtn.classList.add('loading');
            loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 登入中...';
        } else {
            loginBtn.disabled = false;
            loginBtn.classList.remove('loading');
            loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> 登入';
        }
    }
    
    /**
     * 載入儲存的憑證
     */
    loadSavedCredentials() {
        const savedEmail = Utils.getStorageItem('admin_saved_email');
        const savedPassword = Utils.getStorageItem('admin_saved_password');
        
        if (savedEmail && savedPassword) {
            this.emailInput.value = savedEmail;
            this.passwordInput.value = savedPassword;
            this.rememberMeCheckbox.checked = true;
        }
    }
    
    /**
     * 儲存憑證
     */
    saveCredentials(email, password) {
        Utils.setStorageItem('admin_saved_email', email);
        Utils.setStorageItem('admin_saved_password', password);
    }
    
    /**
     * 清除儲存的憑證
     */
    clearSavedCredentials() {
        Utils.removeStorageItem('admin_saved_email');
        Utils.removeStorageItem('admin_saved_password');
    }
    
    /**
     * 聚焦電子郵件輸入框
     */
    focusEmailInput() {
        if (this.emailInput && !this.emailInput.value) {
            this.emailInput.focus();
        }
    }
    
    /**
     * 重置表單
     */
    resetForm() {
        this.form.reset();
        this.clearAllErrors();
        this.focusEmailInput();
    }
    
    /**
     * 清除所有錯誤
     */
    clearAllErrors() {
        const inputs = [this.emailInput, this.passwordInput];
        inputs.forEach(input => {
            if (input) {
                input.classList.remove('is-invalid', 'is-valid');
                const errorElement = input.parentNode.querySelector('.form-error');
                if (errorElement) {
                    errorElement.remove();
                }
            }
        });
    }
    
    /**
     * 顯示成功訊息
     */
    showSuccessMessage(message) {
        Utils.showAlert(message, 'success');
    }
    
    /**
     * 顯示錯誤訊息
     */
    showErrorMessage(message) {
        Utils.showAlert(message, 'error');
    }
}

// 全域登入實例
const adminLogin = new AdminLogin(); 