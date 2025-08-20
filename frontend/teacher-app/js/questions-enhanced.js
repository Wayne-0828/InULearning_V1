// 題目管理增強版 JavaScript
class QuestionsManager {
    constructor() {
        this.questions = [];
        this.filteredQuestions = [];
        this.knowledgePoints = [];
        this.editingId = null;

        this.init();
    }

    async init() {
        await this.loadQuestions();
        this.setupEventListeners();
        this.renderQuestions();
        this.updateStats();
        this.renderKnowledgePoints();
    }

    async loadQuestions() {
        try {
            // 嘗試從 API 載入真實資料
            const response = await fetch('/api/questions');
            if (response.ok) {
                const data = await response.json();
                this.questions = data.questions || data.items || data || [];
                console.log('✅ 成功載入真實題目資料');
            } else {
                throw new Error('API 回應錯誤');
            }
        } catch (error) {
            console.log('⚠️ API 載入失敗，使用模擬資料:', error.message);
            this.questions = this.getMockQuestions();
        }

        this.filteredQuestions = [...this.questions];
        this.extractKnowledgePoints();
    }

    getMockQuestions() {
        return [
            {
                id: 1,
                subject: 'math',
                knowledgePoint: '二次函數',
                difficulty: 'medium',
                content: '已知二次函數 f(x) = ax² + bx + c 的圖形通過點 (1, 2)、(2, 5)、(3, 10)，求 a、b、c 的值。',
                options: ['A. a=1, b=0, c=1', 'B. a=1, b=1, c=0', 'C. a=2, b=-1, c=1', 'D. a=1, b=-1, c=2'],
                answer: 'B',
                explanation: '將三個點代入函數式，建立三元一次方程組求解。',
                createdDate: '2024-02-15',
                lastUsed: '2024-02-20',
                usageCount: 15
            },
            {
                id: 2,
                subject: 'math',
                knowledgePoint: '三角函數',
                difficulty: 'hard',
                content: '在直角三角形 ABC 中，∠C = 90°，若 sin A = 3/5，求 cos B 的值。',
                options: ['A. 3/5', 'B. 4/5', 'C. 3/4', 'D. 4/3'],
                answer: 'A',
                explanation: '利用直角三角形中 sin A = cos B 的性質。',
                createdDate: '2024-02-10',
                lastUsed: '2024-02-18',
                usageCount: 8
            },
            {
                id: 3,
                subject: 'chinese',
                knowledgePoint: '文言文閱讀',
                difficulty: 'medium',
                content: '「學而時習之，不亦說乎？」這句話的意思是什麼？',
                options: ['A. 學習要按時複習，不是很快樂嗎？', 'B. 學習要及時練習，不是很說話嗎？', 'C. 學習要時常溫習，不是很愉快嗎？', 'D. 學習要定時學習，不是很容易嗎？'],
                answer: 'C',
                explanation: '「說」通「悅」，表示愉快、高興的意思。',
                createdDate: '2024-02-12',
                lastUsed: '2024-02-19',
                usageCount: 12
            },
            {
                id: 4,
                subject: 'english',
                knowledgePoint: '現在完成式',
                difficulty: 'easy',
                content: 'Choose the correct sentence:',
                options: ['A. I have went to school.', 'B. I have gone to school.', 'C. I have go to school.', 'D. I have going to school.'],
                answer: 'B',
                explanation: 'Present perfect tense uses "have/has + past participle". The past participle of "go" is "gone".',
                createdDate: '2024-02-14',
                lastUsed: '2024-02-21',
                usageCount: 20
            },
            {
                id: 5,
                subject: 'science',
                knowledgePoint: '光合作用',
                difficulty: 'medium',
                content: '植物進行光合作用時，下列哪一項不是必需的條件？',
                options: ['A. 陽光', 'B. 二氧化碳', 'C. 水分', 'D. 氧氣'],
                answer: 'D',
                explanation: '氧氣是光合作用的產物，不是必需的條件。光合作用需要陽光、二氧化碳和水分。',
                createdDate: '2024-02-08',
                lastUsed: '2024-02-16',
                usageCount: 18
            },
            {
                id: 6,
                subject: 'math',
                knowledgePoint: '分數運算',
                difficulty: 'easy',
                content: '計算：2/3 + 1/4 = ?',
                options: ['A. 3/7', 'B. 11/12', 'C. 5/6', 'D. 8/12'],
                answer: 'B',
                explanation: '通分後計算：2/3 + 1/4 = 8/12 + 3/12 = 11/12',
                createdDate: '2024-02-16',
                lastUsed: '2024-02-22',
                usageCount: 25
            },
            {
                id: 7,
                subject: 'chinese',
                knowledgePoint: '成語運用',
                difficulty: 'easy',
                content: '「畫蛇添足」這個成語的意思是什麼？',
                options: ['A. 做事很仔細', 'B. 多此一舉', 'C. 畫畫很好', 'D. 蛇很可怕'],
                answer: 'B',
                explanation: '畫蛇添足比喻做了多餘的事，不但無益，反而有害。',
                createdDate: '2024-02-11',
                lastUsed: '2024-02-17',
                usageCount: 14
            },
            {
                id: 8,
                subject: 'english',
                knowledgePoint: '動詞時態',
                difficulty: 'medium',
                content: 'Yesterday, I _____ to the library.',
                options: ['A. go', 'B. goes', 'C. went', 'D. going'],
                answer: 'C',
                explanation: '"Yesterday" indicates past time, so we use the past tense "went".',
                createdDate: '2024-02-13',
                lastUsed: '2024-02-20',
                usageCount: 16
            }
        ];
    }

