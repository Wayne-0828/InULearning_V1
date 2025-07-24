#!/usr/bin/env python3
"""
InULearning AI Analysis Service 簡化啟動腳本

用於啟動簡化版本的 AI 分析服務應用程式
"""

import os
import sys
import uvicorn
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函數"""
    
    # 載入環境變數
    from dotenv import load_dotenv
    load_dotenv()
    
    # 獲取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8004"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    reload = debug
    
    print(f"🚀 啟動 InULearning AI Analysis Service (簡化版)")
    print(f"📍 服務地址: http://{host}:{port}")
    print(f"🔧 調試模式: {debug}")
    print(f"📊 API 文檔: http://{host}:{port}/docs")
    print(f"📋 健康檢查: http://{host}:{port}/health")
    print("-" * 50)
    
    # 啟動服務
    uvicorn.run(
        "src.main_simple:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info" if debug else "warning",
        access_log=True
    )

if __name__ == "__main__":
    main() 