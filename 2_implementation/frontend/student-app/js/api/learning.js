/**
 * 學習 API 函數
 * 整合 learning-service 的 API 呼叫
 */

// 學習相關 API 客戶端
class LearningAPI {
    constructor() {
        this.baseURL = 'http://localhost:8003/api/v1/learning';
        this.questionBankURL = 'http://localhost:8002/api/v1/questions';
    }

    // 獲取認證頭
    getAuthHeaders() {
        const token = localStorage.getItem('auth_token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    // 獲取隨機題目
    async getRandomQuestions(count = 5, filters = {}) {
        try {
            const params = new URLSearchParams({
                count: count,
                ...filters
            });
            
            const response = await fetch(`${this.questionBankURL}/random?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const questions = await response.json();
            return {
                success: true,
                data: questions
            };
        } catch (error) {
            console.error('獲取題目失敗:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 搜索題目
    async searchQuestions(filters = {}, page = 1, limit = 10) {
        try {
            const params = new URLSearchParams({
                page: page,
                limit: limit,
                ...filters
            });
            
            const response = await fetch(`${this.questionBankURL}/search?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return {
                success: true,
                data: result
            };
        } catch (error) {
            console.error('搜索題目失敗:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 創建學習會話
    async createLearningSession(sessionData) {
        try {
            const response = await fetch(`${this.baseURL}/sessions`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(sessionData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const session = await response.json();
            return {
                success: true,
                data: session
            };
        } catch (error) {
            console.error('創建學習會話失敗:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 提交答案並獲取批改結果
    async submitAnswers(sessionId, answers) {
        try {
            const response = await fetch(`${this.baseURL}/exercises/submit`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    session_id: sessionId,
                    answers: answers
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return {
                success: true,
                data: result
            };
        } catch (error) {
            console.error('提交答案失敗:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 獲取學習記錄
    async getLearningRecords(filters = {}, page = 1, limit = 10) {
        try {
            const params = new URLSearchParams({
                page: page,
                limit: limit,
                ...filters
            });
            
            const response = await fetch(`${this.baseURL}/records?${params}`, {
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const records = await response.json();
            return {
                success: true,
                data: records
            };
        } catch (error) {
            console.error('獲取學習記錄失敗:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 獲取學習統計
    async getLearningStatistics(days = 30) {
        try {
            const params = new URLSearchParams({ days: days });
            
            const response = await fetch(`${this.baseURL}/statistics?${params}`, {
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const statistics = await response.json();
            return {
                success: true,
                data: statistics
            };
        } catch (error) {
            console.error('獲取學習統計失敗:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// 創建全局實例
window.learningAPI = new LearningAPI(); 