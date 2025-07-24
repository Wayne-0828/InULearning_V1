"""
Manual Exploratory Testing Script
For discovering edge cases and UI/UX issues
"""
import time
import json
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class TestCase:
    """Test case data structure."""
    name: str
    description: str
    steps: List[str]
    expected_result: str
    actual_result: str = ""
    status: str = "pending"
    notes: str = ""

class ExploratoryTestSuite:
    """Manual exploratory testing suite."""
    
    def __init__(self):
        self.test_cases = []
        self.results = []
    
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the suite."""
        self.test_cases.append(test_case)
    
    def run_test_case(self, test_case: TestCase) -> Dict[str, Any]:
        """Run a single test case and return results."""
        print(f"\n{'='*60}")
        print(f"Running: {test_case.name}")
        print(f"Description: {test_case.description}")
        print(f"{'='*60}")
        
        print("\nSteps:")
        for i, step in enumerate(test_case.steps, 1):
            print(f"{i}. {step}")
        
        print(f"\nExpected Result: {test_case.expected_result}")
        
        # Manual input for actual result
        actual_result = input("\nEnter actual result: ")
        status = input("Status (pass/fail/skip): ").lower()
        notes = input("Additional notes: ")
        
        test_case.actual_result = actual_result
        test_case.status = status
        test_case.notes = notes
        
        return {
            "name": test_case.name,
            "status": status,
            "actual_result": actual_result,
            "notes": notes
        }
    
    def run_all_tests(self):
        """Run all test cases."""
        print("Starting Manual Exploratory Testing")
        print("="*60)
        
        for test_case in self.test_cases:
            result = self.run_test_case(test_case)
            self.results.append(result)
            
            continue_testing = input("\nContinue to next test? (y/n): ").lower()
            if continue_testing != 'y':
                break
        
        self.generate_report()
    
    def generate_report(self):
        """Generate test report."""
        print("\n" + "="*60)
        print("EXPLORATORY TESTING REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["status"] == "pass")
        failed_tests = sum(1 for r in self.results if r["status"] == "fail")
        skipped_tests = sum(1 for r in self.results if r["status"] == "skip")
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
        
        print("\nDetailed Results:")
        for result in self.results:
            status_icon = "✅" if result["status"] == "pass" else "❌" if result["status"] == "fail" else "⏭️"
            print(f"{status_icon} {result['name']}: {result['status']}")
            if result["notes"]:
                print(f"   Notes: {result['notes']}")

def create_exploratory_test_suite() -> ExploratoryTestSuite:
    """Create comprehensive exploratory test suite."""
    suite = ExploratoryTestSuite()
    
    # UI/UX Edge Cases
    suite.add_test_case(TestCase(
        name="Long Username Input",
        description="Test system behavior with very long usernames",
        steps=[
            "Navigate to registration page",
            "Enter username with 100+ characters",
            "Fill other required fields",
            "Submit registration"
        ],
        expected_result="System should handle long usernames gracefully with proper validation"
    ))
    
    suite.add_test_case(TestCase(
        name="Special Characters in Input",
        description="Test input fields with special characters",
        steps=[
            "Navigate to registration page",
            "Enter username with special characters: !@#$%^&*()",
            "Enter email with special characters",
            "Submit registration"
        ],
        expected_result="System should properly validate and handle special characters"
    ))
    
    suite.add_test_case(TestCase(
        name="Empty Form Submission",
        description="Test form submission with empty fields",
        steps=[
            "Navigate to registration page",
            "Leave all fields empty",
            "Click submit button"
        ],
        expected_result="System should show appropriate validation errors"
    ))
    
    suite.add_test_case(TestCase(
        name="Duplicate Registration",
        description="Test registering with existing username/email",
        steps=[
            "Register a new user",
            "Try to register again with same username",
            "Try to register again with same email"
        ],
        expected_result="System should prevent duplicate registrations with clear error messages"
    ))
    
    suite.add_test_case(TestCase(
        name="Password Strength Validation",
        description="Test password strength requirements",
        steps=[
            "Navigate to registration page",
            "Try weak passwords: '123', 'password', 'abc'",
            "Try strong passwords with various combinations"
        ],
        expected_result="System should enforce password strength requirements"
    ))
    
    suite.add_test_case(TestCase(
        name="Session Timeout",
        description="Test session timeout behavior",
        steps=[
            "Login to the system",
            "Leave the page idle for extended period",
            "Try to perform an action"
        ],
        expected_result="System should handle session timeout gracefully"
    ))
    
    suite.add_test_case(TestCase(
        name="Browser Back Button",
        description="Test browser back button behavior",
        steps=[
            "Login to the system",
            "Navigate to different pages",
            "Use browser back button",
            "Check if authentication state is maintained"
        ],
        expected_result="Browser navigation should work correctly with proper authentication"
    ))
    
    suite.add_test_case(TestCase(
        name="Form Resubmission",
        description="Test form resubmission prevention",
        steps=[
            "Submit a form (registration, login, etc.)",
            "Use browser back button",
            "Try to resubmit the form"
        ],
        expected_result="System should prevent accidental form resubmission"
    ))
    
    suite.add_test_case(TestCase(
        name="Large File Upload",
        description="Test file upload with large files",
        steps=[
            "Navigate to file upload section",
            "Try to upload very large files (>10MB)",
            "Check system response"
        ],
        expected_result="System should handle large files appropriately with proper error messages"
    ))
    
    suite.add_test_case(TestCase(
        name="Concurrent User Actions",
        description="Test system behavior with multiple browser tabs",
        steps=[
            "Open multiple browser tabs",
            "Login to different accounts in each tab",
            "Perform actions simultaneously"
        ],
        expected_result="System should handle concurrent sessions correctly"
    ))
    
    suite.add_test_case(TestCase(
        name="Network Interruption",
        description="Test system behavior during network issues",
        steps=[
            "Start a critical operation (registration, exercise submission)",
            "Simulate network interruption",
            "Check system response and recovery"
        ],
        expected_result="System should handle network issues gracefully"
    ))
    
    suite.add_test_case(TestCase(
        name="Data Persistence",
        description="Test data persistence across sessions",
        steps=[
            "Create learning session and answer questions",
            "Close browser without submitting",
            "Reopen and login",
            "Check if data is preserved"
        ],
        expected_result="System should preserve user data appropriately"
    ))
    
    suite.add_test_case(TestCase(
        name="Accessibility Testing",
        description="Test accessibility features",
        steps=[
            "Use keyboard navigation only",
            "Check screen reader compatibility",
            "Test with high contrast mode",
            "Verify focus indicators"
        ],
        expected_result="System should be accessible to users with disabilities"
    ))
    
    suite.add_test_case(TestCase(
        name="Mobile Responsiveness",
        description="Test mobile device compatibility",
        steps=[
            "Access system on mobile device",
            "Test all major functions",
            "Check touch interactions",
            "Verify responsive design"
        ],
        expected_result="System should work well on mobile devices"
    ))
    
    suite.add_test_case(TestCase(
        name="Error Message Clarity",
        description="Test error message quality",
        steps=[
            "Trigger various error conditions",
            "Check error message clarity",
            "Verify error message helpfulness"
        ],
        expected_result="Error messages should be clear and helpful"
    ))
    
    suite.add_test_case(TestCase(
        name="Loading States",
        description="Test loading state indicators",
        steps=[
            "Perform operations that take time",
            "Check for loading indicators",
            "Verify user feedback during operations"
        ],
        expected_result="System should provide clear loading feedback"
    ))
    
    return suite

if __name__ == "__main__":
    print("InULearning Platform - Manual Exploratory Testing")
    print("="*60)
    print("This script will guide you through manual exploratory testing")
    print("to discover edge cases and UI/UX issues.")
    print("\nInstructions:")
    print("1. Follow the steps for each test case")
    print("2. Record actual results and observations")
    print("3. Note any issues or improvements needed")
    print("4. Continue until all tests are completed or you choose to stop")
    
    input("\nPress Enter to start testing...")
    
    suite = create_exploratory_test_suite()
    suite.run_all_tests() 