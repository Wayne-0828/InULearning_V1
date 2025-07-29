# InULearning 快速開始指南

## 🚀 一鍵啟動

```bash
# 1. 進入專案目錄
cd InULearning_V1

# 2. 啟動系統
./start.sh

# 3. 測試系統
./test_system.sh
```

## 📋 系統功能

### ✅ 已實現功能

1. **學生註冊登入** - 完整的用戶認證系統
2. **條件選擇練習** - 根據年級、科目、章節選擇練習範圍
3. **題目回傳** - 根據條件回傳符合的題目
4. **自動批改** - 即時批改答案並顯示詳解
5. **學習紀錄** - 完整記錄學習歷程

### 🔧 技術架構

- **前端**: HTML/CSS/JavaScript (學生端)
- **後端**: FastAPI (微服務架構)
- **資料庫**: PostgreSQL (用戶資料) + MongoDB (題庫)
- **快取**: Redis
- **檔案儲存**: MinIO
- **反向代理**: Nginx

## 🌐 訪問地址

| 服務 | 地址 | 說明 |
|------|------|------|
| 學生端前端 | http://localhost:8080 | 主要學習介面 |
| 認證服務 | http://localhost:8001 | API 文檔 |
| 題庫服務 | http://localhost:8002 | API 文檔 |
| 學習服務 | http://localhost:8003 | API 文檔 |

## 🧪 測試帳號

```
學生帳號: student@test.com / password123
教師帳號: teacher@test.com / password123
```

## 📝 使用流程

1. **註冊/登入**: 使用測試帳號登入系統
2. **選擇練習**: 選擇年級、科目、章節
3. **開始練習**: 系統會根據條件提供題目
4. **作答**: 選擇答案並提交
5. **查看結果**: 系統會顯示正確答案和詳解
6. **學習紀錄**: 所有練習都會被記錄

## 🔧 管理命令

```bash
# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f [服務名]

# 停止系統
./stop.sh

# 重啟特定服務
docker-compose restart [服務名]
```

## 🚨 故障排除

### 常見問題

1. **端口被佔用**: 修改 `docker-compose.yml` 中的端口映射
2. **服務啟動失敗**: 查看日誌 `docker-compose logs [服務名]`
3. **資料庫連接失敗**: 重新啟動 `docker-compose down && docker-compose up -d`

### 清理環境

```bash
# 完全清理（包括資料）
docker-compose down -v
docker system prune -f
```

## 📚 詳細文檔

- [完整部署指南](README_DOCKER.md)
- [API 文檔](http://localhost:8001/docs)
- [系統架構文檔](files/02_system_architecture_document.md)

---

**版本**: v1.0.0  
**維護者**: AIPE01_group2  
**最後更新**: 2024-12-19 