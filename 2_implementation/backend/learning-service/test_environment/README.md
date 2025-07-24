# InULearning Learning Service 測試環境

本目錄包含用於測試 learning-service 的完整測試環境和工具。

## 📁 目錄結構

```
test_environment/
├── setup_test_env.sh      # 測試環境設置腳本
├── run_tests.sh           # 測試執行腳本
├── test_api.py            # API 測試腳本
├── init_test_db.sql       # 測試資料庫初始化腳本
└── README.md              # 本文件
```

## 🚀 快速開始

### 1. 設置測試環境

```bash
# 設置虛擬環境和依賴
chmod +x test_environment/setup_test_env.sh
./test_environment/setup_test_env.sh
```

### 2. 啟動 PostgreSQL 資料庫

```bash
# 使用 Docker 啟動 PostgreSQL
docker run -d \
  --name postgres-test \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=inulearning_test \
  -p 5432:5432 \
  postgres:13

# 或者使用本地 PostgreSQL
sudo systemctl start postgresql
```

### 3. 初始化測試資料庫

```bash
# 創建測試資料庫和表
psql -U postgres -f test_environment/init_test_db.sql
```

### 4. 運行測試

```bash
# 執行完整測試套件
chmod +x test_environment/run_tests.sh
./test_environment/run_tests.sh
```

## 🧪 測試類型

### 1. 環境測試 (`test_setup.py`)

測試開發環境配置：
- Python 模組導入
- 應用程式配置
- 環境變數設置
- 資料庫連接
- 服務初始化

### 2. 單元測試 (`pytest`)

測試核心功能邏輯：
- 資料模型驗證
- 服務層邏輯
- 工具函數
- 錯誤處理

### 3. API 測試 (`test_api.py`)

測試 HTTP 端點：
- 健康檢查
- 練習創建
- 答案提交
- 會話管理
- 學習建議
- 趨勢分析

### 4. 覆蓋率測試

檢查代碼覆蓋率：
- 生成 HTML 報告
- 終端覆蓋率顯示
- 缺失覆蓋率分析

## 📊 測試結果

### 預期結果

1. **環境測試**: 所有檢查項目通過
2. **單元測試**: 測試通過率 > 80%
3. **API 測試**: 核心端點正常響應
4. **覆蓋率**: 核心功能覆蓋率 > 85%

### 查看結果

- **HTML 覆蓋率報告**: `htmlcov/index.html`
- **API 文檔**: http://localhost:8002/docs
- **健康檢查**: http://localhost:8002/health

## 🔧 故障排除

### 常見問題

1. **虛擬環境問題**
   ```bash
   # 重新創建虛擬環境
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **資料庫連接問題**
   ```bash
   # 檢查 PostgreSQL 狀態
   sudo systemctl status postgresql
   
   # 檢查資料庫連接
   psql -U postgres -d inulearning_test -c "SELECT 1;"
   ```

3. **服務啟動問題**
   ```bash
   # 檢查端口佔用
   lsof -i :8002
   
   # 手動啟動服務
   source venv/bin/activate
   python run.py
   ```

4. **依賴問題**
   ```bash
   # 更新依賴
   pip install --upgrade -r requirements.txt
   
   # 檢查依賴衝突
   pip check
   ```

### 調試模式

啟用調試模式以獲取詳細錯誤信息：

```bash
# 設置環境變數
export DEBUG=true
export LOG_LEVEL=DEBUG

# 啟動服務
python run.py
```

## 📋 測試檢查清單

### 環境設置
- [ ] Python 3.8+ 已安裝
- [ ] 虛擬環境已創建
- [ ] 依賴已安裝
- [ ] 環境變數已配置
- [ ] PostgreSQL 已啟動
- [ ] 測試資料庫已初始化

### 功能測試
- [ ] 模組導入正常
- [ ] 應用程式啟動成功
- [ ] 資料庫連接正常
- [ ] API 端點響應正常
- [ ] 認證機制正常
- [ ] 錯誤處理正常

### 性能測試
- [ ] API 響應時間 < 500ms
- [ ] 資料庫查詢效率
- [ ] 記憶體使用正常
- [ ] 併發處理能力

## 🔄 持續測試

### 自動化測試

```bash
# 設置 Git Hooks (可選)
cp test_environment/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### CI/CD 整合

測試腳本已準備好與 CI/CD 系統整合：

```yaml
# GitHub Actions 範例
- name: Run Tests
  run: |
    chmod +x test_environment/setup_test_env.sh
    ./test_environment/setup_test_env.sh
    ./test_environment/run_tests.sh
```

## 📞 支援

如遇到問題，請檢查：

1. 系統日誌
2. 應用程式日誌
3. 資料庫日誌
4. 網路連接狀態

或聯繫開發團隊獲取支援。 