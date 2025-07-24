/**
 * AI 分析 API 函數
 * 整合 ai-analysis-service 的 API 呼叫
 */

class AIAnalysisAPI {
    constructor() {
        this.baseURL = 'http://localhost:8004'; // ai-analysis-service 的預設端口
    }

    /**
     * 獲取弱點分析
     */
    async getWeaknessAnalysis(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/learning/sessions/${sessionId}/weakness-analysis`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取弱點分析失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取弱點分析錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習建議
     */
    async getLearningRecommendations() {
        try {
            const response = await fetch(`${this.baseURL}/learning/recommendations`, {
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
     * 獲取學習趨勢分析
     */
    async getLearningTrends(userId) {
        try {
            const response = await fetch(`${this.baseURL}/learning/users/${userId}/trends`, {
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
     * 獲取個人化推薦題目
     */
    async getPersonalizedQuestions(count = 10) {
        try {
            const response = await fetch(`${this.baseURL}/learning/recommendations/questions?count=${count}`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取推薦題目失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取推薦題目錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習進度分析
     */
    async getProgressAnalysis() {
        try {
            const response = await fetch(`${this.baseURL}/learning/progress/analysis`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取進度分析失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取進度分析錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取科目表現分析
     */
    async getSubjectPerformance() {
        try {
            const response = await fetch(`${this.baseURL}/learning/subjects/performance`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取科目表現分析失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取科目表現分析錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習效率分析
     */
    async getEfficiencyAnalysis() {
        try {
            const response = await fetch(`${this.baseURL}/learning/efficiency/analysis`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取效率分析失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取效率分析錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習目標建議
     */
    async getGoalRecommendations() {
        try {
            const response = await fetch(`${this.baseURL}/learning/goals/recommendations`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取目標建議失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取目標建議錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習策略建議
     */
    async getStrategyRecommendations() {
        try {
            const response = await fetch(`${this.baseURL}/learning/strategies/recommendations`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取策略建議失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取策略建議錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取學習時間建議
     */
    async getTimeRecommendations() {
        try {
            const response = await fetch(`${this.baseURL}/learning/time/recommendations`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取時間建議失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取時間建議錯誤:', error);
            throw error;
        }
    }

    /**
     * 獲取綜合學習報告
     */
    async getComprehensiveReport() {
        try {
            const response = await fetch(`${this.baseURL}/learning/reports/comprehensive`, {
                method: 'GET',
                headers: authManager.getAuthHeaders()
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '獲取綜合報告失敗');
            }

            return data;
        } catch (error) {
            console.error('獲取綜合報告錯誤:', error);
            throw error;
        }
    }
}

// 創建全域 AI 分析 API 實例
const aiAnalysisAPI = new AIAnalysisAPI();

// 導出 AI 分析 API
window.aiAnalysisAPI = aiAnalysisAPI; 