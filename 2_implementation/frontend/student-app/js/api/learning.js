/**
 * 學習 API 函數
 * 整合 learning-service 的 API 呼叫
 */

class LearningAPI {
    constructor() {
        this.baseURL = 'http://localhost:8002'; // learning-service 的預設端口
    }

    /**
     * 創建練習會話
     */
    async createExercise(exerciseData) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/exercises/create`, {
                method: 'POST',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(exerciseData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '創建練習失敗');
            }

            return data;
        } catch (error) {
            console.error('創建練習錯誤:', error);
            throw error;
        }
    }

    /**
     * 提交答案
     */
    async submitAnswer(sessionId, answers) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/exercises/${sessionId}/submit`, {
                method: 'POST',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(answers)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '提交答案失敗');
            }

            return data;
        } catch (error) {
            console.error('提交答案錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取練習會話列表
     */
    async getSessions(page = 1, limit = 10) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/sessions/?page=${page}&limit=${limit}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取會話列表失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取會話列表錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取特定會話詳情
     */
    async getSession(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/sessions/${sessionId}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取會話詳情失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取會話詳情錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習建議
     */
    async getLearningRecommendations() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/recommendations/learning`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取學習建議失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取學習建議錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習趨勢
     */
    async getLearningTrends(userId) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/trends/`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取學習趨勢失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取學習趨勢錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習統計
     */
    async getLearningStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/stats/`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取學習統計失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取學習統計錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習進度
     */
    async getLearningProgress() {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/progress/`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取學習進度失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取學習進度錯誤:', error);
            throw error;
        }
    }

    /**
     * 更新學習進度
     */
    async updateLearningProgress(progressData) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/progress/`, {
                method: 'PUT',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(progressData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '更新學習進度失敗');
            }

            return data;
        } catch (error) {
            console.error('更新學習進度錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取練習記錄
     */
    async getExerciseRecords(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/sessions/${sessionId}/records`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取練習記錄失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取練習記錄錯誤:', error);
            throw error;
        }
    }

    /**
     * 刪除練習會話
     */
    async deleteSession(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/api/v1/learning/sessions/${sessionId}`, {
                method: 'DELETE',
                headers: authManager.getAuthHeaders()
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || '刪除會話失敗');
            }

            return { success: true };
        } catch (error) {
            console.error('刪除會話錯誤:', error);
            throw error;
        }
    }
}

// 創建全域學習 API 實例
const learningAPI = new LearningAPI();

// 導出學習 API
window.learningAPI = learningAPI; 