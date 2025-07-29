// 章節初始化腳本
// 根據三版本科目章節.json 建立章節資料

// 切換到 inulearning 資料庫
db = db.getSiblingDB('inulearning');

// 建立用戶（如果需要）
try {
    db.createUser({
        user: "aipe-tester",
        pwd: "aipe-tester",
        roles: [
            { role: "readWrite", db: "inulearning" }
        ]
    });
} catch (e) {
    // 用戶可能已存在，忽略錯誤
    print("User may already exist, continuing...");
}

// 清空現有章節資料
db.chapters.deleteMany({});
db.knowledge_points.deleteMany({});

// 完整的章節資料（根據三版本科目章節.json）
const chapters = [
    // 南一版本
    {
        publisher: "南一",
        subject: "國文",
        grade: "7A",
        chapters: [
            "夏夜", "老師的十二樣見面禮", "鮭魚產卵，力爭上游", "吃冰的滋味",
            "絕句選(一)登鸛雀樓(二)黃鶴樓宋孟浩然之廣陵(三)楓橋夜泊",
            "飛翔的舞者", "牛背上的呀喝", "論語選(一)學而(二)子罕(三)述而紙船印象",
            "閱讀課　故鄉的桂花雨", "自學選文　暑假作業", "自學選文　茶葉的分類",
            "自學選文　值得記憶的小事：日記", "語文常識一　標點符號使用法",
            "語文常識二　資料檢索與閱讀策略"
        ]
    },
    {
        publisher: "南一",
        subject: "國文",
        grade: "7B",
        chapters: [
            "視力與偏見", "背　影", "土芭樂的生存之道", "溪頭的竹子",
            "律詩選(一)山居秋暝(二)聞官軍收河南河北", "劉墉寓言作品選",
            "負　荷", "兒時記趣", "謝　天", "閱讀課　示　愛",
            "自學選文　賣油翁", "自學選文　食蔥有時",
            "自學選文　跨時空的對望：淺談文言文翻譯", "語文常識一　認識漢字的造字法則",
            "語文常識二　漢字演變與書法欣賞"
        ]
    },
    {
        publisher: "南一",
        subject: "國文",
        grade: "8A",
        chapters: [
            "新詩選(一)傘(二)風箏", "聲音鐘", "我所知道的康橋", "五柳先生傳",
            "差不多先生傳", "張釋之執法", "蜜蜂的讚美", "愛蓮說", "棒球靈魂學",
            "指尖上的故事：簡報", "自學一　油桐花編織的祕徑", "自學二　王冕的少年時代",
            "自學三　一顆珍珠", "語文常識一　語法（上）詞類", "語文常識二　語法（下）句型"
        ]
    },
    {
        publisher: "南一",
        subject: "國文",
        grade: "8B",
        chapters: [
            "歲月跟著", "古詩選(一)迢迢牽牛星(二)四月十五夜鐵窗下作", "鳥",
            "田園之秋選", "木蘭詩", "深藍的憂鬱", "運動家的風度", "談交友",
            "為學一首示子姪", "舌尖上的思路：演講", "自學一　秋之味",
            "自學二　空城計", "自學三　陋室銘", "語文常識一　書信與便條",
            "語文常識二　題辭"
        ]
    },
    {
        publisher: "南一",
        subject: "國文",
        grade: "9A",
        chapters: [
            "余光中詩選(一)苗栗明德水庫(二)飛瀑", "詞選(一)武陵春(二)南鄉子登京口北固亭有懷",
            "黑與白──虎鯨", "臺北‧淡水105與宋元思書", "我的太魯閣",
            "生於憂患死於安樂", "在錯誤中學習", "寄弟墨書",
            "知識與表達的盛宴：專題報告", "自學一　春天的聲音", "自學二　大明湖",
            "自學三　人生逆境", "語文常識　對聯"
        ]
    },
    {
        publisher: "南一",
        subject: "國文",
        grade: "9B",
        chapters: [
            "一棵開花的樹", "曲選(一)沉醉東風漁父詞(二)天淨沙秋思", "人間情分",
            "項鍊", "水神的指引", "常保好奇心", "自學一　湖心亭看雪",
            "自學二　玫瑰樹根", "自學三　勤訓"
        ]
    },
    // 康軒版本
    {
        publisher: "康軒",
        subject: "國文",
        grade: "7A",
        chapters: [
            "夏夜", "老師的十二樣見面禮", "鮭魚產卵，力爭上游", "吃冰的滋味",
            "絕句選(一)登鸛雀樓(二)黃鶴樓宋孟浩然之廣陵(三)楓橋夜泊",
            "飛翔的舞者", "牛背上的呀喝", "論語選(一)學而(二)子罕(三)述而紙船印象",
            "閱讀課　故鄉的桂花雨", "自學選文　暑假作業", "自學選文　茶葉的分類",
            "自學選文　值得記憶的小事：日記", "語文常識一　標點符號使用法",
            "語文常識二　資料檢索與閱讀策略"
        ]
    },
    {
        publisher: "康軒",
        subject: "國文",
        grade: "7B",
        chapters: [
            "視力與偏見", "背　影", "土芭樂的生存之道", "溪頭的竹子",
            "律詩選(一)山居秋暝(二)聞官軍收河南河北", "劉墉寓言作品選",
            "負　荷", "兒時記趣", "謝　天", "閱讀課　示　愛",
            "自學選文　賣油翁", "自學選文　食蔥有時",
            "自學選文　跨時空的對望：淺談文言文翻譯", "語文常識一　認識漢字的造字法則",
            "語文常識二　漢字演變與書法欣賞"
        ]
    },
    // 翰林版本
    {
        publisher: "翰林",
        subject: "國文",
        grade: "7A",
        chapters: [
            "夏夜", "老師的十二樣見面禮", "鮭魚產卵，力爭上游", "吃冰的滋味",
            "絕句選(一)登鸛雀樓(二)黃鶴樓宋孟浩然之廣陵(三)楓橋夜泊",
            "飛翔的舞者", "牛背上的呀喝", "論語選(一)學而(二)子罕(三)述而紙船印象",
            "閱讀課　故鄉的桂花雨", "自學選文　暑假作業", "自學選文　茶葉的分類",
            "自學選文　值得記憶的小事：日記", "語文常識一　標點符號使用法",
            "語文常識二　資料檢索與閱讀策略"
        ]
    },
    {
        publisher: "翰林",
        subject: "國文",
        grade: "7B",
        chapters: [
            "視力與偏見", "背　影", "土芭樂的生存之道", "溪頭的竹子",
            "律詩選(一)山居秋暝(二)聞官軍收河南河北", "劉墉寓言作品選",
            "負　荷", "兒時記趣", "謝　天", "閱讀課　示　愛",
            "自學選文　賣油翁", "自學選文　食蔥有時",
            "自學選文　跨時空的對望：淺談文言文翻譯", "語文常識一　認識漢字的造字法則",
            "語文常識二　漢字演變與書法欣賞"
        ]
    },
    // 數學科目（簡化版本）
    {
        publisher: "南一",
        subject: "數學",
        grade: "7A",
        chapters: [
            "整數與分數", "代數式", "一元一次方程式", "二元一次聯立方程式",
            "直角坐標與二元一次方程式的圖形", "比例", "正比與反比", "幾何圖形",
            "三角形的基本性質", "平行與截線", "三角形與多邊形", "圓形",
            "統計圖表與資料分析"
        ]
    },
    {
        publisher: "南一",
        subject: "數學",
        grade: "7B",
        chapters: [
            "乘法公式與多項式", "平方根與畢氏定理", "因式分解", "一元二次方程式",
            "數列與等差級數", "幾何證明", "相似形", "圓的性質", "二次函數",
            "機率", "統計與抽樣"
        ]
    },
    // 自然科目
    {
        publisher: "南一",
        subject: "自然",
        grade: "7A",
        chapters: [
            "探究自然的方法", "物質的組成", "物質的變化", "能量的形式與轉換",
            "生物與環境", "生物體的構造與功能", "遺傳與演化", "地球的構造",
            "地球的歷史", "天氣與氣候", "宇宙與天體", "科技與生活"
        ]
    },
    // 地理科目
    {
        publisher: "翰林",
        subject: "地理",
        grade: "7A",
        chapters: [
            "地理學的基本概念", "地圖與地理資訊", "地形", "氣候", "水文",
            "土壤與生物", "人口", "聚落", "交通", "產業", "環境問題",
            "區域發展"
        ]
    },
    // 歷史科目
    {
        publisher: "翰林",
        subject: "歷史",
        grade: "7A",
        chapters: [
            "史前時代", "古代文明", "中古時代", "近代歐洲", "近代亞洲",
            "現代世界", "臺灣史", "中國史", "世界史", "歷史與文化",
            "歷史與社會", "歷史與科技"
        ]
    },
    // 公民科目
    {
        publisher: "翰林",
        subject: "公民",
        grade: "7A",
        chapters: [
            "個人與社會", "家庭生活", "學校生活", "社區生活", "國家與政府",
            "民主政治", "法律與生活", "經濟與生活", "國際關係", "永續發展",
            "科技與社會", "文化與生活"
        ]
    }
];

