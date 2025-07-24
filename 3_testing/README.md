# InULearning_V1 統一測試套件

本資料夾包含 InULearning_V1 專案的所有測試檔案，統一管理以確保測試的一致性和可維護性。

## 📁 測試結構

```
unified_tests/
├── README.md                    # 本文件
├── conftest.py                  # pytest 配置和共用 fixtures
├── requirements-test.txt         # 測試依賴套件
├── run_all_tests.py             # 執行所有測試的主腳本
├── utils/                       # 測試工具和輔助函數
│   ├── __init__.py
│   ├── test_helpers.py          # 測試輔助函數
│   └── api_client.py            # API 測試客戶端
├── unit_tests/                  # 單元測試
│   ├── __init__.py
│   ├── test_auth_service.py     # 認證服務單元測試
│   ├── test_learning_service.py # 學習服務單元測試
│   ├── test_question_bank.py    # 題庫服務單元測試
│   └── test_ai_analysis.py      # AI 分析服務單元測試
├── integration_tests/           # 整合測試
│   ├── __init__.py
│   ├── test_database.py         # 資料庫整合測試
│   ├── test_api_integration.py  # API 整合測試
│   └── test_service_communication.py # 服務間通訊測試
├── e2e_tests/                   # 端到端測試
│   ├── __init__.py
│   ├── test_user_flow.py        # 用戶流程測試
│   └── test_system_workflow.py  # 系統工作流程測試
└── performance_tests/           # 效能測試
    ├── __init__.py
    ├── test_api_performance.py  # API 效能測試
    └── test_database_performance.py # 資料庫效能測試
```

## 🚀 快速開始

### 1. 安裝測試依賴

```bash
cd InULearning_V1/unified_tests
pip install -r requirements-test.txt
```

### 2. 執行所有測試

```bash
python run_all_tests.py
```

### 3. 執行特定測試類別

```bash
# 執行單元測試
pytest unit_tests/ -v

# 執行整合測試
pytest integration_tests/ -v

# 執行端到端測試
pytest e2e_tests/ -v

# 執行效能測試
pytest performance_tests/ -v
```

### 4. 執行特定服務測試

```bash
# 測試認證服務
pytest unit_tests/test_auth_service.py -v

# 測試學習服務
pytest unit_tests/test_learning_service.py -v

# 測試題庫服務
pytest unit_tests/test_question_bank.py -v

# 測試 AI 分析服務
pytest unit_tests/test_ai_analysis.py -v
```

## 📊 測試報告

測試執行後會生成以下報告：

- **HTML 報告**: `test_reports/report.html`
- **覆蓋率報告**: `test_reports/coverage.html`
- **JSON 報告**: `test_reports/report.json`

## 🔧 測試配置

### 環境變數

測試使用以下環境變數（可通過 `.env` 檔案設定）：

```bash
# 資料庫配置
DATABASE_URL=postgresql://user:password@localhost:5432/inulearning_test
MONGODB_URL=mongodb://localhost:27017/inulearning_test
REDIS_URL=redis://localhost:6379/1

# 服務配置
AUTH_SERVICE_URL=http://localhost:8001
LEARNING_SERVICE_URL=http://localhost:8002
QUESTION_BANK_SERVICE_URL=http://localhost:8003
AI_ANALYSIS_SERVICE_URL=http://localhost:8004

# 測試配置
TEST_MODE=true
LOG_LEVEL=INFO
```

### pytest 配置

主要配置在 `conftest.py` 中：

- 測試資料夾設定
- 共用 fixtures
- 測試資料庫配置
- 日誌配置

## 🧪 測試類型說明

### 單元測試 (Unit Tests)
- 測試個別函數和類別
- 使用 mock 隔離外部依賴
- 快速執行，高覆蓋率

### 整合測試 (Integration Tests)
- 測試模組間的互動
- 測試資料庫操作
- 測試 API 端點

### 端到端測試 (E2E Tests)
- 測試完整的用戶流程
- 測試跨服務的互動
- 模擬真實使用場景

### 效能測試 (Performance Tests)
- 測試 API 回應時間
- 測試資料庫查詢效能
- 測試系統負載能力

## 📝 撰寫新測試

### 1. 遵循命名慣例

```python
# 檔案命名: test_<module_name>.py
# 函數命名: test_<function_name>_<scenario>
def test_user_registration_success():
    """測試用戶註冊成功場景"""
    pass

def test_user_registration_invalid_email():
    """測試用戶註冊無效郵件場景"""
    pass
```

### 2. 使用 fixtures

```python
import pytest

@pytest.fixture
def test_user_data():
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }

def test_create_user(test_user_data):
    # 使用 fixture 提供的測試資料
    pass
```

### 3. 使用參數化測試

```python
import pytest

@pytest.mark.parametrize("email,expected", [
    ("valid@example.com", True),
    ("invalid-email", False),
    ("", False),
])
def test_email_validation(email, expected):
    # 測試多個輸入值
    pass
```

## 🔍 除錯技巧

### 1. 啟用詳細輸出

```bash
pytest -v -s --tb=short
```

### 2. 執行特定測試

```bash
pytest -k "test_user_registration" -v
```

### 3. 生成覆蓋率報告

```bash
pytest --cov=src --cov-report=html
```

### 4. 並行執行測試

```bash
pytest -n auto
```

## 📋 測試檢查清單

在提交程式碼前，請確保：

- [ ] 所有新功能都有對應的測試
- [ ] 測試覆蓋率達到 80% 以上
- [ ] 所有測試都能通過
- [ ] 測試執行時間在合理範圍內
- [ ] 測試報告已生成並檢查

## 🐛 常見問題

### Q: 測試失敗怎麼辦？
A: 檢查錯誤訊息，確認服務是否正在運行，環境變數是否正確設定。

### Q: 如何跳過某些測試？
A: 使用 `@pytest.mark.skip` 或 `@pytest.mark.skipif` 裝飾器。

### Q: 如何設定測試資料庫？
A: 使用 Docker 或本地資料庫，確保測試資料庫與開發資料庫分離。

## 📞 支援

如有測試相關問題，請：

1. 檢查本文件
2. 查看測試日誌
3. 聯繫開發團隊

---

**注意**: 本測試套件遵循 `.cursorrules` 和產品開發流程使用說明書的規範。 