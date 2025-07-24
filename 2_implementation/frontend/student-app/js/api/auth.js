/**
 * 認證 API 函數
 * 整合 auth-service 的 API 呼叫
 */

class AuthAPI {
    constructor() {
        this.baseURL = 'http://localhost:8001'; // auth-service 的預設端口
    }

    /**
     * 用戶註冊
     */
    async register(userData) {
        try {
            const response = await fetch(`${this.baseURL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '註冊失敗');
            }

            return data;
        } catch (error) {
            console.error('註冊錯誤:', error);
            throw error;
        }
    }

    /**
     * 用戶登入
     */
    async login(email, password) {
        try {
            const response = await fetch(`${this.baseURL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '登入失敗');
            }

            return data;
        } catch (error) {
            console.error('登入錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取用戶資料
     */
    async getUserProfile() {
        try {
            const response = await fetch(`${this.baseURL}/users/profile`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取用戶資料失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取用戶資料錯誤:', error);
            throw error;
        }
    }

    /**
     * 更新用戶資料
     */
    async updateUserProfile(profileData) {
        try {
            const response = await fetch(`${this.baseURL}/users/profile`, {
                method: 'PATCH',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(profileData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '更新用戶資料失敗');
            }

            return data;
        } catch (error) {
            console.error('更新用戶資料錯誤:', error);
            throw error;
        }
    }

    /**
     * 刷新 Token
     */
    async refreshToken() {
        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authManager.getToken()}`
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Token 刷新失敗');
            }

            return data;
        } catch (error) {
            console.error('Token 刷新錯誤:', error);
            throw error;
        }
    }

    /**
     * 登出
     */
    async logout() {
        try {
            const response = await fetch(`${this.baseURL}/auth/logout`, {
                method: 'POST',
                headers: authManager.getAuthHeaders()
            });

            if (!response.ok) {
                console.warn('登出 API 呼叫失敗，但本地登出仍會執行');
            }
        } catch (error) {
            console.error('登出錯誤:', error);
        } finally {
            // 無論 API 是否成功，都執行本地登出
            authManager.logout();
        }
    }

    /**
     * 忘記密碼
     */
    async forgotPassword(email) {
        try {
            const response = await fetch(`${this.baseURL}/auth/forgot-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '密碼重置請求失敗');
            }

            return data;
        } catch (error) {
            console.error('忘記密碼錯誤:', error);
            throw error;
        }
    }

    /**
     * 重置密碼
     */
    async resetPassword(token, newPassword) {
        try {
            const response = await fetch(`${this.baseURL}/auth/reset-password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    token: token,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '密碼重置失敗');
            }

            return data;
        } catch (error) {
            console.error('重置密碼錯誤:', error);
            throw error;
        }
    }

    /**
     * 驗證 Token
     */
    async verifyToken() {
        try {
            const response = await fetch(`${this.baseURL}/auth/verify`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Token 驗證失敗');
            }

            return data;
        } catch (error) {
            console.error('Token 驗證錯誤:', error);
            throw error;
        }
    }
}

// 創建全域認證 API 實例
const authAPI = new AuthAPI();

// 導出認證 API
window.authAPI = authAPI; 