// 插入章節資料
chapters.forEach((subjectData, index) => {
    subjectData.chapters.forEach((chapterName, chapterIndex) => {
        db.chapters.insertOne({
            publisher: subjectData.publisher,
            subject: subjectData.subject,
            grade: subjectData.grade,
            chapter: chapterName,
            description: `${subjectData.subject} - ${subjectData.grade} - ${chapterName}`,
            order: chapterIndex + 1,
            created_at: new Date(),
            updated_at: new Date()
        });
    });
});

// 建立知識點資料（為每個章節建立基本知識點）
db.chapters.find({}).forEach(function(chapter) {
    db.knowledge_points.insertOne({
        subject: chapter.subject,
        grade: chapter.grade,
        chapter: chapter.chapter,
        name: `${chapter.chapter} - 基本概念`,
        description: `${chapter.chapter} 的基本概念與應用`,
        order: 1,
        created_at: new Date(),
        updated_at: new Date()
    });
    
    db.knowledge_points.insertOne({
        subject: chapter.subject,
        grade: chapter.grade,
        chapter: chapter.chapter,
        name: `${chapter.chapter} - 進階應用`,
        description: `${chapter.chapter} 的進階應用與練習`,
        order: 2,
        created_at: new Date(),
        updated_at: new Date()
    });
});

print("章節資料初始化完成！");
print(`共插入 ${db.chapters.countDocuments()} 個章節`);
print(`共插入 ${db.knowledge_points.countDocuments()} 個知識點`); 