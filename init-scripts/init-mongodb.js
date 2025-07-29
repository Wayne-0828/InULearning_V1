// 在 admin 資料庫中建立用戶
db = db.getSiblingDB('admin');

// 建立用戶（如果需要）
try {
    db.createUser({
        user: "aipe-tester",
        pwd: "aipe-tester",
        roles: [
            { role: "readWrite", db: "inulearning" },
            { role: "dbAdmin", db: "inulearning" }
        ]
    });
    print("User created successfully");
} catch (e) {
    // 用戶可能已存在，忽略錯誤
    print("User may already exist, continuing...");
}

// 切換到 inulearning 資料庫
db = db.getSiblingDB('inulearning');

// 在 inulearning 資料庫中也創建用戶
try {
    db.createUser({
        user: "aipe-tester",
        pwd: "aipe-tester",
        roles: [
            { role: "readWrite", db: "inulearning" },
            { role: "dbAdmin", db: "inulearning" }
        ]
    });
    print("User created in inulearning database successfully");
} catch (e) {
    print("User may already exist in inulearning database, continuing...");
}

// 建立集合
db.createCollection('questions');
db.createCollection('chapters');
db.createCollection('knowledge_points');

// 建立索引
db.questions.createIndex({ "subject": 1, "grade": 1, "chapter": 1 });
db.questions.createIndex({ "knowledge_points": 1 });
db.questions.createIndex({ "difficulty": 1 });
db.questions.createIndex({ "question_type": 1 });

db.chapters.createIndex({ "subject": 1, "grade": 1 });
db.knowledge_points.createIndex({ "subject": 1, "grade": 1, "chapter": 1 });

// 插入測試章節數據
db.chapters.insertMany([
    {
        subject: "數學",
        grade: "7A",
        chapter: "整數與分數",
        description: "學習整數和分數的基本概念與運算",
        order: 1,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        subject: "數學",
        grade: "7A",
        chapter: "代數式",
        description: "學習代數式的基本概念與運算",
        order: 2,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        subject: "數學",
        grade: "7A",
        chapter: "一元一次方程式",
        description: "學習一元一次方程式的解法",
        order: 3,
        created_at: new Date(),
        updated_at: new Date()
    }
]);

// 載入題庫資料 - 由 question-bank-service 的 load_rawdata.py 處理
print("題庫資料將由 question-bank-service 的 load_rawdata.py 腳本載入");

// 插入測試知識點數據
db.knowledge_points.insertMany([
    {
        subject: "數學",
        grade: "7A",
        chapter: "整數與分數",
        name: "整數的加法",
        description: "學習整數加法的規則與應用",
        order: 1,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        subject: "數學",
        grade: "7A",
        chapter: "整數與分數",
        name: "整數的減法",
        description: "學習整數減法的規則與應用",
        order: 2,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        subject: "數學",
        grade: "7A",
        chapter: "整數與分數",
        name: "分數的加法",
        description: "學習分數加法的規則與應用",
        order: 3,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        subject: "數學",
        grade: "7A",
        chapter: "代數式",
        name: "代數式的化簡",
        description: "學習代數式化簡的方法",
        order: 1,
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        subject: "數學",
        grade: "7A",
        chapter: "一元一次方程式",
        name: "移項法則",
        description: "學習一元一次方程式的移項法則",
        order: 1,
        created_at: new Date(),
        updated_at: new Date()
    }
]);

// 插入測試題目數據
db.questions.insertMany([
    {
        question_id: "MATH_001",
        subject: "數學",
        grade: "7A",
        chapter: "整數與分數",
        knowledge_points: ["整數的加法"],
        question_type: "選擇題",
        difficulty: "簡單",
        content: "計算：(-5) + 3 = ?",
        options: ["-8", "-2", "2", "8"],
        correct_answer: "-2",
        explanation: "負數加正數，取絕對值相減，符號取絕對值較大的數的符號。|-5| = 5, |3| = 3, 5 - 3 = 2，因為 -5 的絕對值較大，所以結果為負數，即 -2。",
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        question_id: "MATH_002",
        subject: "數學",
        grade: "7A",
        chapter: "整數與分數",
        knowledge_points: ["整數的減法"],
        question_type: "選擇題",
        difficulty: "簡單",
        content: "計算：7 - (-3) = ?",
        options: ["4", "10", "-4", "-10"],
        correct_answer: "10",
        explanation: "減去負數等於加上正數，所以 7 - (-3) = 7 + 3 = 10。",
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        question_id: "MATH_003",
        subject: "數學",
        grade: "7A",
        chapter: "整數與分數",
        knowledge_points: ["分數的加法"],
        question_type: "選擇題",
        difficulty: "中等",
        content: "計算：1/2 + 1/3 = ?",
        options: ["2/5", "5/6", "1/6", "3/5"],
        correct_answer: "5/6",
        explanation: "分數加法需要通分。1/2 = 3/6, 1/3 = 2/6，所以 1/2 + 1/3 = 3/6 + 2/6 = 5/6。",
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        question_id: "MATH_004",
        subject: "數學",
        grade: "7A",
        chapter: "代數式",
        knowledge_points: ["代數式的化簡"],
        question_type: "選擇題",
        difficulty: "中等",
        content: "化簡：2x + 3x - x = ?",
        options: ["4x", "5x", "6x", "x"],
        correct_answer: "4x",
        explanation: "同類項合併：2x + 3x - x = (2 + 3 - 1)x = 4x。",
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        question_id: "MATH_005",
        subject: "數學",
        grade: "7A",
        chapter: "一元一次方程式",
        knowledge_points: ["移項法則"],
        question_type: "選擇題",
        difficulty: "中等",
        content: "解方程式：2x + 5 = 13",
        options: ["x = 4", "x = 8", "x = 3", "x = 6"],
        correct_answer: "x = 4",
        explanation: "2x + 5 = 13，移項得 2x = 13 - 5 = 8，所以 x = 8 ÷ 2 = 4。",
        created_at: new Date(),
        updated_at: new Date()
    }
]);

print("MongoDB 初始化完成！"); 