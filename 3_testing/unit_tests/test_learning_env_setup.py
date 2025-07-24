#!/usr/bin/env python3
"""
測試環境設置檢查腳本
檢查所有必要的組件是否正確安裝和配置
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """檢查 Python 版本"""
    print("🐍 檢查 Python 版本...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python 版本符合要求 (>= 3.8)")
        return True
    else:
        print("   ❌ Python 版本不符合要求 (需要 >= 3.8)")
        return False

def check_virtual_environment():
    """檢查虛擬環境"""
    print("\n🔧 檢查虛擬環境...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ 正在使用虛擬環境")
        print(f"   虛擬環境路徑: {sys.prefix}")
        return True
    else:
        print("   ⚠️  未檢測到虛擬環境")
        return False

def check_required_packages():
    """檢查必要的套件"""
    print("\n📦 檢查必要套件...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlalchemy',
        'asyncpg',
        'httpx',
        'jose',
        'multipart',
        'structlog',
        'dotenv'
    ]
    
    missing_packages = []
    installed_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            installed_packages.append(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} (未安裝)")
    
    if missing_packages:
        print(f"\n   ⚠️  缺少套件: {', '.join(missing_packages)}")
        return False
    else:
        print(f"\n   ✅ 所有必要套件已安裝 ({len(installed_packages)} 個)")
        return True

def check_project_structure():
    """檢查專案結構"""
    print("\n📁 檢查專案結構...")
    
    current_dir = Path.cwd()
    required_files = [
        'src/main.py',
        'src/models/',
        'src/services/',
        'src/routers/',
        'src/utils/',
        'requirements.txt',
        'env.example',
        'run.py'
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            existing_files.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} (不存在)")
    
    if missing_files:
        print(f"\n   ⚠️  缺少檔案: {', '.join(missing_files)}")
        return False
    else:
        print(f"\n   ✅ 專案結構完整 ({len(existing_files)} 個檔案/目錄)")
        return True

def check_environment_file():
    """檢查環境變數檔案"""
    print("\n🔐 檢查環境變數檔案...")
    
    env_files = ['.env', '.env.test', 'env.example']
    found_env = False
    
    for env_file in env_files:
        if Path(env_file).exists():
            print(f"   ✅ 找到環境檔案: {env_file}")
            found_env = True
        else:
            print(f"   ⚠️  未找到: {env_file}")
    
    if not found_env:
        print("   ❌ 未找到任何環境變數檔案")
        return False
    
    return True

def main():
    """主檢查函數"""
    print("🔍 InULearning Learning Service 測試環境檢查")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_virtual_environment(),
        check_required_packages(),
        check_project_structure(),
        check_environment_file()
    ]
    
    print("\n" + "=" * 50)
    print("📊 檢查結果摘要:")
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ 所有檢查通過 ({passed}/{total})")
        print("🎉 測試環境設置完成！")
        return True
    else:
        print(f"⚠️  部分檢查失敗 ({passed}/{total})")
        print("🔧 請檢查上述問題並重新設置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 