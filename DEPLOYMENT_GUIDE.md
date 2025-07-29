# InULearning 部署指南

## 🚀 一鍵啟動系統

InULearning 提供了完整的一鍵啟動解決方案，支援在不同裝置間快速部署。

## 📋 系統需求

### 最低需求
- **作業系統**: Linux、macOS 或 Windows (WSL)
- **記憶體**: 4GB RAM (建議 8GB+)
- **磁碟空間**: 10GB 可用空間
- **Docker**: 版本 20.10+
- **Docker Compose**: 版本 2.0+

### 支援的環境
- ✅ Linux (Ubuntu, CentOS, Debian 等)
- ✅ macOS (Intel & Apple Silicon)
- ✅ Windows 10/11 (WSL2)
- ✅ Windows (Git Bash)

## 🛠️ 快速開始

### 1. 首次部署

```bash
# 下載或複製專案到本地
cd InULearning_V1

# 一鍵啟動（完整部署）
./start.sh
```

### 2. 後續使用

```bash
# 快速重啟（系統已配置完成時）
./restart.sh

# 系統診斷檢查
./check.sh
```

## 📜 腳本說明

### `start.sh` - 完整部署腳本
**用途**: 首次部署或完全重新部署系統

**功能**:
- ✅ 自動檢測系統環境 (Linux/macOS/Windows)
- ✅ 驗證 Docker 環境和版本
- ✅ 自動清理舊環境
- ✅ 建立必要的目錄結構
- ✅ 自動生成 `.env` 配置檔案
- ✅ 拉取並構建所有服務
- ✅ 智能等待服務就緒
- ✅ 自動初始化測試資料
- ✅ 全面的健康檢查
- ✅ 連通性測試

**適用場景**:
- 首次在新裝置上部署
- 系統出現嚴重問題需要重置
- 更新代碼後需要重新構建

### `restart.sh` - 快速重啟腳本
**用途**: 在系統已配置完成後快速重啟

**功能**:
- 🔄 快速停止所有服務
- 🔄 重新啟動所有容器
- 🔄 基本狀態檢查

**適用場景**:
- 日常開發中的快速重啟
- 服務異常時的快速恢復
- 配置檔案修改後的重載

### `check.sh` - 系統診斷腳本
**用途**: 診斷系統狀態和問題排查

**功能**:
- 🔍 Docker 環境檢查
- 🔍 容器狀態監控
- 🔍 端口占用檢查
- 🔍 服務連通性測試
- 🔍 數據庫連接驗證
- 🔍 錯誤日誌分析
- 🔍 系統資源監控
- 🔍 測試帳號驗證

**適用場景**:
- 系統出現問題時的診斷
- 定期健康檢查
- 故障排除

## 🌐 服務訪問地址

部署完成後，可以通過以下地址訪問各個服務：

### 前端應用
- 🎓 **學生端**: http://localhost:8080
- 👨‍💼 **管理員端**: http://localhost:8081
- 👪 **家長端**: http://localhost:8082
- 👨‍🏫 **教師端**: http://localhost:8083

### 後端服務
- 🔐 **認證服務**: http://localhost:8001
- 📚 **題庫服務**: http://localhost:8002
- 📖 **學習服務**: http://localhost:8003

### 數據庫服務
- 🗄️ **PostgreSQL**: localhost:5432
- 📊 **MongoDB**: localhost:27017
- 🚀 **Redis**: localhost:6379
- 📦 **MinIO**: http://localhost:9000 (Console: http://localhost:9001)

## 👤 測試帳號

所有測試帳號的密碼都是 `password123`：

| 身份 | 帳號 | 前端地址 |
|------|------|----------|
| 👨‍🎓 學生 | student01@test.com | http://localhost:8080 |
| 👨‍🏫 教師 | teacher01@test.com | http://localhost:8083 |
| 👪 家長 | parent01@test.com | http://localhost:8082 |
| 👨‍💼 管理員 | admin01@test.com | http://localhost:8081 |

## 🔧 常用管理命令

```bash
# 查看所有服務狀態
docker compose ps

# 查看特定服務日誌
docker compose logs -f [服務名]

# 重啟特定服務
docker compose restart [服務名]

# 停止所有服務
docker compose down

# 進入容器進行調試
docker compose exec [服務名] bash

# 查看系統資源使用
docker stats
```

## 🚨 故障排除

### 常見問題

#### 1. 端口被占用
```bash
# 檢查端口占用
netstat -tuln | grep :8080

# 或使用系統檢查腳本
./check.sh
```

#### 2. Docker 權限問題
```bash
# Linux 系統添加用戶到 docker 組
sudo usermod -aG docker $USER
# 重新登入或重啟終端
```

#### 3. 記憶體不足
```bash
# 檢查系統資源
free -h
df -h

# 清理 Docker 資源
docker system prune -a --volumes
```

#### 4. 服務啟動失敗
```bash
# 查看詳細日誌
docker compose logs [服務名]

# 重新構建特定服務
docker compose build [服務名]
docker compose up -d [服務名]
```

### 診斷流程

1. **首先運行系統檢查**:
   ```bash
   ./check.sh
   ```

2. **查看問題服務的日誌**:
   ```bash
   docker compose logs -f [問題服務名]
   ```

3. **嘗試重啟問題服務**:
   ```bash
   docker compose restart [問題服務名]
   ```

4. **如果問題持續，完全重新部署**:
   ```bash
   ./start.sh
   ```

## 🔄 在不同裝置間遷移

### 1. 備份配置
```bash
# 備份環境配置
cp .env .env.backup

# 備份數據（可選）
docker compose exec postgres pg_dump -U aipe-tester inulearning > backup.sql
```

### 2. 在新裝置上部署
```bash
# 複製專案檔案到新裝置
# 運行一鍵啟動
./start.sh
```

### 3. 恢復配置（如需要）
```bash
# 恢復環境配置
cp .env.backup .env

# 恢復數據（可選）
docker compose exec -T postgres psql -U aipe-tester -d inulearning < backup.sql
```

## 📈 性能優化建議

### Docker 配置優化
```bash
# 增加 Docker 可用記憶體（Docker Desktop）
# 設置 -> Resources -> Memory: 至少 4GB

# 啟用 BuildKit 加速構建
export DOCKER_BUILDKIT=1
```

### 系統優化
```bash
# Linux 系統優化 Docker 性能
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 🆘 技術支援

如果遇到無法解决的問題，請提供以下資訊：

1. 作業系統和版本
2. Docker 和 Docker Compose 版本
3. `./check.sh` 的完整輸出
4. 相關服務的日誌輸出
5. 錯誤發生的具體步驟

---

## 📝 版本歷史

- **v1.1.0**: 完整的一鍵啟動解決方案
  - 新增智能環境檢測
  - 新增自動測試資料初始化
  - 新增全面的健康檢查
  - 新增快速重啟和診斷腳本

- **v1.0.0**: 基礎啟動腳本
  - 基本的 Docker Compose 啟動功能 