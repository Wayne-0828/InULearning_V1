/**
 * 考試結果頁面管理
 */
class ResultPage {
    constructor() {
        this.examResults = null;
        this.currentDetailIndex = 0;
    }

    /**
     * 初始化頁面
     */
    async init() {
        try {
            // 從 sessionStorage 載入考試結果
            this.loadExamResults();
            
            // 檢查認證狀態
            this.checkAuthStatus();
            
            // 顯示結果
            this.displayResults();
            
            // 綁定事件
            this.bindEvents();
            
        } catch (error) {
            console.error('初始化結果頁面失敗:', error);
            this.showError('載入結果失敗，請重新進入');
        }
    }

    /**
     * 載入考試結果
     */
    loadExamResults() {
        const resultsData = sessionStorage.getItem('examResults');
        if (!resultsData) {
            throw new Error('找不到考試結果數據');
        }
        
        this.examResults = JSON.parse(resultsData);
        console.log('載入考試結果:', this.examResults);
    }

    /**
     * 檢查認證狀態
     */
    checkAuthStatus() {
        // 檢查 authManager 是否存在
        if (typeof authManager === 'undefined') {
            console.warn('authManager 未定義，跳過認證檢查');
            return;
        }
        
        // 更新認證狀態 UI
        if (typeof authManager.updateAuthUI === 'function') {
            authManager.updateAuthUI();
        }
    }

    /**
     * 顯示考試結果
     */
    displayResults() {
        // 顯示總體分數
        this.displayOverallScore();
        
        // 顯示詳細結果
        this.displayDetailedResults();
        
        // 顯示時間統計
        this.displayTimeStats();
    }

    /**
     * 顯示總體分數
     */
    displayOverallScore() {
        const scoreElement = document.getElementById('overallScore');
        const correctCountElement = document.getElementById('correctCount');
        const totalQuestionsElement = document.getElementById('totalQuestions');
        const wrongCountElement = document.getElementById('wrongCount');

        if (scoreElement) {
            scoreElement.textContent = this.examResults.score;
        }
        
        if (correctCountElement) {
            correctCountElement.textContent = this.examResults.correctAnswers;
        }
        
        if (totalQuestionsElement) {
            totalQuestionsElement.textContent = this.examResults.totalQuestions;
        }
        
        if (wrongCountElement) {
            wrongCountElement.textContent = this.examResults.wrongAnswers;
        }

        // 根據分數設置顏色
        const scoreCard = document.querySelector('.score-card');
        if (scoreCard) {
            if (this.examResults.score >= 80) {
                scoreCard.classList.add('bg-green-50', 'border-green-200');
            } else if (this.examResults.score >= 60) {
                scoreCard.classList.add('bg-yellow-50', 'border-yellow-200');
            } else {
                scoreCard.classList.add('bg-red-50', 'border-red-200');
            }
        }
    }

    /**
     * 顯示詳細結果
     */
    displayDetailedResults() {
        const detailContainer = document.getElementById('detailResults');
        if (!detailContainer || !this.examResults.detailedResults) {
            return;
        }

        let html = '';
        this.examResults.detailedResults.forEach((result, index) => {
            const statusClass = result.isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50';
            const statusIcon = result.isCorrect ? '✅' : '❌';
            
            html += `
                <div class="question-result border-2 ${statusClass} rounded-lg p-4 mb-4">
                    <div class="flex items-start justify-between mb-3">
                        <h3 class="font-semibold text-lg">第 ${index + 1} 題 ${statusIcon}</h3>
                        <span class="text-sm text-gray-500">得分: ${result.isCorrect ? '1' : '0'}/1</span>
                    </div>
                    
                    <div class="question-text mb-4 p-3 bg-white rounded border">
                        <p class="text-gray-800">${result.questionText}</p>
                    </div>

                    <div class="options mb-4">
                        ${result.options.map((option, optIndex) => {
                            let optionClass = 'bg-white border';
                            if (optIndex === result.correctAnswer) {
                                optionClass = 'bg-green-100 border-green-300'; // 正確答案
                            }
                            if (optIndex === result.userAnswer && !result.isCorrect) {
                                optionClass = 'bg-red-100 border-red-300'; // 用戶錯誤答案
                            }
                            if (optIndex === result.userAnswer && result.isCorrect) {
                                optionClass = 'bg-green-100 border-green-300'; // 用戶正確答案
                            }
                            
                            const prefix = String.fromCharCode(65 + optIndex); // A, B, C, D
                            return `
                                <div class="option p-2 rounded mb-2 ${optionClass}">
                                    <span class="font-medium">${prefix}.</span> ${option}
                                    ${optIndex === result.correctAnswer ? ' <span class="text-green-600">(正確答案)</span>' : ''}
                                    ${optIndex === result.userAnswer && !result.isCorrect ? ' <span class="text-red-600">(您的選擇)</span>' : ''}
                                </div>
                            `;
                        }).join('')}
                    </div>

                    <div class="answer-summary mb-3 p-3 bg-gray-50 rounded">
                        <p><strong>您的答案：</strong> ${result.userAnswerText}</p>
                        <p><strong>正確答案：</strong> ${result.correctAnswerText}</p>
                    </div>

                    ${result.explanation ? `
                        <div class="explanation p-3 bg-blue-50 rounded border-l-4 border-blue-400">
                            <h4 class="font-medium text-blue-800 mb-2">詳解：</h4>
                            <p class="text-blue-700">${result.explanation}</p>
                        </div>
                    ` : ''}
                </div>
            `;
        });

        detailContainer.innerHTML = html;
    }

    /**
     * 顯示時間統計
     */
    displayTimeStats() {
        const timeSpentElement = document.getElementById('timeSpent');
        if (timeSpentElement && this.examResults.timeSpent) {
            const minutes = Math.floor(this.examResults.timeSpent / 60);
            const seconds = this.examResults.timeSpent % 60;
            timeSpentElement.textContent = `${minutes}分${seconds}秒`;
        }

        const submittedAtElement = document.getElementById('submittedAt');
        if (submittedAtElement && this.examResults.submittedAt) {
            const date = new Date(this.examResults.submittedAt);
            submittedAtElement.textContent = date.toLocaleString('zh-TW');
        }
    }

    /**
     * 綁定事件
     */
    bindEvents() {
        // 返回練習按鈕
        const backToExerciseBtn = document.getElementById('backToExercise');
        if (backToExerciseBtn) {
            backToExerciseBtn.addEventListener('click', () => {
                window.location.href = '../pages/exercise.html';
            });
        }

        // 重新考試按鈕
        const retakeExamBtn = document.getElementById('retakeExam');
        if (retakeExamBtn) {
            retakeExamBtn.addEventListener('click', () => {
                // 清除當前結果
                sessionStorage.removeItem('examResults');
                // 返回練習頁面
                window.location.href = '../pages/exercise.html';
            });
        }

        // 查看歷史按鈕
        const viewHistoryBtn = document.getElementById('viewHistory');
        if (viewHistoryBtn) {
            viewHistoryBtn.addEventListener('click', () => {
                window.location.href = '../pages/history.html';
            });
        }
    }

    /**
     * 顯示錯誤訊息
     */
    showError(message) {
        const errorElement = document.getElementById('errorMessage');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
        } else {
            alert(message);
        }
    }
}

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', () => {
    const resultPage = new ResultPage();
    resultPage.init();
}); 