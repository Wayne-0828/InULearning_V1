#!/usr/bin/env python3
"""
Test Runner Script for InULearning Platform
Executes different types of tests based on command line arguments
"""
import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any

# Add the testing directory to Python path
testing_dir = Path(__file__).parent
sys.path.insert(0, str(testing_dir))

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

def install_test_dependencies() -> bool:
    """Install test dependencies using Poetry."""
    print("Installing test dependencies...")
    
    # Install test requirements
    cmd = ["poetry", "run", "pip", "install", "-r", "3_testing/requirements.txt"]
    return run_command(cmd, "Install test dependencies")

def run_unit_tests() -> bool:
    """Run unit tests."""
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/unit_tests/",
        "-v",
        "--tb=short",
        "--cov=backend",
        "--cov-report=html:test-results/coverage",
        "--cov-report=term-missing"
    ]
    return run_command(cmd, "Unit Tests")

def run_integration_tests() -> bool:
    """Run integration tests."""
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/integration_tests/",
        "-v",
        "-m", "integration",
        "--tb=short"
    ]
    return run_command(cmd, "Integration Tests")

def run_performance_tests() -> bool:
    """Run performance tests."""
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/performance_tests/",
        "-v",
        "-m", "performance",
        "--tb=short"
    ]
    return run_command(cmd, "Performance Tests")

def run_ai_tests() -> bool:
    """Run AI model tests."""
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/ai_model_tests/",
        "-v",
        "-m", "ai",
        "--tb=short"
    ]
    return run_command(cmd, "AI Model Tests")

def run_e2e_tests() -> bool:
    """Run end-to-end tests."""
    # First install Playwright browsers
    print("Installing Playwright browsers...")
    install_cmd = ["poetry", "run", "playwright", "install", "chromium"]
    if not run_command(install_cmd, "Install Playwright browsers"):
        return False
    
    # Run E2E tests
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/e2e_tests/",
        "-v",
        "-m", "e2e",
        "--tb=short",
        "--headed"  # Run with browser visible
    ]
    return run_command(cmd, "End-to-End Tests")

def run_complete_e2e_tests() -> bool:
    """Run complete E2E test suite with all user stories."""
    print("Running complete E2E test suite...")
    
    # Run comprehensive E2E tests
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/e2e_tests/test_complete_user_stories.py",
        "-v",
        "-m", "e2e",
        "--tb=short",
        "--headed"
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
        "--tb=short"
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

def run_smoke_tests() -> bool:
    """Run smoke tests (quick health checks)."""
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/",
        "-v",
        "-m", "smoke",
        "--tb=short",
        "--maxfail=1"
    ]
    return run_command(cmd, "Smoke Tests")

def run_all_tests() -> bool:
    """Run all tests."""
    print("Running all tests...")
    
    test_results = {
        "unit": run_unit_tests(),
        "integration": run_integration_tests(),
        "performance": run_performance_tests(),
        "ai": run_ai_tests(),
        "e2e": run_e2e_tests(),
        "complete-e2e": run_complete_e2e_tests(),
        "load-stress": run_load_stress_tests()
    }
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for test_type, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_type.upper():15} {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed

def generate_test_report() -> bool:
    """Generate comprehensive test report."""
    print("Generating test report...")
    
    # Create test results directory
    results_dir = Path("test-results")
    results_dir.mkdir(exist_ok=True)
    
    # Run tests with HTML report
    cmd = [
        "poetry", "run", "pytest", 
        "3_testing/",
        "--html=test-results/report.html",
        "--self-contained-html",
        "--junitxml=test-results/junit.xml",
        "--cov=backend",
        "--cov-report=html:test-results/coverage",
        "--cov-report=xml:test-results/coverage.xml"
    ]
    
    success = run_command(cmd, "Generate Test Report")
    
    if success:
        print(f"\n📊 Test reports generated in {results_dir.absolute()}")
        print(f"   - HTML Report: {results_dir / 'report.html'}")
        print(f"   - Coverage Report: {results_dir / 'coverage' / 'index.html'}")
        print(f"   - JUnit XML: {results_dir / 'junit.xml'}")
    
    return success

def check_services_health() -> bool:
    """Check if all services are healthy before running tests."""
    print("Checking services health...")
    
    import requests
    import time
    
    services = [
        "http://localhost:8001/health",  # auth-service
        "http://localhost:8002/health",  # learning-service
        "http://localhost:8003/health",  # question-bank-service
        "http://localhost:8004/health",  # ai-analysis-service
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
    
    if not all_healthy:
        print("\n⚠️  Some services are not healthy. Tests may fail.")
        response = input("Continue anyway? (y/N): ")
        return response.lower() == 'y'
    
    return True

def main():
    """Main function to run tests based on command line arguments."""
    parser = argparse.ArgumentParser(description="InULearning Platform Test Runner")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "performance", "ai", "e2e", "complete-e2e", "load-stress", "exploratory", "smoke", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running tests"
    )
    parser.add_argument(
        "--check-health",
        action="store_true",
        help="Check services health before running tests"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive test report"
    )
    parser.add_argument(
        "--skip-e2e",
        action="store_true",
        help="Skip E2E tests when running all tests"
    )
    
    args = parser.parse_args()
    
    print("🚀 InULearning Platform Test Runner")
    print(f"Test Type: {args.type.upper()}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    # Check services health if requested
    if args.check_health:
        if not check_services_health():
            print("❌ Services health check failed")
            sys.exit(1)
    
    # Run tests based on type
    success = False
    
    if args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "performance":
        success = run_performance_tests()
    elif args.type == "ai":
        success = run_ai_tests()
    elif args.type == "e2e":
        success = run_e2e_tests()
    elif args.type == "complete-e2e":
        success = run_complete_e2e_tests()
    elif args.type == "load-stress":
        success = run_load_stress_tests()
    elif args.type == "exploratory":
        success = run_exploratory_tests()
    elif args.type == "smoke":
        success = run_smoke_tests()
    elif args.type == "all":
        if args.skip_e2e:
            print("Skipping E2E tests as requested...")
            # Run all tests except E2E
            success = (
                run_unit_tests() and
                run_integration_tests() and
                run_performance_tests() and
                run_ai_tests()
            )
        else:
            success = run_all_tests()
    
    # Generate report if requested
    if args.report and success:
        generate_test_report()
    
    # Exit with appropriate code
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 