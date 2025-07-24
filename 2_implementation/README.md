# InULearning 統一虛擬環境

這個目錄包含了一個統一的 Python 虛擬環境，用於管理所有後端服務的依賴。

## 🚀 快速開始

### 1. 啟動虛擬環境

```bash
# 進入 2_implementation 目錄
cd InULearning_V1/2_implementation

# 啟動虛擬環境
source venv/bin/activate
```

### 2. 安裝依賴

```bash
# 安裝所有依賴
pip install -r requirements.txt
```

### 3. 啟動所有服務

```bash
# 使用啟動腳本
./start_services.sh
```

### 4. 停止所有服務

```bash
# 使用停止腳本
./stop_services.sh
```

## 📁 目錄結構

```
2_implementation/
├── venv/                    # 統一虛擬環境
├── requirements.txt         # 統一依賴檔案
├── start_services.sh        # 服務啟動腳本
├── stop_services.sh         # 服務停止腳本
├── backend/                 # 後端服務
│   ├── auth-service/        # 認證服務 (Port 8000)
│   ├── learning-service/    # 學習服務 (Port 8001)
│   └── question-bank-service/ # 題庫服務 (Port 8002)
└── frontend/               # 前端應用
```

## 🔧 服務管理

### 手動啟動服務

```bash
# 啟動認證服務
cd backend/auth-service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 啟動學習服務
cd backend/learning-service
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# 啟動題庫服務
cd backend/question-bank-service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 使用 Screen 管理

```bash
# 查看所有 screen 會話
screen -ls

# 進入特定服務的 screen 會話
screen -r auth-service
screen -r learning-service
screen -r question-bank-service

# 從 screen 會話中退出 (保持服務運行)
# 按 Ctrl+A，然後按 D

# 停止特定服務
screen -S auth-service -X quit
```

## 🌐 API 端點

### 認證服務 (Port 8000)
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/health

### 學習服務 (Port 8001)
- **API 文檔**: http://localhost:8001/docs
- **健康檢查**: http://localhost:8001/health

### 題庫服務 (Port 8002)
- **API 文檔**: http://localhost:8002/docs
- **健康檢查**: http://localhost:8002/health

## 🧪 測試

### 使用 Postman 測試

1. **建立 Collection**: "InULearning API Tests"
2. **設定環境變數**:
   - `base_url_auth`: `http://localhost:8000`
   - `base_url_learning`: `http://localhost:8001`
   - `base_url_question`: `http://localhost:8002`
   - `access_token`: (登入後自動填入)

3. **測試流程**:
   - 先測試健康檢查端點
   - 註冊新用戶
   - 登入獲取 Token
   - 測試需要認證的 API

### 健康檢查測試

```bash
# 測試認證服務
curl http://localhost:8000/health

# 測試學習服務
curl http://localhost:8001/health

# 測試題庫服務
curl http://localhost:8002/health
```

## 🔍 故障排除

### 常見問題

1. **Port 已被佔用**
   ```bash
   # 查看端口使用情況
   sudo netstat -tulpn | grep :8000
   
   # 殺死佔用端口的進程
   sudo kill -9 <PID>
   ```

2. **虛擬環境未啟動**
   ```bash
   # 檢查虛擬環境狀態
   echo $VIRTUAL_ENV
   
   # 重新啟動虛擬環境
   source venv/bin/activate
   ```

3. **依賴安裝失敗**
   ```bash
   # 更新 pip
   pip install --upgrade pip
   
   # 重新安裝依賴
   pip install -r requirements.txt --force-reinstall
   ```

4. **資料庫連接問題**
   ```bash
   # 檢查 PostgreSQL 狀態
   sudo systemctl status postgresql
   
   # 啟動 PostgreSQL
   sudo systemctl start postgresql
   ```

## 📝 開發指南

### 新增依賴

1. 編輯 `requirements.txt`
2. 安裝新依賴：`pip install <package>`
3. 更新 requirements.txt：`pip freeze > requirements.txt`

### 開發新服務

1. 在 `backend/` 目錄下建立新服務
2. 確保使用統一的虛擬環境
3. 更新啟動腳本以包含新服務

### 版本控制

```bash
# 忽略虛擬環境檔案
echo "venv/" >> .gitignore

# 提交依賴變更
git add requirements.txt
git commit -m "Update dependencies"
```

## 🎯 最佳實踐

1. **始終使用虛擬環境**: 避免全域套件衝突
2. **定期更新依賴**: 保持套件版本最新
3. **使用啟動腳本**: 簡化服務管理
4. **監控服務狀態**: 定期檢查健康檢查端點
5. **備份重要資料**: 定期備份資料庫和配置檔案 