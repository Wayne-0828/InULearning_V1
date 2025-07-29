/**
 * 考試頁面 JavaScript
 * 實現自動批改系統功能
 */

class ExamPage {
    constructor() {
        this.sessionId = this.getSessionIdFromURL();
        this.currentQuestionIndex = 0;
        this.questions = [];
        this.answers = [];
        this.timeRemaining = 0;
        this.timerInterval = null;
        this.startTime = null;
        
        // DOM 元素
        this.questionContainer = document.getElementById('questionContainer');
        this.questionNumber = document.getElementById('questionNumber');
        this.questionText = document.getElementById('questionText');
        this.optionsContainer = document.getElementById('optionsContainer');
        this.prevButton = document.getElementById('prevButton');
        this.nextButton = document.getElementById('nextButton');
        this.submitButton = document.getElementById('submitButton');
        this.timeDisplay = document.getElementById('timeDisplay');
        this.progressBar = document.getElementById('progressBar');
        this.questionNav = document.getElementById('questionNav');
        
        this.init();
    }

    /**
     * 初始化
     */
    async init() {
        try {
            // 暫時跳過認證檢查，允許訪客模式測試
            console.log('暫時跳過認證檢查，允許訪客模式');
            
            // 檢查登入狀態（如果 authManager 存在）
            // if (typeof authManager !== 'undefined' && !authManager.isLoggedIn()) {
            //     window.location.href = '/pages/login.html';
            //     return;
            // }

            // 載入考試會話資料
            await this.loadExamSession();
            
            // 初始化UI
            this.initializeUI();
            
            // 載入第一題
            this.displayQuestion(0);
            
            // 開始計時
            this.startTimer();
            
        } catch (error) {
            console.error('初始化考試失敗:', error);
            this.showError('載入考試失敗，請重新開始');
        }
    }

