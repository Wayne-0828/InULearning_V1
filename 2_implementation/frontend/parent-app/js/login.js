/**
 * 家長登入頁面模組
 * 處理登入表單、驗證和快速登入功能
 */
class ParentLogin {
    constructor() {
        this.form = null;
        this.emailInput = null;
        this.passwordInput = null;
        this.passwordToggle = null;
        this.loginBtn = null;
        this.rememberMeCheckbox = null;
        
        this.init();
    }

    init() {
        this.setupElements();
        this.bindEvents();
        this.checkRememberedCredentials();
    }

    setupElements() {
        this.form = document.getElementById('loginForm');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.passwordToggle = document.getElementById('passwordToggle');
        this.loginBtn = document.getElementById('loginBtn');
        this.rememberMeCheckbox = document.getElementById('rememberMe');
    }

    bindEvents() {
        // 表單提交事件
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // 密碼顯示/隱藏切換
        this.passwordToggle.addEventListener('click', () => {
            this.togglePasswordVisibility();
        });

        // 快速登入按鈕
        document.addEventListener('click', (e) => {
            if (e.target.matches('.quick-btn')) {
                this.handleQuickLogin(e.target);
            }
        });

        // 忘記密碼連結
        document.addEventListener('click', (e) => {
            if (e.target.matches('.forgot-password')) {
                e.preventDefault();
                this.handleForgotPassword();
            }
        });

        // 註冊連結
        document.addEventListener('click', (e) => {
            if (e.target.matches('.register-link')) {
                e.preventDefault();
                this.handleRegister();
            }
        });

        // 輸入框驗證
        this.emailInput.addEventListener('blur', () => {
            this.validateEmail();
        });

        this.passwordInput.addEventListener('blur', () => {
            this.validatePassword();
        });

        // 鍵盤快捷鍵
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !this.loginBtn.disabled) {
                this.handleLogin();
            }
        });
    }

    async handleLogin() {
        // 驗證表單
        if (!this.validateForm()) {
            return;
        }

        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;
        const rememberMe = this.rememberMeCheckbox.checked;

        try {
            // 顯示載入狀態
            this.setLoadingState(true);
            this.clearErrors();

            // 執行登入
            const success = await parentAuth.login(email, password, rememberMe);

            if (success) {
                // 記住憑證（如果選擇）
                if (rememberMe) {
                    this.rememberCredentials(email, password);
                } else {
                    this.clearRememberedCredentials();
                }

                // 顯示成功訊息
                this.showSuccessMessage('登入成功！正在跳轉...');

                // 延遲跳轉到儀表板
                setTimeout(() => {
                    window.location.href = '../index.html';
                }, 1000);
            } else {
                this.showErrorMessage('登入失敗，請檢查您的電子郵件和密碼');
            }
        } catch (error) {
            console.error('登入錯誤:', error);
            this.showErrorMessage('登入時發生錯誤，請稍後重試');
        } finally {
            this.setLoadingState(false);
        }
    }

    handleQuickLogin(button) {
        const email = button.dataset.email;
        const password = button.dataset.password;

        this.emailInput.value = email;
        this.passwordInput.value = password;
        this.rememberMeCheckbox.checked = true;

        // 觸發登入
        this.handleLogin();
    }

    handleForgotPassword() {
        // 顯示忘記密碼對話框或跳轉到忘記密碼頁面
        this.showNotification('忘記密碼功能正在開發中，請聯絡學校管理員', 'info');
    }

    handleRegister() {
        // 顯示註冊說明
        this.showNotification('家長帳號需要透過學校管理員註冊，請聯絡學校', 'info');
    }

    validateForm() {
        const isEmailValid = this.validateEmail();
        const isPasswordValid = this.validatePassword();

        return isEmailValid && isPasswordValid;
    }

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

    validatePassword() {
        const password = this.passwordInput.value;

        if (!password) {
            this.showFieldError(this.passwordInput, '請輸入密碼');
            return false;
        }

        if (password.length < 6) {
            this.showFieldError(this.passwordInput, '密碼至少需要6個字元');
            return false;
        }

        this.clearFieldError(this.passwordInput);
        return true;
    }

    showFieldError(input, message) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.add('error');

        // 移除現有的錯誤訊息
        const existingError = formGroup.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // 添加新的錯誤訊息
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.innerHTML = `<i class="fas fa-exclamation-circle"></i>${message}`;
        formGroup.appendChild(errorMessage);
    }

    clearFieldError(input) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.remove('error');

        const errorMessage = formGroup.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    clearErrors() {
        document.querySelectorAll('.form-group.error').forEach(group => {
            group.classList.remove('error');
            const errorMessage = group.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.remove();
            }
        });
    }

    togglePasswordVisibility() {
        const type = this.passwordInput.type === 'password' ? 'text' : 'password';
        this.passwordInput.type = type;
        
        const icon = this.passwordToggle.querySelector('i');
        icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
    }

    setLoadingState(loading) {
        const btnText = this.loginBtn.querySelector('.btn-text');
        const btnLoading = this.loginBtn.querySelector('.btn-loading');

        if (loading) {
            this.loginBtn.disabled = true;
            this.loginBtn.classList.add('loading');
            btnText.style.display = 'none';
            btnLoading.style.display = 'flex';
        } else {
            this.loginBtn.disabled = false;
            this.loginBtn.classList.remove('loading');
            btnText.style.display = 'block';
            btnLoading.style.display = 'none';
        }
    }

    showSuccessMessage(message) {
        this.showNotification(message, 'success');
    }

    showErrorMessage(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // 創建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // 添加樣式
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;

        // 添加到頁面
        document.body.appendChild(notification);

        // 關閉按鈕事件
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });

        // 自動關閉
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    getNotificationColor(type) {
        const colors = {
            success: '#27ae60',
            error: '#e74c3c',
            warning: '#f39c12',
            info: '#3498db'
        };
        return colors[type] || colors.info;
    }

    rememberCredentials(email, password) {
        try {
            localStorage.setItem('parent_remembered_email', email);
            localStorage.setItem('parent_remembered_password', btoa(password)); // 簡單編碼
        } catch (error) {
            console.error('無法儲存記住的憑證:', error);
        }
    }

    clearRememberedCredentials() {
        try {
            localStorage.removeItem('parent_remembered_email');
            localStorage.removeItem('parent_remembered_password');
        } catch (error) {
            console.error('無法清除記住的憑證:', error);
        }
    }

    checkRememberedCredentials() {
        try {
            const rememberedEmail = localStorage.getItem('parent_remembered_email');
            const rememberedPassword = localStorage.getItem('parent_remembered_password');

            if (rememberedEmail && rememberedPassword) {
                this.emailInput.value = rememberedEmail;
                this.passwordInput.value = atob(rememberedPassword); // 解碼
                this.rememberMeCheckbox.checked = true;
            }
        } catch (error) {
            console.error('無法讀取記住的憑證:', error);
        }
    }
}

// 添加動畫樣式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0.25rem;
        opacity: 0.7;
        transition: opacity 0.3s ease;
    }
    
    .notification-close:hover {
        opacity: 1;
    }
`;
document.head.appendChild(style);

// 初始化登入模組
const parentLogin = new ParentLogin();
window.parentLogin = parentLogin; 