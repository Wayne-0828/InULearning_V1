#!/usr/bin/env python3
"""
測試 AI 分析服務的導入問題
"""

import os
import sys
from pathlib import Path

def test_imports():
    """測試所有必要的導入"""
    print("🔍 測試 AI 分析服務導入...")
    
    # 添加專案根目錄到 Python 路徑
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    print(f"📁 專案根目錄: {project_root}")
    
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
    
    # 測試 AI 相關導入
    try:
        print("\n✅ 測試 AI 相關導入...")
        import google.generativeai as genai
        print("  ✓ google-generativeai")
        
        import openai
        print("  ✓ openai")
        
        from pymilvus import connections, Collection
        print("  ✓ pymilvus")
        
        from sentence_transformers import SentenceTransformer
        print("  ✓ sentence-transformers")
        
    except ImportError as e:
        print(f"  ⚠️ AI 相關導入失敗 (部分功能可能受限): {e}")
    
    # 測試本地模組導入
    try:
        print("\n✅ 測試本地模組導入...")
        from src.utils.config import get_settings
        print("  ✓ config utils")
        
        from src.utils.database import init_db, check_redis_connection, check_postgresql_connection
        print("  ✓ database utils")
        
    except ImportError as e:
        print(f"  ❌ 本地模組導入失敗: {e}")
        return False
    
    # 測試路由導入
    try:
        print("\n✅ 測試路由導入...")
        from src.routers import (
            weakness_analysis_router,
            learning_recommendation_router,
            trend_analysis_router,
            vector_search_router
        )
        print("  ✓ all routers")
        
    except ImportError as e:
        print(f"  ❌ 路由導入失敗: {e}")
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
    print("🚀 AI 分析服務導入測試")
    print("=" * 50)
    
    if test_imports():
        if test_main_app():
            print("\n✅ 所有測試通過！AI 分析服務可以正常啟動。")
        else:
            print("\n❌ 主應用程式測試失敗。")
    else:
        print("\n❌ 導入測試失敗。") 