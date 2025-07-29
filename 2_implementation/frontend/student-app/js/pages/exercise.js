/**
 * 練習選擇頁面 JavaScript
 * 實現智慧出題引擎功能
 */

// 練習頁面管理器
class ExerciseManager {
    constructor() {
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.sessionId = null;
        this.startTime = null;
        this.isSubmitted = false;
        this.selectedCriteria = {};
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializePage();
    }

    initializePage() {
        // 初始化頁面，顯示設置區域
        const setupDiv = document.getElementById('exerciseSetup');
        if (setupDiv) {
            setupDiv.classList.remove('hidden');
        }
        
        // 初始化默認值
        const questionCountSelect = document.getElementById('questionCountSelect');
        if (questionCountSelect) {
            questionCountSelect.value = '5';
        }
    }

    bindEvents() {
        // 載入題目按鈕
        const loadBtn = document.getElementById('loadQuestionsBtn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadQuestionsByConditions());
        }

        // 開始練習按鈕
        const startBtn = document.getElementById('startExerciseBtn');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startExercise());
        }

        // 選項選擇事件
        document.addEventListener('change', (e) => {
            if (e.target.name === 'answer') {
                this.selectAnswer(e.target.value);
            }
        });

        // 導航按鈕
        const prevBtn = document.getElementById('prevQuestionBtn');
        const nextBtn = document.getElementById('nextQuestionBtn');
        
        if (prevBtn) prevBtn.addEventListener('click', () => this.previousQuestion());
        if (nextBtn) nextBtn.addEventListener('click', () => this.nextQuestion());

        // 提交按鈕
        const submitBtn = document.getElementById('submitExerciseBtn');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitExercise());
        }

        // 重新開始按鈕
        const restartBtn = document.getElementById('restartExerciseBtn');
        if (restartBtn) {
            restartBtn.addEventListener('click', () => this.restartExercise());
        }
    }

    getSelectedCriteria() {
        const subject = document.getElementById('subjectSelect')?.value || '';
        const grade = document.getElementById('gradeSelect')?.value || '';
        const difficulty = document.getElementById('difficultySelect')?.value || '';
        const questionCount = parseInt(document.getElementById('questionCountSelect')?.value || '5');

        return {
            subject,
            grade,
            difficulty,
            question_count: questionCount
        };
    }

    async loadQuestionsByConditions() {
        try {
            this.showLoading('正在載入題目...');
            
            this.selectedCriteria = this.getSelectedCriteria();
            
            // 檢查是否至少選擇了科目
            if (!this.selectedCriteria.subject) {
                this.showError('請至少選擇一個科目');
                return;
            }

            // 獲取符合條件的題目
            const result = await learningAPI.getRandomQuestions(
                this.selectedCriteria.question_count,
                {
                    subject: this.selectedCriteria.subject,
                    grade: this.selectedCriteria.grade,
                    difficulty: this.selectedCriteria.difficulty
                }
            );

            if (result.success && result.data && result.data.length > 0) {
                this.questions = result.data;
                this.displayQuestionsInfo();
                this.enableStartButton();
            } else {
                // 沒有符合條件的題目
                this.showNoQuestionsFound();
            }
        } catch (error) {
            console.error('載入題目失敗:', error);
            this.showError('載入題目失敗，請重新嘗試');
        } finally {
            this.hideLoading();
        }
    }

    showNoQuestionsFound() {
        const questionsInfo = document.getElementById('questionsInfo');
        if (questionsInfo) {
            questionsInfo.innerHTML = `
                <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div class="flex items-center">
                        <svg class="w-5 h-5 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                        </svg>
                        <div>
                            <h4 class="text-yellow-800 font-medium">找不到符合條件的題目</h4>
                            <p class="text-yellow-700 text-sm mt-1">
                                請嘗試調整篩選條件，或選擇其他科目/難度組合
                            </p>
                        </div>
                    </div>
                </div>
            `;
        }
        this.disableStartButton();
    }

    displayQuestionsInfo() {
        const questionsInfo = document.getElementById('questionsInfo');
        if (questionsInfo) {
            questionsInfo.innerHTML = `
                <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div class="flex items-center">
                        <svg class="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                        </svg>
                        <div>
                            <h4 class="text-green-800 font-medium">題目載入成功！</h4>
                            <div class="text-green-700 text-sm mt-1 space-y-1">
                                <p>科目: ${this.selectedCriteria.subject}</p>
                                ${this.selectedCriteria.grade ? `<p>年級: ${this.getGradeDisplayName(this.selectedCriteria.grade)}</p>` : ''}
                                ${this.selectedCriteria.difficulty ? `<p>難度: ${this.getDifficultyDisplayName(this.selectedCriteria.difficulty)}</p>` : ''}
                                <p>題目數量: ${this.questions.length} 題</p>
                                <p>預估時間: ${this.questions.length * 2} 分鐘</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    getGradeDisplayName(grade) {
        const gradeMap = {
            '7A': '國一',
            '7B': '國二', 
            '7C': '國三'
        };
        return gradeMap[grade] || grade;
    }

    getDifficultyDisplayName(difficulty) {
        const difficultyMap = {
            'easy': '簡單',
            'normal': '中等',
            'hard': '困難'
        };
        return difficultyMap[difficulty] || difficulty;
    }

    enableStartButton() {
        const startBtn = document.getElementById('startExerciseBtn');
        if (startBtn) {
            startBtn.disabled = false;
            startBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    disableStartButton() {
        const startBtn = document.getElementById('startExerciseBtn');
        if (startBtn) {
            startBtn.disabled = true;
            startBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    async startExercise() {
        try {
            this.showLoading('正在準備練習...');
            
            // 創建學習會話
            const sessionResult = await learningAPI.createLearningSession({
                session_type: 'exercise',
                question_count: this.questions.length,
                subject: this.selectedCriteria.subject,
                grade: this.selectedCriteria.grade,
                difficulty: this.selectedCriteria.difficulty
            });

            if (sessionResult.success) {
                this.sessionId = sessionResult.data.id;
                this.startTime = new Date();
                this.showExerciseInterface();
                this.displayQuestion();
            } else {
                throw new Error(sessionResult.error || '創建學習會話失敗');
            }
        } catch (error) {
            console.error('開始練習失敗:', error);
            this.showError('開始練習失敗，請稍後再試');
        } finally {
            this.hideLoading();
        }
    }

    showExerciseInterface() {
        const setupDiv = document.getElementById('exerciseSetup');
        const interfaceDiv = document.getElementById('exerciseInterface');
        
        if (setupDiv) setupDiv.classList.add('hidden');
        if (interfaceDiv) interfaceDiv.classList.remove('hidden');
        
        this.updateProgress();
    }

    displayQuestion() {
        const question = this.questions[this.currentQuestionIndex];
        if (!question) return;

        const questionContainer = document.getElementById('questionContainer');
        if (!questionContainer) return;

        // 處理選項格式
        let optionsArray = [];
        if (Array.isArray(question.options)) {
            optionsArray = question.options;
        } else if (typeof question.options === 'object') {
            optionsArray = Object.entries(question.options).map(([key, value]) => `${key}. ${value}`);
        } else {
            console.error('Invalid options format:', question.options);
            optionsArray = ['選項格式錯誤'];
        }

        questionContainer.innerHTML = `
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="mb-4">
                    <span class="text-sm text-gray-500">題目 ${this.currentQuestionIndex + 1} / ${this.questions.length}</span>
                </div>
                
                <h3 class="text-lg font-semibold mb-4">${question.question || question.content}</h3>
                
                <div class="space-y-3">
                    ${optionsArray.map((option, index) => {
                        const optionKey = String.fromCharCode(65 + index);
                        const isSelected = this.userAnswers[question.id] === optionKey;
                        return `
                            <label class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${isSelected ? 'bg-blue-50 border-blue-300' : 'border-gray-200'}">
                                <input type="radio" name="answer" value="${optionKey}" class="mr-3" ${isSelected ? 'checked' : ''}>
                                <span>${option}</span>
                            </label>
                        `;
                    }).join('')}
                </div>
            </div>
        `;

        this.updateNavigationButtons();
    }

    selectAnswer(answer) {
        const question = this.questions[this.currentQuestionIndex];
        this.userAnswers[question.id] = answer;
        this.updateProgress();
    }

    previousQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.currentQuestionIndex--;
            this.displayQuestion();
        }
    }

    nextQuestion() {
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.currentQuestionIndex++;
            this.displayQuestion();
        }
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevQuestionBtn');
        const nextBtn = document.getElementById('nextQuestionBtn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentQuestionIndex === 0;
        }
        
        if (nextBtn) {
            nextBtn.disabled = this.currentQuestionIndex === this.questions.length - 1;
        }
    }

    updateProgress() {
        const progressBar = document.getElementById('exerciseProgress');
        const progressText = document.getElementById('progressText');
        
        const answeredCount = Object.keys(this.userAnswers).length;
        const progress = (answeredCount / this.questions.length) * 100;
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        if (progressText) {
            progressText.textContent = `已完成 ${answeredCount} / ${this.questions.length} 題`;
        }

        // 更新提交按鈕狀態
        const submitBtn = document.getElementById('submitExerciseBtn');
        if (submitBtn) {
            submitBtn.disabled = answeredCount < this.questions.length;
            submitBtn.classList.toggle('opacity-50', answeredCount < this.questions.length);
        }
    }

    async submitExercise() {
        if (this.isSubmitted) return;

        try {
            this.showLoading('正在批改答案...');
            this.isSubmitted = true;

            // 準備答案數據
            const answers = this.questions.map(question => ({
                question_id: question.id,
                user_answer: this.userAnswers[question.id] || '',
                correct_answer: question.answer
            }));

            // 提交答案
            const result = await learningAPI.submitAnswers(this.sessionId, {
                answers: answers,
                completed_at: new Date().toISOString()
            });

            if (result.success) {
                this.showResults(result.data);
            } else {
                throw new Error(result.error || '提交答案失敗');
            }
        } catch (error) {
            console.error('提交答案失敗:', error);
            this.showError('提交答案失敗，請稍後再試');
            this.isSubmitted = false;
        } finally {
            this.hideLoading();
        }
    }

    showResults(results) {
        const interfaceDiv = document.getElementById('exerciseInterface');
        const resultsDiv = document.getElementById('exerciseResults');
        
        if (interfaceDiv) interfaceDiv.classList.add('hidden');
        if (resultsDiv) resultsDiv.classList.remove('hidden');

        const endTime = new Date();
        const timeSpent = Math.round((endTime - this.startTime) / 1000 / 60); // 分鐘

        // 計算結果統計
        let correctCount = 0;
        this.questions.forEach(question => {
            const userAnswer = this.userAnswers[question.id];
            const correctAnswer = question.answer;
            if (userAnswer === correctAnswer) {
                correctCount++;
            }
        });

        const accuracy = Math.round((correctCount / this.questions.length) * 100);
        const totalScore = Math.round((correctCount / this.questions.length) * 100);

        const resultsContainer = document.getElementById('resultsContainer');
        if (!resultsContainer) return;

        resultsContainer.innerHTML = `
            <div class="bg-white rounded-lg shadow-md p-6 mb-6">
                <h3 class="text-2xl font-bold text-center mb-6">練習完成！</h3>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div class="text-center p-4 bg-blue-50 rounded-lg">
                        <div class="text-2xl font-bold text-blue-600">${totalScore}</div>
                        <div class="text-sm text-gray-600">總分</div>
                    </div>
                    <div class="text-center p-4 bg-green-50 rounded-lg">
                        <div class="text-2xl font-bold text-green-600">${accuracy}%</div>
                        <div class="text-sm text-gray-600">正確率</div>
                    </div>
                    <div class="text-center p-4 bg-purple-50 rounded-lg">
                        <div class="text-2xl font-bold text-purple-600">${timeSpent}</div>
                        <div class="text-sm text-gray-600">用時(分鐘)</div>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow-md p-6">
                <h4 class="text-lg font-semibold mb-4">詳細結果</h4>
                <div class="space-y-4">
                    ${this.questions.map((question, index) => {
                        const userAnswer = this.userAnswers[question.id];
                        const correctAnswer = question.answer;
                        const isCorrect = userAnswer === correctAnswer;
                        
                        return `
                            <div class="border rounded-lg p-4 ${isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}">
                                <div class="flex items-center mb-2">
                                    <span class="font-semibold">題目 ${index + 1}</span>
                                    <span class="ml-2 px-2 py-1 rounded text-sm ${isCorrect ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}">
                                        ${isCorrect ? '✓ 正確' : '✗ 錯誤'}
                                    </span>
                                </div>
                                <p class="mb-2">${question.question || question.content}</p>
                                <div class="text-sm">
                                    <p>您的答案: <span class="font-semibold">${userAnswer || '未作答'}</span></p>
                                    <p>正確答案: <span class="font-semibold text-green-600">${correctAnswer}</span></p>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    restartExercise() {
        // 重置狀態
        this.questions = [];
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.sessionId = null;
        this.startTime = null;
        this.isSubmitted = false;
        this.selectedCriteria = {};

        // 隱藏結果頁面
        const resultsDiv = document.getElementById('exerciseResults');
        if (resultsDiv) resultsDiv.classList.add('hidden');

        // 顯示設置頁面
        const setupDiv = document.getElementById('exerciseSetup');
        if (setupDiv) setupDiv.classList.remove('hidden');

        // 清空題目資訊
        const questionsInfo = document.getElementById('questionsInfo');
        if (questionsInfo) {
            questionsInfo.innerHTML = '';
        }

        // 重置按鈕狀態
        this.disableStartButton();
    }

    showLoading(message = '載入中...') {
        const loadingDiv = document.getElementById('loadingMessage');
        if (loadingDiv) {
            const loadingContent = loadingDiv.querySelector('.inline-flex');
            if (loadingContent) {
                loadingContent.lastChild.textContent = message;
            }
            loadingDiv.classList.remove('hidden');
        }
    }

    hideLoading() {
        const loadingDiv = document.getElementById('loadingMessage');
        if (loadingDiv) {
            loadingDiv.classList.add('hidden');
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
            
            // 5秒後自動隱藏
            setTimeout(() => {
                errorDiv.classList.add('hidden');
            }, 5000);
        }
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
    // 確保authManager已初始化
    if (typeof authManager !== 'undefined') {
        authManager.init();
    }
    
    window.exerciseManager = new ExerciseManager();
});