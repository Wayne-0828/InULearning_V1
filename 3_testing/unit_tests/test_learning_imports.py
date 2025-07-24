#!/usr/bin/env python3
"""
測試學習服務的導入問題
"""

import os
import sys
from pathlib import Path

def test_imports():
    """測試所有必要的導入"""
    print("🔍 測試學習服務導入...")
    
    # 添加專案根目錄到 Python 路徑
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # 添加 shared 目錄到 Python 路徑
    shared_path = os.path.join(project_root, '..', 'shared')
    if shared_path not in sys.path:
        sys.path.insert(0, shared_path)
    
    print(f"📁 專案根目錄: {project_root}")
    print(f"📁 Shared 目錄: {shared_path}")
    print(f"📁 Shared 目錄存在: {os.path.exists(shared_path)}")
    
    # 測試基本導入
    try:
        print("\n✅ 測試基本導入...")
        import uvicorn
        print("  ✓ uvicorn")
        
        from fastapi import FastAPI
        print("  ✓ fastapi")
        
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
        
    except ImportError as e:
        print(f"  ❌ 基本導入失敗: {e}")
        return False
    
    # 測試資料庫導入
    try:
        print("\n✅ 測試資料庫導入...")
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
        print("  ✓ sqlalchemy")
        
        import asyncpg
        print("  ✓ asyncpg")
        
        from motor.motor_asyncio import AsyncIOMotorClient
        print("  ✓ motor")
        
        import redis.asyncio as redis
        print("  ✓ redis")
        
    except ImportError as e:
        print(f"  ❌ 資料庫導入失敗: {e}")
        return False
    
    # 測試 shared 導入
    try:
        print("\n✅ 測試 shared 導入...")
        from database.postgresql import get_postgresql_engine
        print("  ✓ shared postgresql")
        
        from database.mongodb import get_mongodb_client
        print("  ✓ shared mongodb")
        
        from database.redis import get_redis_client
        print("  ✓ shared redis")
        
    except ImportError as e:
        print(f"  ⚠️ Shared 導入失敗 (將使用本地配置): {e}")
    
    # 測試本地模型導入
    try:
        print("\n✅ 測試本地模型導入...")
        from src.models.base import Base
        print("  ✓ local base model")
        
        from src.models import schemas
        print("  ✓ local schemas")
        
    except ImportError as e:
        print(f"  ❌ 本地模型導入失敗: {e}")
        return False
    
    # 測試路由導入
    try:
        print("\n✅ 測試路由導入...")
        from src.routers import exercises, sessions, recommendations, trends
        print("  ✓ all routers")
        
    except ImportError as e:
        print(f"  ❌ 路由導入失敗: {e}")
        return False
    
    # 測試工具導入
    try:
        print("\n✅ 測試工具導入...")
        from src.utils.logging_config import setup_logging
        print("  ✓ logging config")
        
        from src.utils.auth import get_current_user
        print("  ✓ auth utils")
        
        from src.utils.exceptions import LearningException
        print("  ✓ exceptions")
        
    except ImportError as e:
        print(f"  ❌ 工具導入失敗: {e}")
        return False
    
    print("\n🎉 所有導入測試通過！")
    return True

def test_main_app():
    """測試主應用程式"""
    try:
        print("\n🔍 測試主應用程式...")
        from src.main import app
        print("  ✓ 主應用程式創建成功")
        print(f"  ✓ 應用程式標題: {app.title}")
        print(f"  ✓ 應用程式版本: {app.version}")
        return True
    except Exception as e:
        print(f"  ❌ 主應用程式測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 學習服務導入測試")
    print("=" * 50)
    
    if test_imports():
        if test_main_app():
            print("\n✅ 所有測試通過！學習服務可以正常啟動。")
        else:
            print("\n❌ 主應用程式測試失敗。")
    else:
        print("\n❌ 導入測試失敗。") 