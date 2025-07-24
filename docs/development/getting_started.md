# InULearning 開發入門指南

## 🚀 快速開始

### 前置需求

在開始開發之前，請確保您的系統已安裝以下軟體：

- **Docker & Docker Compose**: 用於容器化部署
- **Python 3.11+**: 後端開發
- **Git**: 版本控制
- **VS Code** (推薦): 程式碼編輯器

### 環境設置

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd InULearning_V1
   ```

2. **執行自動設置腳本**
   ```bash
   ./2_implementation/scripts/setup/dev-setup.sh
   ```

3. **手動設置（如果自動腳本失敗）**
   ```bash
   # 複製環境變數
   cp env.example .env
   
   # 編輯環境變數
   nano .env
   
   # 啟動基礎服務
   docker-compose -f 4_deployment/docker/docker-compose.dev.yml up -d
   ```

## 🏗️ 專案結構說明

### 核心目錄

```
InULearning_V1/
├── 2_implementation/          # 核心實作
│   ├── backend/              # 後端微服務
│   │   ├── auth-service/     # 認證服務
│   │   ├── learning-service/ # 學習服務
│   │   ├── question-bank-service/ # 題庫服務
│   │   ├── ai-analysis-service/   # AI 分析服務
│   │   └── shared/           # 共用組件
│   ├── frontend/             # 前端應用
│   └── database/             # 資料庫相關
├── 3_testing/                # 測試檔案
├── 4_deployment/             # 部署配置
├── config/                   # 配置檔案
└── docs/                     # 技術文檔
```

### 開發階段對應

| 階段 | 目錄 | 狀態 | 說明 |
|------|------|------|------|
| Phase 1 | `1_system_design/` | ✅ 完成 | 系統設計與架構 |
| Phase 2 | `2_implementation/` | 🔄 進行中 | 核心功能開發 |
| Phase 3 | `3_testing/` | ⏳ 待開始 | 測試驗證 |
| Phase 4 | `4_deployment/` | ⏳ 待開始 | 部署上線 |

## 🔧 開發工作流程

### 1. 功能開發流程

```bash
# 1. 建立功能分支
git checkout -b feature/your-feature-name

# 2. 開發功能
# ... 編寫程式碼 ...

# 3. 執行測試
pytest 3_testing/unit_tests/
pytest 3_testing/integration_tests/

# 4. 程式碼品質檢查
black 2_implementation/backend/
flake8 2_implementation/backend/
mypy 2_implementation/backend/

# 5. 提交變更
git add .
git commit -m "feat: add your feature description"

# 6. 推送到遠端
git push origin feature/your-feature-name
```

### 2. 微服務開發

每個微服務都遵循相同的結構：

```
service-name/
├── src/
│   ├── main.py              # 服務入口點
│   ├── routers/             # API 路由
│   ├── models/              # 資料模型
│   ├── services/            # 業務邏輯
│   └── utils/               # 工具函數
├── tests/                   # 測試檔案
├── requirements.txt         # Python 依賴
└── Dockerfile              # 容器配置
```

### 3. API 開發規範

- **路由命名**: 使用 RESTful 命名規範
- **回應格式**: 統一的 JSON 回應格式
- **錯誤處理**: 標準化的錯誤回應
- **文檔**: 使用 FastAPI 自動生成 API 文檔

範例：
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["example"])

class ExampleRequest(BaseModel):
    name: str
    description: str

@router.post("/example")
async def create_example(request: ExampleRequest):
    try:
        # 業務邏輯
        result = {"id": 1, "name": request.name}
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 🧪 測試策略

### 測試類型

1. **單元測試**: 測試個別函數和類別
2. **整合測試**: 測試服務間整合
3. **E2E 測試**: 測試完整用戶流程
4. **效能測試**: 測試系統效能

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest 3_testing/unit_tests/test_auth.py

# 執行測試並生成覆蓋率報告
pytest --cov=2_implementation/backend --cov-report=html

# 執行效能測試
pytest 3_testing/performance_tests/
```

### 測試覆蓋率目標

- **單元測試**: ≥ 80%
- **整合測試**: ≥ 70%
- **E2E 測試**: 關鍵流程 100%

## 📊 監控與除錯

### 日誌查看

```bash
# 查看所有服務日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs -f auth-service

# 查看應用程式日誌
tail -f logs/app.log
```

### 監控指標

- **系統指標**: CPU、記憶體、磁碟使用率
- **應用指標**: API 響應時間、錯誤率
- **業務指標**: 用戶活躍度、學習成效

### 除錯技巧

1. **使用 VS Code 除錯器**
2. **查看 FastAPI 自動生成的文檔**
3. **使用 Docker 日誌進行問題排查**
4. **檢查資料庫連接和查詢**

## 🔒 安全開發

### 安全最佳實踐

1. **環境變數**: 敏感資訊使用環境變數
2. **輸入驗證**: 所有用戶輸入都要驗證
3. **SQL 注入防護**: 使用參數化查詢
4. **XSS 防護**: 輸出內容進行轉義
5. **CORS 設定**: 正確配置跨域請求

### 安全檢查清單

- [ ] 所有 API 端點都有適當的認證
- [ ] 敏感資料已加密儲存
- [ ] 日誌中不包含敏感資訊
- [ ] 錯誤訊息不洩露系統資訊
- [ ] 定期更新依賴套件

## 📚 學習資源

### 技術文檔

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://pydantic-docs.helpmanual.io/
- **Docker**: https://docs.docker.com/

### 專案文檔

- **系統架構**: `files/02_system_architecture_document.md`
- **API 設計**: `files/04_api_design.md`
- **專案結構**: `files/07_project_structure.md`

### 開發工具

- **VS Code 擴充功能**: Python, Docker, Git
- **Postman**: API 測試工具
- **pgAdmin**: PostgreSQL 管理工具
- **MongoDB Compass**: MongoDB 管理工具

## 🤝 團隊協作

### 程式碼審查

1. **建立 Pull Request**
2. **指派審查者**
3. **通過所有測試**
4. **符合程式碼規範**
5. **獲得審查批准**

### 溝通管道

- **技術討論**: GitHub Discussions
- **問題回報**: GitHub Issues
- **即時溝通**: Slack/Discord
- **文件協作**: Google Docs

### 開發會議

- **每日站會**: 同步開發進度
- **週會**: 回顧與規劃
- **技術分享**: 知識交流

## 🚨 常見問題

### Q: 如何解決 Docker 權限問題？

A: 將用戶加入 docker 群組：
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Q: 如何重置開發環境？

A: 執行重置腳本：
```bash
./2_implementation/scripts/setup/reset-dev.sh
```

### Q: 如何查看 API 文檔？

A: 啟動服務後訪問：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Q: 如何新增新的微服務？

A: 參考現有服務結構，並更新相關配置檔案。

## 📞 支援

如果您在開發過程中遇到問題：

1. **查看文檔**: 先查看相關技術文檔
2. **搜尋 Issues**: 查看是否有類似問題
3. **建立 Issue**: 詳細描述問題和重現步驟
4. **尋求幫助**: 在團隊群組中尋求協助

---

**祝您開發愉快！** 🚀 