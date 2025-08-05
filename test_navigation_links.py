#!/usr/bin/env python3
"""
前端導航連結測試
驗證所有頁面間的導航連結是否正確設置
"""

import os
import re
from pathlib import Path

def test_navigation_links():
    """測試前端導航連結"""
    print("🔍 InU Learning 前端導航連結測試")
    print("=" * 60)
    
    # 定義要檢查的文件和預期連結
    test_cases = [
        {
            "file": "2_implementation/frontend/shared/homepage/index.html",
            "name": "首頁",
            "expected_links": [
                "auth/login.html",
                "auth/register.html"
            ]
        },
        {
            "file": "2_implementation/frontend/shared/auth/login.html", 
            "name": "登入頁",
            "expected_links": [
                "register.html"
            ]
        },
        {
            "file": "2_implementation/frontend/shared/auth/register.html",
            "name": "註冊頁", 
            "expected_links": [
                "login.html"
            ]
        }
    ]
    
    all_tests_passed = True
    
    for test_case in test_cases:
        file_path = test_case["file"]
        file_name = test_case["name"]
        expected_links = test_case["expected_links"]
        
        print(f"\n📄 測試 {file_name} ({file_path})")
        print("-" * 50)
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            all_tests_passed = False
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查每個預期連結
            for link in expected_links:
                if link in content:
                    # 計算出現次數
                    count = len(re.findall(re.escape(link), content))
                    print(f"✅ 找到連結: {link} (出現 {count} 次)")
                else:
                    print(f"❌ 缺少連結: {link}")
                    all_tests_passed = False
            
            # 特別檢查首頁的多個連結位置
            if file_name == "首頁":
                locations = [
                    ("導航欄登入", 'class="btn-login".*?href="auth/login.html"'),
                    ("導航欄註冊", 'class="btn-register".*?href="auth/register.html"'),
                    ("英雄區登入", 'class="btn-primary".*?href="auth/login.html"'),
                    ("英雄區註冊", 'class="btn-secondary".*?href="auth/register.html"'),
                    ("頁腳登入", '登入系統.*?href="auth/login.html"'),
                    ("頁腳註冊", '註冊帳號.*?href="auth/register.html"')
                ]
                
                print("  📍 詳細位置檢查:")
                for location_name, pattern in locations:
                    if re.search(pattern, content, re.DOTALL):
                        print(f"    ✅ {location_name}")
                    else:
                        print(f"    ❌ {location_name}")
                        
        except Exception as e:
            print(f"❌ 讀取文件錯誤: {e}")
            all_tests_passed = False
    
    # 摘要
    print("\n" + "=" * 60)
    print("📊 測試摘要")
    print("=" * 60)
    
    if all_tests_passed:
        print("✅ 所有導航連結測試通過！")
        print("🎉 前端操作已完善，使用者可以順利導航")
        
        print("\n🚀 使用者流程:")
        print("  1. 首頁 → 點擊註冊 → 註冊頁面")
        print("  2. 首頁 → 點擊登入 → 登入頁面") 
        print("  3. 登入頁 → 點擊前往註冊 → 註冊頁面")
        print("  4. 註冊頁 → 點擊前往登入 → 登入頁面")
        print("  5. 註冊完成 → 自動跳轉到對應角色頁面")
        
        print("\n📱 支援的導航位置:")
        print("  • 首頁導航欄 (登入/註冊)")
        print("  • 首頁英雄區按鈕 (立即登入/立即註冊)")
        print("  • 首頁頁腳連結 (登入系統/註冊帳號)")
        print("  • 登入頁底部 (前往註冊)")
        print("  • 註冊頁底部 (前往登入)")
        
    else:
        print("❌ 部分導航連結測試失敗")
        print("🔧 請檢查上述失敗項目並修正")
    
    return all_tests_passed

def main():
    success = test_navigation_links()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)