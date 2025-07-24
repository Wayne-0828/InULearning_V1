/**
 * 題庫 API 函數
 * 整合 question-bank-service 的 API 呼叫
 */

class QuestionBankAPI {
    constructor() {
        this.baseURL = 'http://localhost:8003'; // question-bank-service 的預設端口
    }

    /**
     * 根據條件獲取題目
     */
    async getQuestionsByCriteria(criteria) {
        try {
            const queryParams = new URLSearchParams(criteria).toString();
            const response = await fetch(`${this.baseURL}/api/v1/questions/criteria/?${queryParams}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取題目失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取題目錯誤:', error);
            throw error;
        }
    }

    /**
     * 隨機獲取題目
     */
    async getRandomQuestions(count = 10, criteria = {}) {
        try {
            const queryParams = new URLSearchParams({
                count: count,
                ...criteria
            }).toString();
            
            const response = await fetch(`${this.baseURL}/api/v1/questions/random/?${queryParams}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取隨機題目失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取隨機題目錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取特定題目詳情
     */
    async getQuestion(questionId) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/questions/${questionId}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取題目詳情失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取題目詳情錯誤:', error);
            throw error;
        }
    }

    /**
     * 搜尋題目
     */
    async searchQuestions(searchParams) {
        try {
            const queryParams = new URLSearchParams(searchParams).toString();
            const response = await fetch(`${this.baseURL}/api/v1/questions/?${queryParams}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '搜尋題目失敗');
            }

            return data;
        } catch (error) {
            console.error('搜尋題目錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取章節列表
     */
    async getChapters(filters = {}) {
        try {
            const queryParams = new URLSearchParams(filters).toString();
            const response = await fetch(`${this.baseURL}/api/v1/chapters/?${queryParams}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取章節列表失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取章節列表錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取知識點列表
     */
    async getKnowledgePoints(filters = {}) {
        try {
            const queryParams = new URLSearchParams(filters).toString();
            const response = await fetch(`${this.baseURL}/api/v1/knowledge-points/?${queryParams}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取知識點列表失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取知識點列表錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取題目統計
     */
    async getQuestionStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/questions/stats/`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取題目統計失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取題目統計錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取科目列表
     */
    async getSubjects() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/subjects/`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取科目列表失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取科目列表錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取版本列表
     */
    async getEditions() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/editions/`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取版本列表失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取版本列表錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取年級列表
     */
    async getGrades() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/grades/`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取年級列表失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取年級列表錯誤:', error);
            throw error;
        }
    }

    /**
     * 根據章節獲取題目數量
     */
    async getQuestionCountByChapter(chapterId) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/chapters/${chapterId}/question-count`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取題目數量失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取題目數量錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取題目難度分布
     */
    async getDifficultyDistribution(criteria = {}) {
        try {
            const queryParams = new URLSearchParams(criteria).toString();
            const response = await fetch(`${this.baseURL}/api/v1/questions/difficulty-distribution/?${queryParams}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取難度分布失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取難度分布錯誤:', error);
            throw error;
        }
    }
}

// 創建全域題庫 API 實例
const questionBankAPI = new QuestionBankAPI();

// 導出題庫 API
window.questionBankAPI = questionBankAPI; 