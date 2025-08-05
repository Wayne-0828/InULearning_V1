// 完整的前後端整合測試腳本
// 使用方法：在瀏覽器控制台中執行此腳本

async function testCompleteFlow() {
    console.log('🚀 開始完整的前後端整合測試...');
    
    try {
        // 步驟 1: 清理舊數據
        console.log('📋 步驟 1: 清理舊數據...');
        localStorage.removeItem('auth_token');
        sessionStorage.removeItem('examResults');
        sessionStorage.removeItem('savedSessionId');
        console.log('✅ 清理完成');
        
        // 步驟 2: 用戶登入
        console.log('📋 步驟 2: 用戶登入...');
        const loginResponse = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: 'test02@test.com',
                password: 'P@ssw0rd'
            })
        });
        
        if (!loginResponse.ok) {
            throw new Error(`登入失敗: ${loginResponse.status}`);
        }
        
        const loginData = await loginResponse.json();
        localStorage.setItem('auth_token', loginData.access_token);
        console.log('✅ 登入成功，Token已保存');
        
        // 步驟 3: 設置練習結果數據
        console.log('📋 步驟 3: 設置練習結果數據...');
        const examResults = {
            score: 90,
            correctAnswers: 9,
            accuracy: 90,
            timeSpent: 450,
            detailedResults: [
                {
                    questionId: 'flow_test_q_001',
                    questionContent: '解方程式 2x + 6 = 14',
                    questionText: '解方程式 2x + 6 = 14',
                    options: ['x = 3', 'x = 4', 'x = 5', 'x = 6'],
                    answerChoices: {A: 'x = 3', B: 'x = 4', C: 'x = 5', D: 'x = 6'},
                    userAnswer: 'B',
                    correctAnswer: 'B',
                    isCorrect: true,
                    score: 100,
                    explanation: '移項得到 2x = 8，所以 x = 4',
                    timeSpent: 60,
                    subject: '數學',
                    grade: '8A',
                    chapter: '一元一次方程式',
                    publisher: '南一',
                    difficulty: 'normal',
                    knowledgePoints: ['一元一次方程式', '移項運算'],
                    questionTopic: '一元一次方程式解法'
                },
                {
                    questionId: 'flow_test_q_002',
                    questionContent: '計算 5 × 6 - 8',
                    questionText: '計算 5 × 6 - 8',
                    options: ['22', '23', '24', '25'],
                    answerChoices: {A: '22', B: '23', C: '24', D: '25'},
                    userAnswer: 'A',
                    correctAnswer: 'A',
                    isCorrect: true,
                    score: 100,
                    explanation: '先算乘法：5 × 6 = 30，再算減法：30 - 8 = 22',
                    timeSpent: 40,
                    subject: '數學',
                    grade: '8A',
                    chapter: '四則運算',
                    publisher: '南一',
                    difficulty: 'easy',
                    knowledgePoints: ['四則運算', '運算順序'],
                    questionTopic: '四則運算順序'
                },
                {
                    questionId: 'flow_test_q_003',
                    questionContent: '化簡 3x + 2x',
                    questionText: '化簡 3x + 2x',
                    options: ['5x', '6x', '5x²', '6x²'],
                    answerChoices: {A: '5x', B: '6x', C: '5x²', D: '6x²'},
                    userAnswer: 'B',
                    correctAnswer: 'A',
                    isCorrect: false,
                    score: 0,
                    explanation: '同類項相加：3x + 2x = 5x',
                    timeSpent: 50,
                    subject: '數學',
                    grade: '8A',
                    chapter: '代數',
                    publisher: '南一',
                    difficulty: 'normal',
                    knowledgePoints: ['代數', '同類項'],
                    questionTopic: '同類項合併'
                }
            ],
            sessionData: {
                subject: '數學',
                grade: '8A',
                chapter: '綜合練習',
                publisher: '南一',
                difficulty: 'normal',
                sessionName: '完整流程測試會話',
                knowledgePoints: ['一元一次方程式', '四則運算', '代數']
            }
        };
        
        sessionStorage.setItem('examResults', JSON.stringify(examResults));
        console.log('✅ 練習結果數據已設置');
        
        // 步驟 4: 模擬 result.js 的保存邏輯
        console.log('📋 步驟 4: 執行保存邏輯...');
        
        // 檢查登入狀態
        const token = localStorage.getItem('auth_token');
        if (!token) {
            throw new Error('未找到認證Token');
        }
        
        // 檢查數據
        const storedResults = JSON.parse(sessionStorage.getItem('examResults'));
        if (!storedResults || !storedResults.detailedResults || storedResults.detailedResults.length === 0) {
            throw new Error('未找到有效的練習結果數據');
        }
        
        // 轉換數據格式
        const requestData = {
            session_name: storedResults.sessionData.sessionName,
            subject: storedResults.sessionData.subject,
            grade: storedResults.sessionData.grade,
            chapter: storedResults.sessionData.chapter,
            publisher: storedResults.sessionData.publisher,
            difficulty: storedResults.sessionData.difficulty,
            knowledge_points: storedResults.sessionData.knowledgePoints,
            exercise_results: storedResults.detailedResults.map(result => ({
                question_id: result.questionId,
                subject: result.subject,
                grade: result.grade,
                chapter: result.chapter,
                publisher: result.publisher,
                knowledge_points: result.knowledgePoints,
                question_content: result.questionContent,
                answer_choices: result.answerChoices,
                difficulty: result.difficulty,
                question_topic: result.questionTopic,
                user_answer: result.userAnswer,
                correct_answer: result.correctAnswer,
                is_correct: result.isCorrect,
                score: result.score,
                explanation: result.explanation,
                time_spent: result.timeSpent
            })),
            total_time_spent: storedResults.timeSpent,
            session_metadata: {
                source: 'complete_flow_test',
                device: 'desktop',
                test_timestamp: new Date().toISOString()
            }
        };
        
        console.log('📤 發送API請求...', requestData);
        
        // 步驟 5: 調用API
        const apiResponse = await fetch('/api/v1/learning/exercises/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(requestData)
        });
        
        if (!apiResponse.ok) {
            const errorText = await apiResponse.text();
            throw new Error(`API調用失敗: ${apiResponse.status} - ${errorText}`);
        }
        
        const apiData = await apiResponse.json();
        console.log('✅ API調用成功:', apiData);
        
        // 保存會話ID
        sessionStorage.setItem('savedSessionId', apiData.session_id);
        
        // 步驟 6: 驗證資料庫記錄
        console.log('📋 步驟 6: 測試完成！');
        console.log('🎉 完整流程測試成功！');
        console.log('📊 結果摘要:');
        console.log(`   - 會話ID: ${apiData.session_id}`);
        console.log(`   - 總題數: ${apiData.total_questions}`);
        console.log(`   - 答對數: ${apiData.correct_count}`);
        console.log(`   - 總分: ${apiData.total_score}`);
        console.log(`   - 正確率: ${apiData.accuracy_rate}%`);
        console.log(`   - 用時: ${apiData.time_spent}秒`);
        
        // 現在可以打開 result.html 頁面測試顯示
        console.log('');
        console.log('🔗 現在可以打開 result.html 頁面查看結果:');
        console.log('   http://localhost:8080/pages/result.html');
        
        return {
            success: true,
            sessionId: apiData.session_id,
            summary: apiData
        };
        
    } catch (error) {
        console.error('❌ 測試失敗:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

// 執行測試
console.log('請在瀏覽器控制台中執行: testCompleteFlow()');