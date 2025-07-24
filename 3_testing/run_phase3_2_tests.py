#!/usr/bin/env python3
"""
Phase 3.2 Test Runner - System Integration and E2E Testing
Executes comprehensive testing for Phase 3.2 completion
"""
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any

def run_command(cmd: List[str], description: str = "") -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description or ' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description or 'Command'} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description or 'Command'} failed with exit code {e.returncode}")
        return False

def check_services_health() -> bool:
    """Check if all services are healthy."""
    print("Checking services health...")
    
    import requests
    
    services = [
        "http://localhost:8001/health",  # auth-service
        "http://localhost:8002/health",  # learning-service
        "http://localhost:8003/health",  # question-bank-service
        "http://localhost:8004/health",  # ai-analysis-service
        "http://localhost:8005/health",  # parent-dashboard-service
        "http://localhost:8006/health",  # teacher-management-service
        "http://localhost:8007/health",  # notification-service
    ]
    
    all_healthy = True
    for service_url in services:
        try:
            response = requests.get(service_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_url} - Healthy")
            else:
                print(f"❌ {service_url} - Unhealthy (Status: {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"❌ {service_url} - Unreachable ({e})")
            all_healthy = False
    
    return all_healthy

def run_system_integration_tests() -> bool:
    """Run system integration tests."""
    print("Running system integration tests...")
    
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/integration_tests/",
        "-v",
        "-m", "integration",
        "--tb=short",
        "--junitxml=test-results/integration.xml"
    ]
    return run_command(cmd, "System Integration Tests")

def run_complete_e2e_tests() -> bool:
    """Run complete E2E test suite."""
    print("Running complete E2E test suite...")
    
    # Install Playwright browsers
    install_cmd = ["poetry", "run", "playwright", "install", "chromium"]
    if not run_command(install_cmd, "Install Playwright browsers"):
        return False
    
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/e2e_tests/test_complete_user_stories.py",
        "-v",
        "-m", "e2e",
        "--tb=short",
        "--junitxml=test-results/e2e.xml"
    ]
    return run_command(cmd, "Complete E2E Tests")

def run_load_stress_tests() -> bool:
    """Run load and stress tests."""
    print("Running load and stress tests...")
    
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/performance_tests/test_load_and_stress.py",
        "-v",
        "-m", "performance",
        "--tb=short",
        "--junitxml=test-results/performance.xml"
    ]
    return run_command(cmd, "Load and Stress Tests")

def run_exploratory_tests() -> bool:
    """Run manual exploratory tests."""
    print("Running manual exploratory tests...")
    
    cmd = [
        "poetry", "run", "python", 
        "3_testing/exploratory_tests/test_manual_exploration.py"
    ]
    return run_command(cmd, "Manual Exploratory Tests")

def run_phase3_2_complete_suite() -> bool:
    """Run complete Phase 3.2 test suite."""
    print("Running Phase 3.2 Complete Test Suite")
    print("="*60)
    
    # Create test results directory
    results_dir = Path("test-results")
    results_dir.mkdir(exist_ok=True)
    
    test_results = {
        "System Integration": run_system_integration_tests(),
        "Complete E2E": run_complete_e2e_tests(),
        "Load & Stress": run_load_stress_tests(),
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print("PHASE 3.2 TEST SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for test_type, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_type:20} {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall Result: {'✅ PHASE 3.2 TESTS PASSED' if all_passed else '❌ PHASE 3.2 TESTS FAILED'}")
    
    # Generate comprehensive report
    if all_passed:
        generate_comprehensive_report()
    
    return all_passed

def generate_comprehensive_report() -> bool:
    """Generate comprehensive test report."""
    print("Generating comprehensive test report...")
    
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/",
        "--html=test-results/phase3_2_report.html",
        "--self-contained-html",
        "--junitxml=test-results/phase3_2_junit.xml",
        "--cov=backend",
        "--cov-report=html:test-results/coverage",
        "--cov-report=xml:test-results/coverage.xml"
    ]
    
    success = run_command(cmd, "Generate Comprehensive Report")
    
    if success:
        print(f"\n📊 Phase 3.2 test reports generated:")
        print(f"   - HTML Report: test-results/phase3_2_report.html")
        print(f"   - Coverage Report: test-results/coverage/index.html")
        print(f"   - JUnit XML: test-results/phase3_2_junit.xml")
    
    return success

def main():
    """Main function for Phase 3.2 testing."""
    parser = argparse.ArgumentParser(description="Phase 3.2 Test Runner")
    parser.add_argument(
        "--type", 
        choices=["integration", "e2e", "load-stress", "exploratory", "complete"],
        default="complete",
        help="Type of Phase 3.2 tests to run"
    )
    parser.add_argument(
        "--check-health",
        action="store_true",
        help="Check services health before running tests"
    )
    parser.add_argument(
        "--skip-exploratory",
        action="store_true",
        help="Skip manual exploratory tests"
    )
    
    args = parser.parse_args()
    
    print("🚀 Phase 3.2 Test Runner - System Integration and E2E Testing")
    print(f"Test Type: {args.type.upper()}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check services health if requested
    if args.check_health:
        if not check_services_health():
            print("❌ Services health check failed")
            sys.exit(1)
    
    # Run tests based on type
    success = False
    
    if args.type == "integration":
        success = run_system_integration_tests()
    elif args.type == "e2e":
        success = run_complete_e2e_tests()
    elif args.type == "load-stress":
        success = run_load_stress_tests()
    elif args.type == "exploratory":
        success = run_exploratory_tests()
    elif args.type == "complete":
        success = run_phase3_2_complete_suite()
    
    if success:
        print(f"\n🎉 Phase 3.2 {args.type.upper()} tests completed successfully!")
        return 0
    else:
        print(f"\n❌ Phase 3.2 {args.type.upper()} tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 