/**
 * 學習 API 函數
 * 整合 learning-service 的 API 呼叫
 */

// 學習相關 API 客戶端
class LearningAPI {
    constructor() {
        this.baseURL = '/api/v1/learning';
        this.questionBankURL = '/api/v1/questions';
    }

    // 獲取認證頭
    getAuthHeaders() {
        const token = localStorage.getItem('auth_token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    // 檢查題庫數量
    async checkQuestionBank(conditions) {
        try {
            // 構建查詢參數
            const params = new URLSearchParams();
            if (conditions.grade) params.append('grade', conditions.grade);
            if (conditions.edition) params.append('edition', conditions.edition);
            if (conditions.subject) params.append('subject', conditions.subject);
            if (conditions.chapter) params.append('chapter', conditions.chapter);

            const response = await fetch(`${this.questionBankURL}/check?${params}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('檢查題庫失敗:', error);
            return {
                success: false,
                error: error.message,
                data: { count: 0, available: false }
            };
        }
    }

    // 根據條件獲取題目
    async getQuestionsByConditions(conditions) {
        try {
            // 構建查詢參數
            const params = new URLSearchParams();
            if (conditions.grade) params.append('grade', conditions.grade);
            if (conditions.edition) params.append('edition', conditions.edition);
            if (conditions.subject) params.append('subject', conditions.subject);
            if (conditions.chapter) params.append('chapter', conditions.chapter);
            if (conditions.questionCount) params.append('questionCount', conditions.questionCount);

            const response = await fetch(`${this.questionBankURL}/by-conditions?${params}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('獲取題目失敗:', error);
            return {
                success: false,
                error: error.message,
                data: []
            };
        }
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

    // 提交完整的練習結果（包含PostgreSQL記錄）
    async submitExerciseResult(resultData) {
        try {
            const response = await fetch(`${this.baseURL}/exercises/complete`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(resultData)
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
            console.error('提交練習結果失敗:', error);
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