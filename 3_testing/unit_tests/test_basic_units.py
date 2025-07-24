"""
Basic Unit Tests
Simple unit tests for basic functionality
"""
import pytest
from typing import Dict, Any

class TestBasicUnits:
    """Basic unit tests for core functionality"""
    
    @pytest.mark.unit
    @pytest.mark.smoke
    def test_basic_math(self):
        """Test basic mathematical operations."""
        assert 2 + 2 == 4
        assert 10 - 5 == 5
        assert 3 * 4 == 12
        assert 15 / 3 == 5
    
    @pytest.mark.unit
    @pytest.mark.smoke
    def test_string_operations(self):
        """Test string operations."""
        test_string = "Hello, World!"
        assert len(test_string) == 13
        assert test_string.upper() == "HELLO, WORLD!"
        assert test_string.lower() == "hello, world!"
        assert "Hello" in test_string
    
    @pytest.mark.unit
    def test_list_operations(self):
        """Test list operations."""
        test_list = [1, 2, 3, 4, 5]
        assert len(test_list) == 5
        assert sum(test_list) == 15
        assert max(test_list) == 5
        assert min(test_list) == 1
    
    @pytest.mark.unit
    def test_dict_operations(self):
        """Test dictionary operations."""
        test_dict = {"name": "Test", "age": 25, "role": "student"}
        assert len(test_dict) == 3
        assert "name" in test_dict
        assert test_dict["age"] == 25
        assert test_dict.get("role") == "student"
    
    @pytest.mark.unit
    def test_boolean_operations(self):
        """Test boolean operations."""
        assert True is True
        assert False is False
        assert not False is True
        assert True and True is True
        assert True or False is True
    
    @pytest.mark.unit
    def test_none_handling(self):
        """Test None value handling."""
        test_value = None
        assert test_value is None
        assert test_value is not True
        assert test_value is not False
    
    @pytest.mark.unit
    def test_exception_handling(self):
        """Test exception handling."""
        with pytest.raises(ValueError):
            int("not_a_number")
        
        with pytest.raises(KeyError):
            empty_dict = {}
            _ = empty_dict["missing_key"]
        
        with pytest.raises(IndexError):
            empty_list = []
            _ = empty_list[0]
    
    @pytest.mark.unit
    def test_function_with_parameters(self):
        """Test function with parameters."""
        def add_numbers(a: int, b: int) -> int:
            return a + b
        
        assert add_numbers(1, 2) == 3
        assert add_numbers(-1, 1) == 0
        assert add_numbers(0, 0) == 0
    
    @pytest.mark.unit
    def test_class_instantiation(self):
        """Test class instantiation."""
        class TestClass:
            def __init__(self, name: str):
                self.name = name
            
            def get_name(self) -> str:
                return self.name
        
        test_obj = TestClass("TestObject")
        assert test_obj.name == "TestObject"
        assert test_obj.get_name() == "TestObject" 