# 🐳 InULearning Docker 快速啟動指南

## 📋 系統需求

- **Docker**: 版本 20.10 或更高
- **Docker Compose**: 版本 2.0 或更高
- **系統記憶體**: 至少 4GB RAM
- **磁碟空間**: 至少 2GB 可用空間

## 🚀 一鍵啟動

### 步驟 1：克隆並進入專案目錄
```bash
cd /home/bheadwei/clamdownVersion_v1/InULearning_V1
```

### 步驟 2：執行啟動腳本
```bash
# 給予執行權限
chmod +x start.sh

# 啟動系統
./start.sh
```

### 步驟 3：等待服務啟動（約 2-3 分鐘）
腳本會自動：
- 檢查 Docker 環境
- 創建必要目錄
- 複製環境配置
- 建立並啟動所有容器
- 檢查服務健康狀態

## 🌐 服務訪問地址

### 前端應用
- **學生端**: http://localhost:8080
- **管理員端**: http://localhost:8081  
- **家長端**: http://localhost:8082
- **教師端**: http://localhost:8083

### API 服務
- **認證服務**: http://localhost:8001
- **題庫服務**: http://localhost:8002
- **學習服務**: http://localhost:8003

### 資料庫
- **PostgreSQL**: localhost:5432
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379
- **MinIO**: http://localhost:9000 (Console: http://localhost:9001)

## 🎉 最新修正 (2024-12-19)

### ✅ 已修正的問題

1. **統一登入頁面**
   - 移除重複的登入頁面
   - 統一使用根目錄的 `login.html` 
   - 所有前端應用都會重定向到統一登入頁面

2. **練習頁面功能修正**
   - 修正章節選擇功能，現在可以根據年級、版本、科目動態載入章節
   - 修正「檢查題庫」和「開始練習」按鈕功能
   - 添加認證檢查，確保只有登入的學生可以訪問

3. **路徑和資源修正**
   - 修正章節資料檔案路徑：`/files/三版本科目章節.json`
   - 優化 JavaScript 初始化流程
   - 添加錯誤處理和使用者提示

## 🧪 測試新功能

### 測試練習系統流程

#### 1. 登入系統
```bash
# 開啟瀏覽器訪問
http://localhost:8080
```

**重要**: 現在所有未登入的訪問都會自動重定向到 `http://localhost:8080/login.html`

**測試帳號**:
- 學生帳號: `student01@test.com` / `password123`
- 教師帳號: `teacher01@test.com` / `password123`

#### 2. 進入練習頁面
登入成功後會自動進入學生端首頁，點擊「開始練習」或直接訪問：
```
http://localhost:8080/pages/exercise.html
```

#### 3. 測試新的選擇邏輯

**步驟 3.1：測試年級選擇**
- [ ] 選擇「七年級上學期」
- [ ] 選擇「八年級下學期」
- [ ] 選擇「九年級上學期」

**步驟 3.2：測試版本選擇**
- [ ] 選擇「南一」
- [ ] 選擇「康軒」
- [ ] 選擇「翰林」

**步驟 3.3：測試科目選擇**
- [ ] 選擇「國文」
- [ ] 選擇「數學」
- [ ] 選擇「英文」

**步驟 3.4：測試章節動態載入 ⭐ 新功能**
- [ ] 選擇完前三個條件後，觀察章節選項是否自動更新
- [ ] 更改任一條件，確認章節重新載入
- [ ] 檢查 F12 開發者工具 Console，應該顯示「章節資料載入成功」

**步驟 3.5：測試題數驗證**
- [ ] 輸入 `5` 題，點擊「檢查題庫」
- [ ] 輸入 `30` 題，觀察題庫檢查結果
- [ ] 輸入 `0` 或 `51`，確認錯誤提示

**步驟 3.6：測試按鈕功能 ⭐ 新功能**
- [ ] 「檢查題庫」按鈕現在可以點擊
- [ ] 「開始練習」按鈕在檢查通過後可以點擊

#### 4. 測試完整考試流程

**步驟 4.1：開始練習**
- 完成所有選項設置
- 點擊「開始練習」
- 確認跳轉到 `exam.html`

**步驟 4.2：考試頁面測試**
- [ ] 檢查題目是否正確顯示
- [ ] 測試「上一題」、「下一題」功能
- [ ] 檢查計時器是否運作
- [ ] 作答到最後一題，確認顯示「提交」按鈕

**步驟 4.3：結果頁面測試**
- [ ] 提交後自動跳轉到 `result.html`
- [ ] 檢查分數和統計資訊
- [ ] 檢查詳細題目分析

