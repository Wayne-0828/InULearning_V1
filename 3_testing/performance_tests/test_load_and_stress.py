"""
Load Testing and Stress Testing for InULearning Platform
Tests system performance under various load conditions
"""
import pytest
import asyncio
import time
import statistics
import httpx
import concurrent.futures
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PerformanceMetrics:
    """Performance metrics data class."""
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    endpoint: str
    method: str

@dataclass
class LoadTestResult:
    """Load test result data class."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    error_rate: float

class TestLoadAndStress:
    """Load and stress testing for the platform."""
    
    @pytest.fixture
    def performance_config(self):
        """Performance test configuration."""
        return {
            "base_url": "http://localhost:8001",
            "timeout": 30.0,
            "load_test_users": 100,
            "stress_test_users": 500,
            "spike_test_users": 1000,
            "test_duration": 60,  # seconds
            "ramp_up_time": 10,   # seconds
            "target_rps": 50,     # requests per second
            "acceptable_p95": 500, # milliseconds
            "acceptable_error_rate": 0.01  # 1%
        }
    
    @pytest.fixture
    def test_endpoints(self):
        """Test endpoints for performance testing."""
        return [
            {"url": "/api/v1/auth/health", "method": "GET", "weight": 0.1},
            {"url": "/api/v1/learning/health", "method": "GET", "weight": 0.1},
            {"url": "/api/v1/questions/health", "method": "GET", "weight": 0.1},
            {"url": "/api/v1/ai/health", "method": "GET", "weight": 0.1},
            {"url": "/api/v1/auth/register", "method": "POST", "weight": 0.2},
            {"url": "/api/v1/auth/login", "method": "POST", "weight": 0.2},
            {"url": "/api/v1/learning/exercises/create", "method": "POST", "weight": 0.1},
            {"url": "/api/v1/questions/", "method": "GET", "weight": 0.1}
        ]
    
    @pytest.fixture
    def test_data(self):
        """Test data for performance testing."""
        return {
            "user_registration": {
                "username": "perf_test_user",
                "email": "perf_test@example.com",
                "password": "TestPassword123!",
                "role": "student",
                "grade": "7A",
                "version": "南一"
            },
            "user_login": {
                "username": "perf_test_user",
                "password": "TestPassword123!"
            },
            "exercise_creation": {
                "grade": "7A",
                "subject": "數學",
                "version": "南一",
                "chapter": "整數的運算",
                "question_count": 5,
                "difficulty": "medium"
            }
        }
    
    async def make_request(
        self, 
        client: httpx.AsyncClient, 
        endpoint: Dict[str, Any], 
        test_data: Dict[str, Any]
    ) -> PerformanceMetrics:
        """Make a single request and return metrics."""
        start_time = time.time()
        
        try:
            if endpoint["method"] == "GET":
                response = await client.get(endpoint["url"])
            elif endpoint["method"] == "POST":
                # Select appropriate test data based on endpoint
                if "register" in endpoint["url"]:
                    data = test_data["user_registration"].copy()
                    data["username"] = f"{data['username']}_{int(time.time())}"
                    data["email"] = f"{data['username']}@example.com"
                elif "login" in endpoint["url"]:
                    data = test_data["user_login"]
                elif "exercises" in endpoint["url"]:
                    data = test_data["exercise_creation"]
                else:
                    data = {}
                
                response = await client.post(endpoint["url"], json=data)
            else:
                raise ValueError(f"Unsupported method: {endpoint['method']}")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return PerformanceMetrics(
                response_time=response_time,
                status_code=response.status_code,
                success=200 <= response.status_code < 400,
                timestamp=datetime.now(),
                endpoint=endpoint["url"],
                method=endpoint["method"]
            )
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return PerformanceMetrics(
                response_time=response_time,
                status_code=0,
                success=False,
                timestamp=datetime.now(),
                endpoint=endpoint["url"],
                method=endpoint["method"]
            )
    
    def calculate_metrics(self, metrics: List[PerformanceMetrics]) -> LoadTestResult:
        """Calculate performance metrics from raw data."""
        if not metrics:
            return LoadTestResult(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        response_times = [m.response_time for m in metrics]
        successful_requests = sum(1 for m in metrics if m.success)
        failed_requests = len(metrics) - successful_requests
        
        return LoadTestResult(
            total_requests=len(metrics),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=statistics.mean(response_times),
            p95_response_time=statistics.quantiles(response_times, n=20)[18],  # 95th percentile
            p99_response_time=statistics.quantiles(response_times, n=100)[98],  # 99th percentile
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            requests_per_second=len(metrics) / (max(m.timestamp for m in metrics) - min(m.timestamp for m in metrics)).total_seconds(),
            error_rate=failed_requests / len(metrics)
        )
    
    @pytest.mark.performance
    @pytest.mark.load
    async def test_baseline_performance(self, performance_config, test_endpoints, test_data):
        """Test baseline performance with low load."""
        print("\n=== Baseline Performance Test ===")
        
        async with httpx.AsyncClient(
            base_url=performance_config["base_url"],
            timeout=performance_config["timeout"]
        ) as client:
            metrics = []
            
            # Make 10 requests to establish baseline
            for _ in range(10):
                for endpoint in test_endpoints:
                    metric = await self.make_request(client, endpoint, test_data)
                    metrics.append(metric)
                    await asyncio.sleep(0.1)  # Small delay between requests
            
            result = self.calculate_metrics(metrics)
            
            print(f"Baseline Results:")
            print(f"  Total Requests: {result.total_requests}")
            print(f"  Success Rate: {(1 - result.error_rate) * 100:.2f}%")
            print(f"  Average Response Time: {result.avg_response_time:.2f}ms")
            print(f"  P95 Response Time: {result.p95_response_time:.2f}ms")
            print(f"  Requests per Second: {result.requests_per_second:.2f}")
            
            # Assert baseline performance
            assert result.error_rate < 0.05, f"Error rate too high: {result.error_rate}"
            assert result.avg_response_time < 1000, f"Average response time too high: {result.avg_response_time}ms"
    
    @pytest.mark.performance
    @pytest.mark.load
    async def test_load_test(self, performance_config, test_endpoints, test_data):
        """Test system performance under normal load."""
        print("\n=== Load Test (100 concurrent users) ===")
        
        async with httpx.AsyncClient(
            base_url=performance_config["base_url"],
            timeout=performance_config["timeout"]
        ) as client:
            metrics = []
            
            # Simulate 100 concurrent users
            tasks = []
            for user_id in range(performance_config["load_test_users"]):
                for endpoint in test_endpoints:
                    task = self.make_request(client, endpoint, test_data)
                    tasks.append(task)
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and collect metrics
            for result in results:
                if isinstance(result, PerformanceMetrics):
                    metrics.append(result)
            
            result = self.calculate_metrics(metrics)
            
            print(f"Load Test Results:")
            print(f"  Total Requests: {result.total_requests}")
            print(f"  Success Rate: {(1 - result.error_rate) * 100:.2f}%")
            print(f"  Average Response Time: {result.avg_response_time:.2f}ms")
            print(f"  P95 Response Time: {result.p95_response_time:.2f}ms")
            print(f"  P99 Response Time: {result.p99_response_time:.2f}ms")
            print(f"  Requests per Second: {result.requests_per_second:.2f}")
            
            # Assert load test performance requirements
            assert result.error_rate < performance_config["acceptable_error_rate"], \
                f"Error rate exceeds acceptable threshold: {result.error_rate}"
            assert result.p95_response_time < performance_config["acceptable_p95"], \
                f"P95 response time exceeds acceptable threshold: {result.p95_response_time}ms"
    
    @pytest.mark.performance
    @pytest.mark.stress
    async def test_stress_test(self, performance_config, test_endpoints, test_data):
        """Test system performance under stress conditions."""
        print("\n=== Stress Test (500 concurrent users) ===")
        
        async with httpx.AsyncClient(
            base_url=performance_config["base_url"],
            timeout=performance_config["timeout"]
        ) as client:
            metrics = []
            
            # Simulate 500 concurrent users (stress test)
            tasks = []
            for user_id in range(performance_config["stress_test_users"]):
                for endpoint in test_endpoints:
                    task = self.make_request(client, endpoint, test_data)
                    tasks.append(task)
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and collect metrics
            for result in results:
                if isinstance(result, PerformanceMetrics):
                    metrics.append(result)
            
            result = self.calculate_metrics(metrics)
            
            print(f"Stress Test Results:")
            print(f"  Total Requests: {result.total_requests}")
            print(f"  Success Rate: {(1 - result.error_rate) * 100:.2f}%")
            print(f"  Average Response Time: {result.avg_response_time:.2f}ms")
            print(f"  P95 Response Time: {result.p95_response_time:.2f}ms")
            print(f"  P99 Response Time: {result.p99_response_time:.2f}ms")
            print(f"  Requests per Second: {result.requests_per_second:.2f}")
            
            # Stress test should still maintain reasonable performance
            assert result.error_rate < 0.1, f"Error rate too high under stress: {result.error_rate}"
            assert result.p95_response_time < 2000, f"P95 response time too high under stress: {result.p95_response_time}ms"
    
    @pytest.mark.performance
    @pytest.mark.spike
    async def test_spike_test(self, performance_config, test_endpoints, test_data):
        """Test system behavior under sudden spike in load."""
        print("\n=== Spike Test (1000 concurrent users) ===")
        
        async with httpx.AsyncClient(
            base_url=performance_config["base_url"],
            timeout=performance_config["timeout"]
        ) as client:
            metrics = []
            
            # Simulate sudden spike with 1000 concurrent users
            tasks = []
            for user_id in range(performance_config["spike_test_users"]):
                for endpoint in test_endpoints:
                    task = self.make_request(client, endpoint, test_data)
                    tasks.append(task)
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and collect metrics
            for result in results:
                if isinstance(result, PerformanceMetrics):
                    metrics.append(result)
            
            result = self.calculate_metrics(metrics)
            
            print(f"Spike Test Results:")
            print(f"  Total Requests: {result.total_requests}")
            print(f"  Success Rate: {(1 - result.error_rate) * 100:.2f}%")
            print(f"  Average Response Time: {result.avg_response_time:.2f}ms")
            print(f"  P95 Response Time: {result.p95_response_time:.2f}ms")
            print(f"  P99 Response Time: {result.p99_response_time:.2f}ms")
            print(f"  Requests per Second: {result.requests_per_second:.2f}")
            
            # Spike test - system should not completely fail
            assert result.error_rate < 0.2, f"Error rate too high under spike: {result.error_rate}"
    
    @pytest.mark.performance
    @pytest.mark.endurance
    async def test_endurance_test(self, performance_config, test_endpoints, test_data):
        """Test system performance over extended period."""
        print("\n=== Endurance Test (60 seconds sustained load) ===")
        
        async with httpx.AsyncClient(
            base_url=performance_config["base_url"],
            timeout=performance_config["timeout"]
        ) as client:
            metrics = []
            start_time = time.time()
            
            # Sustained load for 60 seconds
            while time.time() - start_time < performance_config["test_duration"]:
                # Make requests at target RPS
                batch_start = time.time()
                
                tasks = []
                for _ in range(performance_config["target_rps"]):
                    for endpoint in test_endpoints:
                        task = self.make_request(client, endpoint, test_data)
                        tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, PerformanceMetrics):
                        metrics.append(result)
                
                # Control rate
                batch_duration = time.time() - batch_start
                if batch_duration < 1.0:
                    await asyncio.sleep(1.0 - batch_duration)
            
            result = self.calculate_metrics(metrics)
            
            print(f"Endurance Test Results:")
            print(f"  Total Requests: {result.total_requests}")
            print(f"  Success Rate: {(1 - result.error_rate) * 100:.2f}%")
            print(f"  Average Response Time: {result.avg_response_time:.2f}ms")
            print(f"  P95 Response Time: {result.p95_response_time:.2f}ms")
            print(f"  P99 Response Time: {result.p99_response_time:.2f}ms")
            print(f"  Requests per Second: {result.requests_per_second:.2f}")
            
            # Endurance test should maintain consistent performance
            assert result.error_rate < performance_config["acceptable_error_rate"], \
                f"Error rate degraded over time: {result.error_rate}"
            assert result.p95_response_time < performance_config["acceptable_p95"] * 1.5, \
                f"Response time degraded over time: {result.p95_response_time}ms"
    
    @pytest.mark.performance
    @pytest.mark.api_specific
    async def test_api_endpoint_performance(self, performance_config, test_data):
        """Test performance of specific API endpoints."""
        print("\n=== API Endpoint Performance Test ===")
        
        async with httpx.AsyncClient(
            base_url=performance_config["base_url"],
            timeout=performance_config["timeout"]
        ) as client:
            endpoints_to_test = [
                {"url": "/api/v1/auth/health", "method": "GET", "name": "Auth Health"},
                {"url": "/api/v1/learning/health", "method": "GET", "name": "Learning Health"},
                {"url": "/api/v1/questions/health", "method": "GET", "name": "Question Bank Health"},
                {"url": "/api/v1/ai/health", "method": "GET", "name": "AI Analysis Health"},
            ]
            
            for endpoint in endpoints_to_test:
                metrics = []
                
                # Test each endpoint with 50 requests
                tasks = []
                for _ in range(50):
                    task = self.make_request(client, endpoint, test_data)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, PerformanceMetrics):
                        metrics.append(result)
                
                result = self.calculate_metrics(metrics)
                
                print(f"{endpoint['name']}:")
                print(f"  Average Response Time: {result.avg_response_time:.2f}ms")
                print(f"  P95 Response Time: {result.p95_response_time:.2f}ms")
                print(f"  Success Rate: {(1 - result.error_rate) * 100:.2f}%")
                
                # Each endpoint should meet performance requirements
                assert result.error_rate < 0.01, f"{endpoint['name']} error rate too high: {result.error_rate}"
                assert result.p95_response_time < 200, f"{endpoint['name']} P95 response time too high: {result.p95_response_time}ms"
    
    @pytest.mark.performance
    @pytest.mark.database
    async def test_database_performance(self, performance_config, test_data):
        """Test database-related operations performance."""
        print("\n=== Database Performance Test ===")
        
        async with httpx.AsyncClient(
            base_url=performance_config["base_url"],
            timeout=performance_config["timeout"]
        ) as client:
            # Test user registration (database write)
            registration_metrics = []
            for i in range(20):
                user_data = test_data["user_registration"].copy()
                user_data["username"] = f"db_test_user_{i}_{int(time.time())}"
                user_data["email"] = f"{user_data['username']}@example.com"
                
                start_time = time.time()
                try:
                    response = await client.post("/api/v1/auth/register", json=user_data)
                    end_time = time.time()
                    
                    metric = PerformanceMetrics(
                        response_time=(end_time - start_time) * 1000,
                        status_code=response.status_code,
                        success=200 <= response.status_code < 400,
                        timestamp=datetime.now(),
                        endpoint="/api/v1/auth/register",
                        method="POST"
                    )
                    registration_metrics.append(metric)
                except Exception:
                    end_time = time.time()
                    metric = PerformanceMetrics(
                        response_time=(end_time - start_time) * 1000,
                        status_code=0,
                        success=False,
                        timestamp=datetime.now(),
                        endpoint="/api/v1/auth/register",
                        method="POST"
                    )
                    registration_metrics.append(metric)
            
            reg_result = self.calculate_metrics(registration_metrics)
            
            print(f"Database Write (Registration) Results:")
            print(f"  Average Response Time: {reg_result.avg_response_time:.2f}ms")
            print(f"  P95 Response Time: {reg_result.p95_response_time:.2f}ms")
            print(f"  Success Rate: {(1 - reg_result.error_rate) * 100:.2f}%")
            
            # Database operations should be reasonably fast
            assert reg_result.p95_response_time < 1000, f"Database write P95 too high: {reg_result.p95_response_time}ms"
    
    @pytest.mark.performance
    @pytest.mark.ai
    async def test_ai_service_performance(self, performance_config, test_data):
        """Test AI service performance."""
        print("\n=== AI Service Performance Test ===")
        
        async with httpx.AsyncClient(
            base_url=performance_config["base_url"],
            timeout=performance_config["timeout"]
        ) as client:
            # Test AI analysis endpoint
            ai_metrics = []
            
            # First create a learning session
            session_data = test_data["exercise_creation"]
            session_response = await client.post("/api/v1/learning/exercises/create", json=session_data)
            
            if session_response.status_code == 200:
                session_id = session_response.json().get("session_id")
                
                # Test AI analysis with the session
                for i in range(10):
                    start_time = time.time()
                    try:
                        response = await client.get(f"/api/v1/ai/analysis/{session_id}")
                        end_time = time.time()
                        
                        metric = PerformanceMetrics(
                            response_time=(end_time - start_time) * 1000,
                            status_code=response.status_code,
                            success=200 <= response.status_code < 400,
                            timestamp=datetime.now(),
                            endpoint=f"/api/v1/ai/analysis/{session_id}",
                            method="GET"
                        )
                        ai_metrics.append(metric)
                    except Exception:
                        end_time = time.time()
                        metric = PerformanceMetrics(
                            response_time=(end_time - start_time) * 1000,
                            status_code=0,
                            success=False,
                            timestamp=datetime.now(),
                            endpoint=f"/api/v1/ai/analysis/{session_id}",
                            method="GET"
                        )
                        ai_metrics.append(metric)
            
            if ai_metrics:
                ai_result = self.calculate_metrics(ai_metrics)
                
                print(f"AI Service Results:")
                print(f"  Average Response Time: {ai_result.avg_response_time:.2f}ms")
                print(f"  P95 Response Time: {ai_result.p95_response_time:.2f}ms")
                print(f"  Success Rate: {(1 - ai_result.error_rate) * 100:.2f}%")
                
                # AI service can be slower but should be consistent
                assert ai_result.p95_response_time < 5000, f"AI service P95 too high: {ai_result.p95_response_time}ms"
            else:
                pytest.skip("AI service not available for testing") 