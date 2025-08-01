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

        // 更新會話ID顯示
        const sessionIdElement = document.getElementById('sessionId');
        if (sessionIdElement) {
            sessionIdElement.textContent = `RESULT-${Date.now()}`;
        }
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
        
        // 創建題目導航
        this.createQuestionNavigation();
        
        // 顯示第一題詳解
        this.displayQuestionDetail(0);
        
        // 顯示時間統計
        this.displayTimeStats();
        
        // 初始 MathJax 渲染
        this.renderMath();
    }

    /**
     * 顯示總體分數
     */
    displayOverallScore() {
        const totalScoreElement = document.getElementById('totalScore');
        const correctCountElement = document.getElementById('correctCount');
        const accuracyRateElement = document.getElementById('accuracyRate');
        const timeSpentElement = document.getElementById('timeSpent');

        if (totalScoreElement) {
            totalScoreElement.textContent = this.examResults.score || 0;
        }
        
        if (correctCountElement) {
            correctCountElement.textContent = this.examResults.correctAnswers || 0;
        }
        
        if (accuracyRateElement) {
            const accuracy = this.examResults.accuracy || this.examResults.score || 0;
            accuracyRateElement.textContent = `${accuracy}%`;
        }
        
        if (timeSpentElement && this.examResults.timeSpent) {
            const minutes = Math.floor(this.examResults.timeSpent / 60);
            const seconds = this.examResults.timeSpent % 60;
            timeSpentElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    /**
     * 創建題目導航
     */
    createQuestionNavigation() {
        const questionNav = document.getElementById('questionNav');
        if (!questionNav || !this.examResults.detailedResults) {
            return;
        }

        questionNav.innerHTML = '';
        
        this.examResults.detailedResults.forEach((result, index) => {
            const navButton = document.createElement('button');
            navButton.className = `w-10 h-10 rounded-full border-2 text-sm font-medium transition-colors ${
                result.isCorrect 
                    ? 'bg-green-100 border-green-300 text-green-800 hover:bg-green-200' 
                    : 'bg-red-100 border-red-300 text-red-800 hover:bg-red-200'
            }`;
            navButton.textContent = index + 1;
            navButton.addEventListener('click', () => this.displayQuestionDetail(index));
            
            questionNav.appendChild(navButton);
        });
    }

    /**
     * 顯示題目詳解
     */
    displayQuestionDetail(index) {
        if (!this.examResults.detailedResults || index < 0 || index >= this.examResults.detailedResults.length) {
            return;
        }

        this.currentDetailIndex = index;
        const result = this.examResults.detailedResults[index];

        // 更新題目內容
        const questionContent = document.getElementById('currentQuestionContent');
        if (questionContent) {
            let imageHtml = '';
            if (result.image_filename || result.image_url) {
                const imageUrl = result.image_url || `/api/v1/images/${result.image_filename}`;
                imageHtml = `
                    <div class="mb-4 text-center">
                        <img src="${imageUrl}" alt="題目圖片" class="max-w-full h-auto mx-auto rounded-lg shadow-md" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <p class="text-red-500 text-sm mt-2 hidden">圖片載入失敗</p>
                    </div>
                `;
            }

            questionContent.innerHTML = `
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-xl font-bold">第 ${index + 1} 題</h3>
                    <span class="px-3 py-1 rounded-full text-sm font-medium ${
                        result.isCorrect 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                    }">
                        ${result.isCorrect ? '✓ 正確' : '✗ 錯誤'}
                    </span>
                </div>
                ${imageHtml}
                <p class="text-lg text-gray-800">${result.questionText}</p>
            `;
        }

        // 更新選項
        const optionsContainer = document.getElementById('currentOptions');
        if (optionsContainer && result.options) {
            optionsContainer.innerHTML = '';
            
            result.options.forEach((option, optionIndex) => {
                const optionElement = document.createElement('div');
                let optionClass = 'flex items-center p-4 border rounded-lg mb-3';
                
                if (optionIndex === result.correctAnswer) {
                    optionClass += ' bg-green-50 border-green-300';
                } else if (optionIndex === result.userAnswer && !result.isCorrect) {
                    optionClass += ' bg-red-50 border-red-300';
                } else {
                    optionClass += ' bg-gray-50 border-gray-200';
                }
                
                optionElement.className = optionClass;
                
                const optionLetter = String.fromCharCode(65 + optionIndex);
                let statusIcon = '';
                
                if (optionIndex === result.correctAnswer) {
                    statusIcon = '<span class="ml-2 text-green-600 font-medium">(正確答案)</span>';
                } else if (optionIndex === result.userAnswer && !result.isCorrect) {
                    statusIcon = '<span class="ml-2 text-red-600 font-medium">(您的選擇)</span>';
                }
                
                optionElement.innerHTML = `
                    <span class="font-medium text-gray-700 mr-3">${optionLetter}.</span>
                    <span class="flex-1">${option}</span>
                    ${statusIcon}
                `;
                
                optionsContainer.appendChild(optionElement);
            });
        }

        // 更新詳解
        const explanationElement = document.getElementById('explanation');
        if (explanationElement) {
            if (result.explanation && result.explanation !== '暫無解析') {
                explanationElement.innerHTML = `
                    <h4 class="text-lg font-semibold text-green-800 mb-2">詳解：</h4>
                    <p class="text-gray-700">${result.explanation}</p>
                `;
                explanationElement.classList.remove('hidden');
            } else {
                explanationElement.innerHTML = `
                    <h4 class="text-lg font-semibold text-green-800 mb-2">詳解：</h4>
                    <p class="text-gray-700">暫無詳細解析</p>
                `;
            }
        }

        // 更新導航按鈕狀態
        this.updateNavigationButtons();
        
        // 更新題目導航高亮
        this.updateQuestionNavigation();
        
        // 觸發 MathJax 重新渲染
        this.renderMath();
    }

    /**
     * 更新導航按鈕狀態
     */
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevQuestionBtn');
        const nextBtn = document.getElementById('nextQuestionBtn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentDetailIndex === 0;
            prevBtn.classList.toggle('opacity-50', this.currentDetailIndex === 0);
        }
        
        if (nextBtn) {
            const isLast = this.currentDetailIndex === this.examResults.detailedResults.length - 1;
            nextBtn.disabled = isLast;
            nextBtn.classList.toggle('opacity-50', isLast);
        }
    }

    /**
     * 更新題目導航高亮
     */
    updateQuestionNavigation() {
        const questionNav = document.getElementById('questionNav');
        if (!questionNav) return;

        const navButtons = questionNav.querySelectorAll('button');
        navButtons.forEach((button, index) => {
            if (index === this.currentDetailIndex) {
                button.classList.add('ring-2', 'ring-blue-500');
            } else {
                button.classList.remove('ring-2', 'ring-blue-500');
            }
        });
    }

    /**
     * 顯示時間統計
     */
    displayTimeStats() {
        // 時間統計已在 displayOverallScore 中處理
    }

    /**
     * 綁定事件
     */
    bindEvents() {
        // 上一題按鈕
        const prevBtn = document.getElementById('prevQuestionBtn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.currentDetailIndex > 0) {
                    this.displayQuestionDetail(this.currentDetailIndex - 1);
                }
            });
        }

        // 下一題按鈕
        const nextBtn = document.getElementById('nextQuestionBtn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (this.currentDetailIndex < this.examResults.detailedResults.length - 1) {
                    this.displayQuestionDetail(this.currentDetailIndex + 1);
                }
            });
        }

        // 登出按鈕
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                if (typeof authManager !== 'undefined' && authManager.logout) {
                    authManager.logout();
                } else {
                    window.location.href = '../index.html';
                }
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

    /**
     * 觸發 MathJax 重新渲染數學公式
     */
    renderMath() {
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise().then(() => {
                console.log('Result頁面 MathJax 渲染完成');
            }).catch((err) => {
                console.error('Result頁面 MathJax 渲染失敗:', err);
            });
        }
    }
}

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', () => {
    const resultPage = new ResultPage();
    resultPage.init();
}); 