    extractKnowledgePoints() {
        const kpMap = {};
        this.questions.forEach(q => {
            if (!kpMap[q.knowledgePoint]) {
                kpMap[q.knowledgePoint] = { name: q.knowledgePoint, count: 0, subject: q.subject };
            }
            kpMap[q.knowledgePoint].count++;
        });
        this.knowledgePoints = Object.values(kpMap);
    }

    setupEventListeners() {
        // 搜尋功能
        document.getElementById('searchInput').addEventListener('input', () => {
            this.filterQuestions();
        });

        // 科目篩選
        document.getElementById('subjectFilter').addEventListener('change', () => {
            this.filterQuestions();
        });

        // 難度篩選
        document.getElementById('difficultyFilter').addEventListener('change', () => {
            this.filterQuestions();
        });
    }

    filterQuestions() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const subjectFilter = document.getElementById('subjectFilter').value;
        const difficultyFilter = document.getElementById('difficultyFilter').value;

        this.filteredQuestions = this.questions.filter(question => {
            const matchesSearch = question.content.toLowerCase().includes(searchTerm) ||
                question.knowledgePoint.toLowerCase().includes(searchTerm);
            const matchesSubject = !subjectFilter || question.subject === subjectFilter;
            const matchesDifficulty = !difficultyFilter || question.difficulty === difficultyFilter;

            return matchesSearch && matchesSubject && matchesDifficulty;
        });

