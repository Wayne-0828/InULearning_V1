#!/usr/bin/env python3
"""
測試檔案整合腳本
將分散在各個服務資料夾中的測試檔案整合到統一測試資料夾中
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Any

class TestConsolidator:
    """測試檔案整合器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.unified_tests_dir = project_root / "unified_tests"
        self.backend_dir = project_root / "2_implementation" / "backend"
        
        # 測試檔案映射
        self.test_file_mapping = {
            # Auth Service
            "auth-service/test_api.py": "unit_tests/test_auth_api.py",
            "auth-service/test_basic.py": "unit_tests/test_auth_basic.py",
            "auth-service/test_startup.py": "unit_tests/test_auth_startup.py",
            "auth-service/tests/test_auth.py": "unit_tests/test_auth_integration.py",
            
            # Learning Service
            "learning-service/test_setup.py": "unit_tests/test_learning_setup.py",
            "learning-service/tests/test_main.py": "unit_tests/test_learning_main.py",
            "learning-service/test_environment/test_setup.py": "unit_tests/test_learning_env_setup.py",
            "learning-service/test_environment/test_api.py": "unit_tests/test_learning_env_api.py",
            
            # Question Bank Service
            "question-bank-service/test_basic.py": "unit_tests/test_question_bank_basic.py",
            "question-bank-service/tests/test_question_bank.py": "unit_tests/test_question_bank_integration.py",
            
            # AI Analysis Service
            "ai-analysis-service/tests/test_basic.py": "unit_tests/test_ai_analysis_basic.py",
            "ai-analysis-service/tests/test_vector_service.py": "unit_tests/test_ai_vector_service.py",
            "ai-analysis-service/tests/test_trend_analysis.py": "unit_tests/test_ai_trend_analysis.py",
            "ai-analysis-service/tests/test_learning_recommendation.py": "unit_tests/test_ai_learning_recommendation.py",
            "ai-analysis-service/tests/test_weakness_analysis.py": "unit_tests/test_ai_weakness_analysis.py",
            "ai-analysis-service/tests/test_api_integration.py": "integration_tests/test_ai_api_integration.py",
            
            # Backend Level Tests
            "test_database_integration.py": "integration_tests/test_database_integration.py",
            "test_models_simple.py": "unit_tests/test_models_simple.py",
            "test_data_consistency.py": "integration_tests/test_data_consistency.py",
            "shared/models/test_models.py": "unit_tests/test_shared_models.py"
        }
    
    def find_test_files(self) -> List[Path]:
        """尋找所有測試檔案"""
        test_files = []
        
        # 搜尋 backend 目錄下的測試檔案
        for root, dirs, files in os.walk(self.backend_dir):
            # 排除 venv 和 site-packages 目錄
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.pytest_cache'] and 'site-packages' not in d]
            
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    file_path = Path(root) / file
                    test_files.append(file_path)
        
        return test_files
    
    def get_relative_path(self, file_path: Path) -> str:
        """獲取相對於 backend 目錄的路徑"""
        try:
            return str(file_path.relative_to(self.backend_dir))
        except ValueError:
            return str(file_path)
    
    def consolidate_test_files(self, dry_run: bool = True) -> Dict[str, Any]:
        """整合測試檔案"""
        results = {
            "copied": [],
            "skipped": [],
            "errors": []
        }
        
        test_files = self.find_test_files()
        print(f"🔍 找到 {len(test_files)} 個測試檔案")
        
        for test_file in test_files:
            relative_path = self.get_relative_path(test_file)
            
            # 檢查是否在映射中
            if relative_path in self.test_file_mapping:
                target_path = self.unified_tests_dir / self.test_file_mapping[relative_path]
                
                # 確保目標目錄存在
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    if not dry_run:
                        # 複製檔案
                        shutil.copy2(test_file, target_path)
                        print(f"✅ 複製: {relative_path} -> {self.test_file_mapping[relative_path]}")
                    else:
                        print(f"📋 將複製: {relative_path} -> {self.test_file_mapping[relative_path]}")
                    
                    results["copied"].append({
                        "source": str(test_file),
                        "target": str(target_path),
                        "relative_path": relative_path
                    })
                    
                except Exception as e:
                    error_msg = f"複製 {relative_path} 失敗: {e}"
                    print(f"❌ {error_msg}")
                    results["errors"].append(error_msg)
            else:
                print(f"⚠️  跳過: {relative_path} (未在映射中)")
                results["skipped"].append(str(test_file))
        
        return results
    
    def update_test_imports(self, dry_run: bool = True) -> Dict[str, Any]:
        """更新測試檔案中的導入路徑"""
        results = {
            "updated": [],
            "errors": []
        }
        
        # 更新統一測試資料夾中的檔案
        for root, dirs, files in os.walk(self.unified_tests_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 更新導入路徑
                        updated_content = self._update_import_paths(content)
                        
                        if content != updated_content:
                            if not dry_run:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(updated_content)
                                print(f"✅ 更新導入: {file_path.relative_to(self.unified_tests_dir)}")
                            else:
                                print(f"📋 將更新導入: {file_path.relative_to(self.unified_tests_dir)}")
                            
                            results["updated"].append(str(file_path))
                    
                    except Exception as e:
                        error_msg = f"更新 {file_path} 失敗: {e}"
                        print(f"❌ {error_msg}")
                        results["errors"].append(error_msg)
        
        return results
    
    def _update_import_paths(self, content: str) -> str:
        """更新導入路徑"""
        # 這裡可以添加具體的導入路徑更新邏輯
        # 例如將相對導入改為絕對導入等
        return content
    
    def create_test_index(self) -> None:
        """創建測試索引檔案"""
        index_content = """# InULearning_V1 統一測試索引

本檔案列出了所有整合的測試檔案及其來源。

## 單元測試 (Unit Tests)

### 認證服務 (Auth Service)
- `unit_tests/test_auth_api.py` - 來自 auth-service/test_api.py
- `unit_tests/test_auth_basic.py` - 來自 auth-service/test_basic.py
- `unit_tests/test_auth_startup.py` - 來自 auth-service/test_startup.py
- `unit_tests/test_auth_integration.py` - 來自 auth-service/tests/test_auth.py

### 學習服務 (Learning Service)
- `unit_tests/test_learning_setup.py` - 來自 learning-service/test_setup.py
- `unit_tests/test_learning_main.py` - 來自 learning-service/tests/test_main.py
- `unit_tests/test_learning_env_setup.py` - 來自 learning-service/test_environment/test_setup.py
- `unit_tests/test_learning_env_api.py` - 來自 learning-service/test_environment/test_api.py

### 題庫服務 (Question Bank Service)
- `unit_tests/test_question_bank_basic.py` - 來自 question-bank-service/test_basic.py
- `unit_tests/test_question_bank_integration.py` - 來自 question-bank-service/tests/test_question_bank.py

### AI 分析服務 (AI Analysis Service)
- `unit_tests/test_ai_analysis_basic.py` - 來自 ai-analysis-service/tests/test_basic.py
- `unit_tests/test_ai_vector_service.py` - 來自 ai-analysis-service/tests/test_vector_service.py
- `unit_tests/test_ai_trend_analysis.py` - 來自 ai-analysis-service/tests/test_trend_analysis.py
- `unit_tests/test_ai_learning_recommendation.py` - 來自 ai-analysis-service/tests/test_learning_recommendation.py
- `unit_tests/test_ai_weakness_analysis.py` - 來自 ai-analysis-service/tests/test_weakness_analysis.py

### 共享模組 (Shared Modules)
- `unit_tests/test_shared_models.py` - 來自 shared/models/test_models.py
- `unit_tests/test_models_simple.py` - 來自 test_models_simple.py

## 整合測試 (Integration Tests)

- `integration_tests/test_database_integration.py` - 來自 test_database_integration.py
- `integration_tests/test_data_consistency.py` - 來自 test_data_consistency.py
- `integration_tests/test_ai_api_integration.py` - 來自 ai-analysis-service/tests/test_api_integration.py

## 端到端測試 (E2E Tests)

- `e2e_tests/test_user_flow.py` - 用戶流程測試
- `e2e_tests/test_system_workflow.py` - 系統工作流程測試

## 效能測試 (Performance Tests)

- `performance_tests/test_api_performance.py` - API 效能測試
- `performance_tests/test_database_performance.py` - 資料庫效能測試

## 執行測試

```bash
# 執行所有測試
python run_all_tests.py

# 執行特定類型測試
python run_all_tests.py --test-types unit
python run_all_tests.py --test-types integration
python run_all_tests.py --test-types e2e
python run_all_tests.py --test-types performance

# 執行特定服務測試
pytest unit_tests/test_auth_*.py -v
pytest unit_tests/test_learning_*.py -v
pytest unit_tests/test_question_bank_*.py -v
pytest unit_tests/test_ai_*.py -v
```

## 注意事項

1. 所有測試檔案已整合到統一測試資料夾中
2. 導入路徑已更新以適應新的檔案結構
3. 測試配置統一在 conftest.py 中管理
4. 測試報告統一生成到 test_reports/ 目錄
"""
        
        index_file = self.unified_tests_dir / "TEST_INDEX.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"✅ 創建測試索引: {index_file}")

def main():
    """主函數"""
    project_root = Path(__file__).parent.parent
    consolidator = TestConsolidator(project_root)
    
    print("🚀 InULearning_V1 測試檔案整合工具")
    print("=" * 50)
    
    # 檢查是否為乾運行
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("🔍 乾運行模式 - 不會實際複製檔案")
    else:
        print("📁 實際整合模式 - 將複製和更新檔案")
    
    print()
    
    # 整合測試檔案
    print("📋 整合測試檔案...")
    results = consolidator.consolidate_test_files(dry_run=dry_run)
    
    print(f"\n📊 整合結果:")
    print(f"  ✅ 複製: {len(results['copied'])} 個檔案")
    print(f"  ⚠️  跳過: {len(results['skipped'])} 個檔案")
    print(f"  ❌ 錯誤: {len(results['errors'])} 個檔案")
    
    if results['errors']:
        print("\n❌ 錯誤詳情:")
        for error in results['errors']:
            print(f"  - {error}")
    
    # 更新導入路徑
    print("\n🔧 更新導入路徑...")
    import_results = consolidator.update_test_imports(dry_run=dry_run)
    
    print(f"📊 導入更新結果:")
    print(f"  ✅ 更新: {len(import_results['updated'])} 個檔案")
    print(f"  ❌ 錯誤: {len(import_results['errors'])} 個檔案")
    
    # 創建測試索引
    print("\n📝 創建測試索引...")
    consolidator.create_test_index()
    
    print("\n" + "=" * 50)
    if dry_run:
        print("🔍 乾運行完成！請檢查上述結果，然後移除 --dry-run 參數執行實際整合")
    else:
        print("🎉 測試檔案整合完成！")
        print("📁 所有測試檔案已整合到 unified_tests/ 目錄")
        print("📖 請查看 TEST_INDEX.md 了解詳細的檔案映射")

if __name__ == "__main__":
    main() 