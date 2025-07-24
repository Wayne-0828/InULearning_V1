# InULearning_V1 統一測試索引

本檔案列出了所有整合的測試檔案及其來源。

## 單元測試 (Unit Tests)

### 認證服務 (Auth Service)
- `unit_tests/test_auth_api.py` - 來自 auth-service/test_api.py
- `unit_tests/test_auth_basic.py` - 來自 auth-service/test_basic.py
- `unit_tests/test_auth_startup.py` - 來自 auth-service/test_startup.py
- `unit_tests/test_auth_integration.py` - 來自 auth-service/tests/test_auth.py

### 學習服務 (Learning Service)
- `unit_tests/test_learning_setup.py` - 來自 learning-service/test_setup.py
- `unit_tests/test_learning_main.py` - 來自 learning-service/tests/test_main.py
- `unit_tests/test_learning_env_setup.py` - 來自 learning-service/test_environment/test_setup.py
- `unit_tests/test_learning_env_api.py` - 來自 learning-service/test_environment/test_api.py

### 題庫服務 (Question Bank Service)
- `unit_tests/test_question_bank_basic.py` - 來自 question-bank-service/test_basic.py
- `unit_tests/test_question_bank_integration.py` - 來自 question-bank-service/tests/test_question_bank.py

### AI 分析服務 (AI Analysis Service)
- `unit_tests/test_ai_analysis_basic.py` - 來自 ai-analysis-service/tests/test_basic.py
- `unit_tests/test_ai_vector_service.py` - 來自 ai-analysis-service/tests/test_vector_service.py
- `unit_tests/test_ai_trend_analysis.py` - 來自 ai-analysis-service/tests/test_trend_analysis.py
- `unit_tests/test_ai_learning_recommendation.py` - 來自 ai-analysis-service/tests/test_learning_recommendation.py
- `unit_tests/test_ai_weakness_analysis.py` - 來自 ai-analysis-service/tests/test_weakness_analysis.py

### 共享模組 (Shared Modules)
- `unit_tests/test_shared_models.py` - 來自 shared/models/test_models.py
- `unit_tests/test_models_simple.py` - 來自 test_models_simple.py

## 整合測試 (Integration Tests)

- `integration_tests/test_database_integration.py` - 來自 test_database_integration.py
- `integration_tests/test_data_consistency.py` - 來自 test_data_consistency.py
- `integration_tests/test_ai_api_integration.py` - 來自 ai-analysis-service/tests/test_api_integration.py

## 端到端測試 (E2E Tests)

- `e2e_tests/test_user_flow.py` - 用戶流程測試
- `e2e_tests/test_system_workflow.py` - 系統工作流程測試

## 效能測試 (Performance Tests)

- `performance_tests/test_api_performance.py` - API 效能測試
- `performance_tests/test_database_performance.py` - 資料庫效能測試

## 執行測試

```bash
# 執行所有測試
python run_all_tests.py

# 執行特定類型測試
python run_all_tests.py --test-types unit
python run_all_tests.py --test-types integration
python run_all_tests.py --test-types e2e
python run_all_tests.py --test-types performance

# 執行特定服務測試
pytest unit_tests/test_auth_*.py -v
pytest unit_tests/test_learning_*.py -v
pytest unit_tests/test_question_bank_*.py -v
pytest unit_tests/test_ai_*.py -v
```

## 注意事項

1. 所有測試檔案已整合到統一測試資料夾中
2. 導入路徑已更新以適應新的檔案結構
3. 測試配置統一在 conftest.py 中管理
4. 測試報告統一生成到 test_reports/ 目錄