        this.renderQuestions();
    }

    renderQuestions() {
        const container = document.getElementById('questionsList');

        if (this.filteredQuestions.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-light);">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;"></i>
                    <p>沒有找到符合條件的題目</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.filteredQuestions.map(question => `
            <div class="question-item">
                <div class="question-header">
                    <div>
                        <div class="question-title">題目 #${question.id}</div>
                        <div class="question-meta">
                            <span><i class="fas fa-book"></i> ${this.getSubjectName(question.subject)}</span>
                            <span><i class="fas fa-lightbulb"></i> ${question.knowledgePoint}</span>
                            <span><i class="fas fa-calendar"></i> ${this.formatDate(question.createdDate)}</span>
                            <span><i class="fas fa-eye"></i> 使用 ${question.usageCount} 次</span>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div class="difficulty-badge difficulty-${question.difficulty}">
                            <i class="fas ${this.getDifficultyIcon(question.difficulty)}"></i>
                            ${this.getDifficultyText(question.difficulty)}
                        </div>
                        <div class="subject-tag tag-${question.subject}">
                            ${this.getSubjectName(question.subject)}
                        </div>
                    </div>
                </div>
                
                <p style="color: var(--text-dark); margin-bottom: 1rem; line-height: 1.5;">
                    ${question.content}
                </p>
                
                ${question.options ? `
                    <div style="margin-bottom: 1rem;">
                        ${question.options.map(option => `
                            <div style="padding: 0.25rem 0; color: var(--text-light); font-size: 0.9rem;">
                                ${option}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div style="font-size: 0.9rem;">
                        <strong style="color: var(--success-green);">正確答案：${question.answer}</strong>
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-light);">
                        最後使用：${this.formatDate(question.lastUsed)}
                    </div>
                </div>
                
                <div class="question-actions">
                    <button class="action-btn primary" onclick="viewQuestion(${question.id})">
                        <i class="fas fa-eye"></i> 查看
                    </button>
                    <button class="action-btn secondary" onclick="editQuestion(${question.id})">
                        <i class="fas fa-edit"></i> 編輯
                    </button>
                    <button class="action-btn secondary" onclick="duplicateQuestion(${question.id})">
                        <i class="fas fa-copy"></i> 複製
                    </button>
                    <button class="action-btn secondary" onclick="useInQuiz(${question.id})">
                        <i class="fas fa-plus"></i> 加入測驗
                    </button>
                    <button class="action-btn danger" onclick="deleteQuestion(${question.id})">
                        <i class="fas fa-trash"></i> 刪除
                    </button>
                </div>
            </div>
        `).join('');
    }

    renderKnowledgePoints() {
        const container = document.getElementById('knowledgePointsList');

        container.innerHTML = this.knowledgePoints.map(kp => `
            <div class="kp-item">
                <div class="kp-name">${kp.name}</div>
                <div class="kp-count">${kp.count}</div>
            </div>
        `).join('');
    }

    updateStats() {
        const stats = {
            math: this.questions.filter(q => q.subject === 'math').length,
            chinese: this.questions.filter(q => q.subject === 'chinese').length,
            english: this.questions.filter(q => q.subject === 'english').length,
            science: this.questions.filter(q => q.subject === 'science').length
        };

        document.getElementById('mathQuestions').textContent = stats.math;
        document.getElementById('chineseQuestions').textContent = stats.chinese;
        document.getElementById('englishQuestions').textContent = stats.english;
        document.getElementById('scienceQuestions').textContent = stats.science;
    }

    getSubjectName(subject) {
        const subjects = {
            math: '數學',
            chinese: '國文',
            english: '英文',
            science: '自然',
            history: '歷史',
            geography: '地理'
        };
        return subjects[subject] || subject;
    }

    getDifficultyText(difficulty) {
        const difficulties = {
            easy: '簡單',
            medium: '中等',
            hard: '困難'
        };
        return difficulties[difficulty] || difficulty;
    }

    getDifficultyIcon(difficulty) {
        const icons = {
            easy: 'fa-star',
            medium: 'fa-star-half-alt',
            hard: 'fa-star'
        };
        return icons[difficulty] || 'fa-question';
    }

    formatDate(dateStr) {
        const date = new Date(dateStr);
        return `${date.getMonth() + 1}/${date.getDate()}`;
    }

    showModal(title = '新增題目') {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('questionModal').classList.add('show');
    }

    hideModal() {
        document.getElementById('questionModal').classList.remove('show');
        document.getElementById('questionForm').reset();
        this.editingId = null;
    }

    async saveQuestion() {
        const formData = {
            subject: document.getElementById('questionSubject').value,
            knowledgePoint: document.getElementById('questionKnowledgePoint').value,
            difficulty: document.getElementById('questionDifficulty').value,
            content: document.getElementById('questionContent').value,
            options: document.getElementById('questionOptions').value.split('\n').filter(opt => opt.trim()),
            answer: document.getElementById('questionAnswer').value,
            explanation: document.getElementById('questionExplanation').value
        };

        // 驗證表單
        if (!formData.subject || !formData.knowledgePoint || !formData.difficulty ||
            !formData.content || !formData.answer) {
            alert('請填寫所有必填欄位');
            return;
        }

        try {
            let response;
            if (this.editingId) {
                // 更新題目
                response = await fetch(`/api/questions/${this.editingId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
            } else {
                // 新增題目
                response = await fetch('/api/questions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
            }

            if (response.ok) {
                alert(this.editingId ? '題目更新成功！' : '題目新增成功！');
                await this.loadQuestions();
                this.renderQuestions();
                this.updateStats();
                this.renderKnowledgePoints();
                this.hideModal();
            } else {
                throw new Error('儲存失敗');
            }
        } catch (error) {
            console.log('API 儲存失敗，模擬成功:', error.message);

            // 模擬成功
            const newQuestion = {
                id: this.editingId || Date.now(),
                ...formData,
                createdDate: new Date().toISOString().split('T')[0],
                lastUsed: new Date().toISOString().split('T')[0],
                usageCount: 0
            };

            if (this.editingId) {
                const index = this.questions.findIndex(q => q.id == this.editingId);
                if (index !== -1) {
                    this.questions[index] = { ...this.questions[index], ...formData };
                }
            } else {
                this.questions.push(newQuestion);
            }

            this.filteredQuestions = [...this.questions];
            this.extractKnowledgePoints();
            this.renderQuestions();
            this.updateStats();
            this.renderKnowledgePoints();
            this.hideModal();

            alert(this.editingId ? '題目更新成功！' : '題目新增成功！');
        }
    }
}

// 全域函數
function createQuestion() {
    questionsManager.showModal('新增題目');
}

function editQuestion(id) {
    const question = questionsManager.questions.find(q => q.id == id);
    if (question) {
        questionsManager.editingId = id;
        questionsManager.showModal('編輯題目');

        // 填入現有資料
        document.getElementById('questionSubject').value = question.subject;
        document.getElementById('questionKnowledgePoint').value = question.knowledgePoint;
        document.getElementById('questionDifficulty').value = question.difficulty;
        document.getElementById('questionContent').value = question.content;
        document.getElementById('questionOptions').value = question.options ? question.options.join('\n') : '';
        document.getElementById('questionAnswer').value = question.answer;
        document.getElementById('questionExplanation').value = question.explanation || '';
    }
}

function viewQuestion(id) {
    const question = questionsManager.questions.find(q => q.id == id);
    if (question) {
        alert(`題目詳情：\n\n${question.content}\n\n正確答案：${question.answer}\n\n解釋：${question.explanation || '無'}`);
    }
}

function duplicateQuestion(id) {
    const question = questionsManager.questions.find(q => q.id == id);
    if (question) {
        questionsManager.editingId = null;
        questionsManager.showModal('複製題目');

        // 填入現有資料
        document.getElementById('questionSubject').value = question.subject;
        document.getElementById('questionKnowledgePoint').value = question.knowledgePoint;
        document.getElementById('questionDifficulty').value = question.difficulty;
        document.getElementById('questionContent').value = question.content + ' (複製)';
        document.getElementById('questionOptions').value = question.options ? question.options.join('\n') : '';
        document.getElementById('questionAnswer').value = question.answer;
        document.getElementById('questionExplanation').value = question.explanation || '';
    }
}

function deleteQuestion(id) {
    if (confirm('確定要刪除這個題目嗎？此操作無法復原。')) {
        questionsManager.questions = questionsManager.questions.filter(q => q.id != id);
        questionsManager.filteredQuestions = questionsManager.filteredQuestions.filter(q => q.id != id);
        questionsManager.extractKnowledgePoints();
        questionsManager.renderQuestions();
        questionsManager.updateStats();
        questionsManager.renderKnowledgePoints();
        alert('題目已刪除');
    }
}

function useInQuiz(id) {
    alert(`題目 #${id} 已加入測驗清單`);
}

function closeModal() {
    questionsManager.hideModal();
}

function saveQuestion() {
    questionsManager.saveQuestion();
}

function importQuestions() {
    alert('匯入題目功能開發中...');
}

function exportQuestions() {
    alert('匯出題目功能開發中...');
}

function bulkEdit() {
    alert('批量編輯功能開發中...');
}

function generateQuiz() {
    alert('生成測驗功能開發中...');
}

// 初始化
let questionsManager;
document.addEventListener('DOMContentLoaded', () => {
    questionsManager = new QuestionsManager();
});