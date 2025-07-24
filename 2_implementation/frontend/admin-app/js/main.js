/**
 * 管理員應用程式主要功能 (Admin App Main) - InULearning 個人化學習平台
 * 
 * 功能：
 * - 全域事件處理
 * - 導航管理
 * - 工具函數
 * - 初始化管理
 */

class AdminApp {
    constructor() {
        this.currentPage = this.getCurrentPage();
        this.init();
    }
    
    /**
     * 初始化應用程式
     */
    init() {
        this.setupGlobalEventListeners();
        this.setupNavigation();
        this.setupKeyboardShortcuts();
        this.initializePage();
    }
    
    /**
     * 取得當前頁面
     */
    getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop();
        return filename.replace('.html', '') || 'index';
    }
    
    /**
     * 設定全域事件監聽器
     */
    setupGlobalEventListeners() {
        // 視窗載入完成
        window.addEventListener('load', () => {
            this.onPageLoad();
        });
        
        // 視窗大小改變
        window.addEventListener('resize', () => {
            this.onWindowResize();
        });
        
        // 鍵盤事件
        document.addEventListener('keydown', (e) => {
            this.onKeyDown(e);
        });
        
        // 點擊事件委派
        document.addEventListener('click', (e) => {
            this.onGlobalClick(e);
        });
    }
    
    /**
     * 設定導航
     */
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                this.onNavLinkClick(e, link);
            });
        });
        
        // 更新當前頁面的導航狀態
        this.updateNavigationState();
    }
    
    /**
     * 更新導航狀態
     */
    updateNavigationState() {
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.classList.remove('active');
            
            const href = link.getAttribute('href');
            if (href && href.includes(this.currentPage)) {
                link.classList.add('active');
            }
        });
    }
    
    /**
     * 設定鍵盤快捷鍵
     */
    setupKeyboardShortcuts() {
        // Ctrl + R: 重新整理
        // Ctrl + D: 儀表板
        // Ctrl + U: 用戶管理
        // Ctrl + Q: 題庫管理
        // Ctrl + S: 系統設定
        // Ctrl + L: 登出
    }
    
    /**
     * 初始化頁面
     */
    initializePage() {
        // 根據當前頁面執行特定的初始化
        switch (this.currentPage) {
            case 'index':
                // 主頁面已在 dashboard.js 中處理
                break;
            case 'login':
                this.initializeLoginPage();
                break;
            case 'users':
                this.initializeUsersPage();
                break;
            case 'questions':
                this.initializeQuestionsPage();
                break;
            case 'system':
                this.initializeSystemPage();
                break;
            default:
                console.log(`頁面 ${this.currentPage} 的初始化未定義`);
        }
    }
    
    /**
     * 頁面載入完成
     */
    onPageLoad() {
        // 隱藏載入指示器
        Utils.hideLoading();
        
        // 檢查認證狀態
        if (this.currentPage !== 'login' && !adminAuth.isAuthenticated()) {
            adminAuth.redirectToLogin();
            return;
        }
        
        // 顯示歡迎訊息
        if (this.currentPage === 'index') {
            this.showWelcomeMessage();
        }
    }
    
    /**
     * 視窗大小改變
     */
    onWindowResize() {
        // 處理響應式設計
        this.handleResponsiveLayout();
    }
    
    /**
     * 鍵盤按下事件
     */
    onKeyDown(e) {
        // 檢查是否為快捷鍵
        if (e.ctrlKey) {
            switch (e.key.toLowerCase()) {
                case 'r':
                    e.preventDefault();
                    this.refreshCurrentPage();
                    break;
                case 'd':
                    e.preventDefault();
                    window.location.href = 'pages/dashboard.html';
                    break;
                case 'u':
                    e.preventDefault();
                    window.location.href = 'pages/users.html';
                    break;
                case 'q':
                    e.preventDefault();
                    window.location.href = 'pages/questions.html';
                    break;
                case 's':
                    e.preventDefault();
                    window.location.href = 'pages/system.html';
                    break;
                case 'l':
                    e.preventDefault();
                    adminAuth.logout();
                    break;
            }
        }
    }
    
    /**
     * 全域點擊事件
     */
    onGlobalClick(e) {
        // 處理下拉選單
        if (e.target.closest('.user-dropdown-toggle')) {
            this.toggleUserDropdown();
        }
        
        // 處理模態框關閉
        if (e.target.classList.contains('modal-overlay')) {
            this.closeModal();
        }
        
        // 處理工具提示
        if (e.target.closest('[data-tooltip]')) {
            this.showTooltip(e.target);
        }
    }
    
    /**
     * 導航連結點擊
     */
    onNavLinkClick(e, link) {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('#')) {
            // 更新導航狀態
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        }
    }
    
    /**
     * 處理響應式佈局
     */
    handleResponsiveLayout() {
        const width = window.innerWidth;
        
        if (width <= 768) {
            // 行動裝置佈局
            this.enableMobileLayout();
        } else {
            // 桌面佈局
            this.enableDesktopLayout();
        }
    }
    
    /**
     * 啟用行動裝置佈局
     */
    enableMobileLayout() {
        // 隱藏桌面導航
        const navbarMenu = document.querySelector('.navbar-menu');
        if (navbarMenu) {
            navbarMenu.style.display = 'none';
        }
        
        // 添加行動裝置選單按鈕
        this.addMobileMenuButton();
    }
    
    /**
     * 啟用桌面佈局
     */
    enableDesktopLayout() {
        // 顯示桌面導航
        const navbarMenu = document.querySelector('.navbar-menu');
        if (navbarMenu) {
            navbarMenu.style.display = 'flex';
        }
        
        // 移除行動裝置選單按鈕
        this.removeMobileMenuButton();
    }
    
    /**
     * 添加行動裝置選單按鈕
     */
    addMobileMenuButton() {
        if (!document.getElementById('mobile-menu-btn')) {
            const navbarContainer = document.querySelector('.navbar-container');
            const mobileBtn = document.createElement('button');
            mobileBtn.id = 'mobile-menu-btn';
            mobileBtn.className = 'mobile-menu-btn';
            mobileBtn.innerHTML = '<i class="fas fa-bars"></i>';
            mobileBtn.addEventListener('click', () => this.toggleMobileMenu());
            
            navbarContainer.appendChild(mobileBtn);
        }
    }
    
    /**
     * 移除行動裝置選單按鈕
     */
    removeMobileMenuButton() {
        const mobileBtn = document.getElementById('mobile-menu-btn');
        if (mobileBtn) {
            mobileBtn.remove();
        }
    }
    
    /**
     * 切換行動裝置選單
     */
    toggleMobileMenu() {
        const navbarMenu = document.querySelector('.navbar-menu');
        if (navbarMenu) {
            navbarMenu.classList.toggle('show');
        }
    }
    
    /**
     * 切換用戶下拉選單
     */
    toggleUserDropdown() {
        const dropdown = document.querySelector('.user-dropdown-menu');
        if (dropdown) {
            dropdown.classList.toggle('show');
        }
    }
    
    /**
     * 關閉模態框
     */
    closeModal() {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            modal.classList.remove('show');
        });
    }
    
    /**
     * 顯示工具提示
     */
    showTooltip(element) {
        const tooltip = element.getAttribute('data-tooltip');
        if (tooltip) {
            // 實作工具提示顯示邏輯
            console.log('顯示工具提示:', tooltip);
        }
    }
    
    /**
     * 重新整理當前頁面
     */
    refreshCurrentPage() {
        if (this.currentPage === 'index' && adminDashboard) {
            adminDashboard.refresh();
        } else {
            window.location.reload();
        }
    }
    
    /**
     * 顯示歡迎訊息
     */
    showWelcomeMessage() {
        const user = adminAuth.getCurrentUser();
        if (user) {
            console.log(`歡迎回來，${user.name || user.email}！`);
        }
    }
    
    /**
     * 初始化登入頁面
     */
    initializeLoginPage() {
        // 登入頁面特定初始化
        console.log('初始化登入頁面');
    }
    
    /**
     * 初始化用戶管理頁面
     */
    initializeUsersPage() {
        // 用戶管理頁面特定初始化
        console.log('初始化用戶管理頁面');
    }
    
    /**
     * 初始化題庫管理頁面
     */
    initializeQuestionsPage() {
        // 題庫管理頁面特定初始化
        console.log('初始化題庫管理頁面');
    }
    
    /**
     * 初始化系統設定頁面
     */
    initializeSystemPage() {
        // 系統設定頁面特定初始化
        console.log('初始化系統設定頁面');
    }
    
    /**
     * 取得當前頁面
     */
    getCurrentPageName() {
        return this.currentPage;
    }
    
    /**
     * 導航到指定頁面
     */
    navigateTo(page) {
        window.location.href = `pages/${page}.html`;
    }
    
    /**
     * 顯示通知
     */
    showNotification(message, type = 'info') {
        Utils.showAlert(message, type);
    }
}

// 全域應用程式實例
const adminApp = new AdminApp(); 