**步驟 4.4：歷史記錄測試**
- [ ] 訪問 `history.html`
- [ ] 確認剛才的練習記錄已儲存
- [ ] 檢查記錄包含：年級、版本、科目、章節資訊

## 🔧 開發者工具

### 查看服務狀態
```bash
# 查看所有服務狀態
docker compose ps

# 查看特定服務日誌
docker compose logs -f student-frontend
docker compose logs -f learning-service
```

### 進入容器除錯
```bash
# 進入學生端前端容器
docker compose exec student-frontend sh

# 進入 PostgreSQL 容器
docker compose exec postgres psql -U aipe-tester -d inulearning

# 進入 MongoDB 容器
docker compose exec mongodb mongosh -u aipe-tester -p aipe-tester
```

### 重啟特定服務
```bash
# 重啟前端服務
docker compose restart student-frontend

# 重啟學習服務
docker compose restart learning-service

# 重建並重啟特定服務
docker compose up --build -d student-frontend
```

## 📊 監控和除錯

### 檢查資料庫連接
```bash
# 檢查 PostgreSQL
docker compose exec postgres pg_isready -U aipe-tester -d inulearning

# 檢查 MongoDB
docker compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# 檢查 Redis
docker compose exec redis redis-cli ping
```

### 檢查 API 健康狀態
```bash
# 檢查認證服務
curl http://localhost:8001/health

# 檢查題庫服務  
curl http://localhost:8002/health

# 檢查學習服務
curl http://localhost:8003/health
```

### 查看前端文件
```bash
# 查看學生端前端文件
docker compose exec student-frontend ls -la /usr/share/nginx/html/

# 查看 nginx 配置
docker compose exec student-frontend cat /etc/nginx/conf.d/default.conf
```

## 🛑 停止系統

### 停止所有服務
```bash
# 停止服務但保留資料
docker compose down

# 停止服務並刪除資料卷
docker compose down -v

# 或使用停止腳本
./stop.sh
```

### 清理系統
```bash
# 清理未使用的容器和映像
docker system prune -f

# 清理所有相關資源
docker compose down -v --remove-orphans
docker system prune -a -f
```

## 🐛 常見問題解決

### 問題 1：端口被占用
```bash
# 檢查端口使用情況
sudo netstat -tulpn | grep :8080

# 停止占用端口的程序
sudo fuser -k 8080/tcp
```

### 問題 2：容器啟動失敗
```bash
# 查看詳細錯誤日誌
docker compose logs [服務名]

# 重新建立容器
docker compose up --build --force-recreate -d [服務名]
```

### 問題 3：資料庫連接失敗
```bash
# 檢查資料庫容器狀態
docker compose ps postgres mongodb

# 重啟資料庫服務
docker compose restart postgres mongodb

# 等待健康檢查通過
docker compose exec postgres pg_isready -U aipe-tester -d inulearning
```

### 問題 4：前端文件未更新
```bash
# 重新建立前端容器
docker compose up --build --no-deps -d student-frontend

# 清除瀏覽器快取
# 按 Ctrl+Shift+R 強制重新載入
```

## 📝 測試檢查清單

### ✅ 基本功能測試
- [ ] 系統成功啟動（所有服務 running）
- [ ] 學生端可正常訪問 (http://localhost:8080)
- [ ] 登入功能正常
- [ ] 練習頁面載入成功

### ✅ 新功能測試  
- [ ] 年級選項正確（七年級上/下學期等）
- [ ] 版本選項正確（南一/康軒/翰林）
- [ ] 章節動態載入功能
- [ ] 題數驗證功能
- [ ] 完整考試流程 (exercise → exam → result)
- [ ] 歷史記錄儲存功能

### ✅ API 整合測試
- [ ] 題庫檢查 API 正常
- [ ] 題目獲取 API 正常  
- [ ] 結果提交 API 正常
- [ ] PostgreSQL 記錄儲存正常

## 🎉 成功標準

當以下所有項目都通過時，表示系統運行正常：

1. **服務啟動**: 所有 Docker 容器狀態為 `running`
2. **前端訪問**: 能夠正常訪問學生端前端
3. **登入功能**: 能夠使用測試帳號登入
4. **練習流程**: 能夠完成完整的練習流程
5. **資料儲存**: 練習記錄能夠正確儲存到資料庫
6. **API 回應**: 所有 API 端點回應正常

---

## 📞 需要協助？

如果遇到問題，請：

1. **檢查日誌**: 使用 `docker compose logs -f [服務名]` 查看詳細錯誤
2. **確認狀態**: 使用 `docker compose ps` 確認所有服務運行正常
3. **重啟服務**: 嘗試重啟有問題的特定服務
4. **回報問題**: 提供具體的錯誤訊息和重現步驟

**祝您測試順利！** 🚀