    /**
     * 從 URL 獲取會話 ID
     */
    getSessionIdFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('session');
    }

    /**
     * 載入考試會話資料
     */
    async loadExamSession() {
        if (!this.sessionId) {
            throw new Error('找不到考試會話ID');
        }

        try {
            // 首先嘗試從 sessionStorage 載入會話資料
            const storedSession = sessionStorage.getItem('currentExerciseSession');
            if (storedSession) {
                const sessionData = JSON.parse(storedSession);
                console.log('從 sessionStorage 載入會話資料:', sessionData);
                
                // 生成模擬題目
                this.questions = await this.generateMockQuestions(sessionData.parameters);
                this.timeRemaining = 3600; // 1小時
                this.answers = new Array(this.questions.length).fill(null);
                this.startTime = new Date();
                
                console.log('模擬考試會話載入成功:', this.questions);
                return;
            }

            // 如果沒有 sessionStorage 資料，嘗試 API 載入
            console.warn('未找到會話資料，生成預設題目');
            this.questions = this.generateDefaultQuestions();
            this.timeRemaining = 3600;
            this.answers = new Array(this.questions.length).fill(null);
            this.startTime = new Date();
            
        } catch (error) {
            console.error('載入考試會話失敗:', error);
            // 生成預設題目作為備案
            this.questions = this.generateDefaultQuestions();
            this.timeRemaining = 3600;
            this.answers = new Array(this.questions.length).fill(null);
            this.startTime = new Date();
        }
    }

    /**
     * 初始化 UI
     */
    initializeUI() {
        // 綁定事件
        this.bindEvents();
        
        // 創建題目導航
        this.createQuestionNavigation();
        
        // 更新進度條
        this.updateProgress();
    }

    /**
     * 綁定事件
     */
    bindEvents() {
        if (this.prevButton) {
            this.prevButton.addEventListener('click', () => this.goToPrevQuestion());
        }

        if (this.nextButton) {
            this.nextButton.addEventListener('click', () => this.goToNextQuestion());
        }

        if (this.submitButton) {
            this.submitButton.addEventListener('click', () => this.showSubmitConfirmation());
        }

        // 防止頁面離開時資料遺失
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        // 自動儲存答案
        setInterval(() => {
            this.autoSaveAnswers();
        }, 30000); // 每30秒自動儲存
    }

    /**
     * 創建題目導航
     */
    createQuestionNavigation() {
        if (!this.questionNav) return;

        this.questionNav.innerHTML = '';
        
        this.questions.forEach((_, index) => {
            const navButton = document.createElement('button');
            navButton.className = 'w-8 h-8 rounded border-2 border-gray-300 text-sm font-medium hover:bg-gray-100 transition-colors';
            navButton.textContent = index + 1;
            navButton.addEventListener('click', () => this.goToQuestion(index));
            
            this.questionNav.appendChild(navButton);
        });
    }

    /**
     * 顯示題目
     */
    displayQuestion(index) {
        if (index < 0 || index >= this.questions.length) {
            return;
        }

        this.currentQuestionIndex = index;
        const question = this.questions[index];

        // 更新題目編號和內容
        if (this.questionNumber) {
            this.questionNumber.textContent = `第 ${index + 1} 題 / 共 ${this.questions.length} 題`;
        }

        if (this.questionText) {
            this.questionText.innerHTML = this.formatQuestionText(question.question_text);
        }

        // 顯示選項
        this.displayOptions(question, index);

        // 更新按鈕狀態
        this.updateNavigationButtons();

        // 更新題目導航狀態
        this.updateQuestionNavigation();

        // 更新進度條
        this.updateProgress();
    }

    /**
     * 格式化題目文字
     */
    formatQuestionText(text) {
        // 處理數學公式、圖片等特殊格式
        return text.replace(/\n/g, '<br>');
    }

    /**
     * 顯示選項
     */
    displayOptions(question, questionIndex) {
        if (!this.optionsContainer) return;

        this.optionsContainer.innerHTML = '';

        const options = question.options || [];
        const selectedAnswer = this.answers[questionIndex];

        options.forEach((option, optionIndex) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors';
            
            const radioInput = document.createElement('input');
            radioInput.type = 'radio';
            radioInput.name = `question_${questionIndex}`;
            radioInput.value = optionIndex;
            radioInput.id = `option_${questionIndex}_${optionIndex}`;
            radioInput.className = 'mr-3 text-blue-600 focus:ring-blue-500';
            
            if (selectedAnswer === optionIndex) {
                radioInput.checked = true;
                optionElement.classList.add('bg-blue-50', 'border-blue-300');
            }

            radioInput.addEventListener('change', () => {
                this.selectAnswer(questionIndex, optionIndex);
            });

            const label = document.createElement('label');
            label.htmlFor = radioInput.id;
            label.className = 'flex-1 cursor-pointer';
            label.innerHTML = `<span class="font-medium text-gray-700">${String.fromCharCode(65 + optionIndex)}.</span> ${option}`;

            optionElement.appendChild(radioInput);
            optionElement.appendChild(label);
            
            // 點擊整個選項區域也能選中
            optionElement.addEventListener('click', (e) => {
                if (e.target !== radioInput) {
                    radioInput.checked = true;
                    this.selectAnswer(questionIndex, optionIndex);
                }
            });

            this.optionsContainer.appendChild(optionElement);
        });
    }

    /**
     * 選擇答案
     */
    selectAnswer(questionIndex, optionIndex) {
        this.answers[questionIndex] = optionIndex;
        
        // 更新選項外觀
        const optionElements = this.optionsContainer.querySelectorAll('div');
        optionElements.forEach((el, index) => {
            if (index === optionIndex) {
                el.classList.add('bg-blue-50', 'border-blue-300');
            } else {
                el.classList.remove('bg-blue-50', 'border-blue-300');
            }
        });

        // 更新題目導航狀態
        this.updateQuestionNavigation();
    }

    /**
     * 前一題
     */
    goToPrevQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.displayQuestion(this.currentQuestionIndex - 1);
        }
    }

    /**
     * 下一題
     */
    goToNextQuestion() {
        if (this.currentQuestionIndex < this.questions.length - 1) {
            this.displayQuestion(this.currentQuestionIndex + 1);
        }
    }

    /**
     * 跳轉到指定題目
     */
    goToQuestion(index) {
        this.displayQuestion(index);
    }

    /**
     * 更新導航按鈕狀態
     */
    updateNavigationButtons() {
        if (this.prevButton) {
            this.prevButton.disabled = this.currentQuestionIndex === 0;
        }

        if (this.nextButton) {
            // 如果是最後一題，改變按鈕文字和功能
            if (this.currentQuestionIndex === this.questions.length - 1) {
                this.nextButton.textContent = '交卷';
                this.nextButton.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                this.nextButton.classList.add('bg-green-600', 'hover:bg-green-700');
                // 移除原有的事件監聽器
                this.nextButton.onclick = () => this.showSubmitConfirmation();
            } else {
                this.nextButton.textContent = '下一題';
                this.nextButton.classList.remove('bg-green-600', 'hover:bg-green-700');
                this.nextButton.classList.add('bg-blue-600', 'hover:bg-blue-700');
                // 恢復原有的事件監聽器
                this.nextButton.onclick = () => this.goToNextQuestion();
            }
            this.nextButton.disabled = false;
        }
    }

    /**
     * 更新題目導航狀態
     */
    updateQuestionNavigation() {
        if (!this.questionNav) return;

        const navButtons = this.questionNav.querySelectorAll('button');
        navButtons.forEach((button, index) => {
            // 重置樣式
            button.className = 'w-8 h-8 rounded border-2 text-sm font-medium transition-colors';
            
            if (index === this.currentQuestionIndex) {
                // 當前題目
                button.classList.add('bg-blue-600', 'text-white', 'border-blue-600');
            } else if (this.answers[index] !== null) {
                // 已作答
                button.classList.add('bg-green-100', 'text-green-800', 'border-green-300');
            } else {
                // 未作答
                button.classList.add('border-gray-300', 'text-gray-600', 'hover:bg-gray-100');
            }
        });
    }

    /**
     * 更新進度條
     */
    updateProgress() {
        if (!this.progressBar) return;

        const answeredCount = this.answers.filter(answer => answer !== null).length;
        const progress = (answeredCount / this.questions.length) * 100;
        
        this.progressBar.style.width = `${progress}%`;
        
        // 更新進度文字
        const progressText = document.getElementById('progressText');
        if (progressText) {
            progressText.textContent = `已完成 ${answeredCount} / ${this.questions.length} 題`;
        }
    }

    /**
     * 開始計時
     */
    startTimer() {
        this.updateTimeDisplay();
        
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            this.updateTimeDisplay();
            
            if (this.timeRemaining <= 0) {
                this.timeUp();
            }
        }, 1000);
    }

    /**
     * 更新時間顯示
     */
    updateTimeDisplay() {
        if (!this.timeDisplay) return;

        const hours = Math.floor(this.timeRemaining / 3600);
        const minutes = Math.floor((this.timeRemaining % 3600) / 60);
        const seconds = this.timeRemaining % 60;

        const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        this.timeDisplay.textContent = timeString;

        // 時間不足時變紅
        if (this.timeRemaining < 300) { // 少於5分鐘
            this.timeDisplay.classList.add('text-red-600');
        }
    }

    /**
     * 時間到
     */
    timeUp() {
        clearInterval(this.timerInterval);
        alert('考試時間到！系統將自動提交您的答案。');
        this.submitExam();
    }

    /**
     * 顯示提交確認
     */
    showSubmitConfirmation() {
        const unansweredCount = this.answers.filter(answer => answer === null).length;
        let message = '確定要提交考試嗎？';
        
        if (unansweredCount > 0) {
            message += `\n還有 ${unansweredCount} 題未作答。`;
        }

        if (confirm(message)) {
            this.submitExam();
        }
    }

    /**
     * 顯示交卷確認對話框
     */
    showSubmitConfirmation() {
        const unansweredCount = this.answers.filter(answer => answer === null).length;
        const message = unansweredCount > 0 
            ? `您還有 ${unansweredCount} 題尚未作答，確定要交卷嗎？`
            : '確定要交卷嗎？';

        if (confirm(message)) {
            this.submitExam();
        }
    }

    /**
     * 自動批改考試
     */
    gradeExam() {
        let correctCount = 0;
        const detailedResults = [];

        this.questions.forEach((question, index) => {
            const userAnswer = this.answers[index];
            const isCorrect = userAnswer === question.correct_answer;
            
            if (isCorrect) {
                correctCount++;
            }

            detailedResults.push({
                questionId: question.id,
                questionText: question.question_text,
                options: question.options,
                userAnswer: userAnswer,
                correctAnswer: question.correct_answer,
                isCorrect: isCorrect,
                explanation: question.explanation,
                userAnswerText: userAnswer !== null ? question.options[userAnswer] : '未作答',
                correctAnswerText: question.options[question.correct_answer]
            });
        });

        const score = Math.round((correctCount / this.questions.length) * 100);
        
        return {
            score: score,
            totalQuestions: this.questions.length,
            correctAnswers: correctCount,
            wrongAnswers: this.questions.length - correctCount,
            detailedResults: detailedResults
        };
    }

    /**
     * 提交考試
     */
    async submitExam() {
        try {
            // 停止計時
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
            }

            // 顯示載入狀態
            this.setSubmitLoading(true);

            const endTime = new Date();
            const duration = Math.floor((endTime - this.startTime) / 1000);

            // 進行本地自動批改
            const results = this.gradeExam();

            // 將結果存儲到 sessionStorage，供結果頁面使用
            sessionStorage.setItem('examResults', JSON.stringify({
                ...results,
                timeSpent: duration,
                submittedAt: endTime.toISOString(),
                questions: this.questions,
                userAnswers: this.answers
            }));

            // 顯示成功訊息
            alert(`考試完成！得分：${results.score}分`);

            // 跳轉到結果頁面
            setTimeout(() => {
                window.location.href = '../pages/result.html';
            }, 1500);

        } catch (error) {
            console.error('提交考試失敗:', error);
            this.showError('提交失敗，請稍後再試');
        } finally {
            this.setSubmitLoading(false);
        }
    }

    /**
     * 自動儲存答案
     */
    async autoSaveAnswers() {
        try {
            const saveData = {
                session_id: this.sessionId,
                answers: this.answers,
                current_question: this.currentQuestionIndex
            };

            await fetch(`/api/v1/exercises/${this.sessionId}/save`, {
                method: 'POST',
                headers: authManager.getAuthHeaders(),
                body: JSON.stringify(saveData)
            });

            console.log('答案自動儲存成功');
        } catch (error) {
            console.error('自動儲存失敗:', error);
        }
    }

    /**
     * 檢查是否有未儲存的變更
     */
    hasUnsavedChanges() {
        return this.answers.some(answer => answer !== null);
    }

    /**
     * 設置提交載入狀態
     */
    setSubmitLoading(isLoading) {
        if (this.submitButton) {
            if (isLoading) {
                this.submitButton.disabled = true;
                this.submitButton.innerHTML = `
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    提交中...
                `;
            } else {
                this.submitButton.disabled = false;
                this.submitButton.textContent = '提交考試';
            }
        }
    }

    /**
     * 顯示錯誤訊息
     */
    showError(message) {
        alert(message); // 簡單實現，後續可改為更好的UI
    }

    /**
     * 生成模擬題目
     */
    async generateMockQuestions(parameters) {
        const { grade, publisher, subject, chapter, question_count } = parameters;
        
        // 首先嘗試從真實題庫載入
        try {
            const realQuestions = await this.loadRealQuestions(grade, publisher, subject, chapter);
            if (realQuestions && realQuestions.length > 0) {
                // 隨機選擇指定數量的題目
                const shuffled = this.shuffleArray([...realQuestions]);
                const selected = shuffled.slice(0, Math.min(question_count, shuffled.length));
                console.log(`從真實題庫載入了 ${selected.length} 道題目`);
                return this.formatQuestionsForExam(selected);
            }
        } catch (error) {
            console.error('載入真實題庫失敗:', error);
        }
        
        // 如果無法載入真實題庫，則生成模擬題目
        console.log('使用模擬題目');
        const questions = [];
        
        for (let i = 1; i <= question_count; i++) {
            questions.push({
                id: i,
                question_text: `${subject} ${grade} ${chapter} - 第 ${i} 題：這是一道關於 ${chapter} 的測試題目。請選擇正確答案。`,
                options: [
                    `選項 A：這是第一個選項`,
                    `選項 B：這是第二個選項`,
                    `選項 C：這是第三個選項`,
                    `選項 D：這是第四個選項`
                ],
                correct_answer: 0, // 正確答案是第一個選項
                explanation: `這是第 ${i} 題的詳細解析...`
            });
        }
        
        return questions;
    }

    /**
     * 生成預設題目
     */
    generateDefaultQuestions() {
        return [
            {
                id: 1,
                question_text: "下列何者為台灣最高峰？",
                options: ["玉山", "雪山", "合歡山", "阿里山"],
                correct_answer: 0,
                explanation: "玉山是台灣最高峰，海拔3952公尺。"
            },
            {
                id: 2,
                question_text: "1 + 1 = ?",
                options: ["1", "2", "3", "4"],
                correct_answer: 1,
                explanation: "1 + 1 等於 2，這是基本的數學運算。"
            },
            {
                id: 3,
                question_text: "台灣的首都是？",
                options: ["台北", "台中", "台南", "高雄"],
                correct_answer: 0,
                explanation: "台北是中華民國的首都。"
            }
        ];
    }

    /**
     * 載入真實題庫
     */
    async loadRealQuestions(grade, publisher, subject, chapter) {
        // 構建可能的文件名
        const possibleFiles = [
            `demo_${subject}_${grade}.json`, // 示例文件
            `${publisher}_${grade}_${subject}.json`,
            `${publisher}_${subject}.json`,
            `生成_${subject}_100.json`
        ];

        for (const fileName of possibleFiles) {
            try {
                const response = await fetch(`../../files/rawdata/${fileName}`);
                if (response.ok) {
                    const data = await response.json();
                    console.log(`成功載入題庫文件: ${fileName}`);
                    
                    // 過濾符合條件的題目
                    const filteredQuestions = data.filter(q => {
                        return (!grade || q.grade === grade) &&
                               (!publisher || q.publisher === publisher) &&
                               (!subject || q.subject === subject) &&
                               (!chapter || q.chapter === chapter || q.chapter.includes(chapter));
                    });
                    
                    if (filteredQuestions.length > 0) {
                        return filteredQuestions;
                    }
                }
            } catch (error) {
                console.log(`無法載入 ${fileName}:`, error.message);
            }
        }
        
        return null;
    }

    /**
     * 打亂數組順序
     */
    shuffleArray(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }

    /**
     * 將題庫格式轉換為考試格式
     */
    formatQuestionsForExam(rawQuestions) {
        return rawQuestions.map((q, index) => {
            // 處理選項格式
            let options = [];
            if (q.options) {
                if (Array.isArray(q.options)) {
                    options = q.options;
                } else if (typeof q.options === 'object') {
                    // 如果選項是物件格式 {A: "...", B: "...", C: "...", D: "..."}
                    options = Object.values(q.options);
                }
            }

            // 處理正確答案格式
            let correct_answer = 0;
            if (q.answer) {
                if (typeof q.answer === 'string') {
                    // 如果答案是 "A", "B", "C", "D" 格式
                    const answerMap = { 'A': 0, 'B': 1, 'C': 2, 'D': 3 };
                    correct_answer = answerMap[q.answer.toUpperCase()] || 0;
                } else if (typeof q.answer === 'number') {
                    correct_answer = q.answer;
                }
            }

            return {
                id: index + 1,
                question_text: q.question || '題目內容',
                options: options,
                correct_answer: correct_answer,
                explanation: q.explanation || '暫無解析',
                originalData: q // 保留原始數據用於批改
            };
        });
    }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
    new ExamPage();
}); 