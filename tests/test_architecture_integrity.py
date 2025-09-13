"""
@doc Architecture Integrity Test Suite

Comprehensive tests to verify architectural changes after major refactoring:
1. Service relocation integrity (markdown_service, storage_service)
2. Dependency injection implementation
3. Clean Architecture compliance
4. API functionality preservation
5. Data flow consistency

Examples:
    python> pytest tests/test_architecture_integrity.py -v
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ["OPENROUTER_API_KEY"] = "sk-or-test-key-12345678901234567890"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-that-is-long-enough-32-chars"
os.environ["DEVELOPMENT_MODE"] = "true"


@pytest.fixture
def test_db():
    """Create in-memory test database"""
    from backend.models.database import initialize_db_manager
    
    db = initialize_db_manager(":memory:")
    db.create_schema()
    db.seed_initial_data(
        admin_username="admin",
        admin_password="admin123",
        admin_full_name="Test Admin",
        hr_username="hr",
        hr_password="hr123",
        hr_full_name="Test HR"
    )
    yield db
    # Cleanup happens automatically with in-memory DB


class TestServiceRelocation:
    """Test that services were correctly relocated from services to core layer"""
    
    def test_markdown_service_in_core(self):
        """Verify ProfileMarkdownService is in core layer"""
        from backend.core.markdown_service import ProfileMarkdownService
        
        service = ProfileMarkdownService()
        assert service is not None
        assert hasattr(service, 'generate_from_json')
        assert hasattr(service, 'save_md_file')
    
    def test_storage_service_in_core(self):
        """Verify ProfileStorageService is in core layer"""
        from backend.core.storage_service import ProfileStorageService
        
        service = ProfileStorageService("/tmp/test")
        assert service is not None
        assert hasattr(service, 'create_profile_directory')
        assert hasattr(service, 'save_profile_files')
    
    def test_profile_generator_uses_relocated_services(self):
        """Verify ProfileGenerator uses the relocated services correctly"""
        from backend.core.profile_generator import ProfileGenerator
        from backend.core.markdown_service import ProfileMarkdownService
        from backend.core.storage_service import ProfileStorageService
        
        generator = ProfileGenerator()
        
        # Check that it uses the correct service types
        assert isinstance(generator.md_generator, ProfileMarkdownService)
        assert isinstance(generator.storage_service, ProfileStorageService)
        
        # Check no import errors or circular dependencies
        assert generator.md_generator is not None
        assert generator.storage_service is not None


class TestDependencyInjection:
    """Test the new dependency injection implementation"""
    
    def test_auth_interface_exists(self):
        """Verify AuthInterface protocol is defined"""
        from backend.core.interfaces import AuthInterface
        
        # Check it's a Protocol
        assert hasattr(AuthInterface, 'verify_token')
    
    def test_auth_service_implements_interface(self, test_db):
        """Verify AuthenticationService implements AuthInterface"""
        from backend.services.auth_service import AuthenticationService
        from backend.core.interfaces import AuthInterface
        
        service = AuthenticationService()
        
        # Check required method exists
        assert hasattr(service, 'verify_token')
        assert callable(service.verify_token)
        
        # Check it can be used as AuthInterface
        def use_auth(auth: AuthInterface):
            return auth.verify_token("test")
        
        # Should not raise TypeError
        result = use_auth(service)
        assert result is None or isinstance(result, dict)
    
    def test_middleware_uses_dependency_injection(self, test_db):
        """Verify RequestLoggingMiddleware uses DI"""
        from backend.api.middleware.logging_middleware import RequestLoggingMiddleware
        from backend.services.auth_service import AuthenticationService
        from fastapi import FastAPI
        
        app = FastAPI()
        auth_service = AuthenticationService()
        
        # Should accept auth_service via DI
        middleware = RequestLoggingMiddleware(app, auth_service=auth_service)
        
        assert middleware.auth_service is auth_service
    
    def test_database_manager_dependency_injection(self, test_db):
        """Verify DatabaseManager uses DI for path"""
        from backend.models.database import DatabaseManager
        
        # Test with custom path
        custom_db = DatabaseManager(":memory:")
        assert custom_db.db_path == ":memory:"
        
        # Test singleton pattern
        from backend.models.database import get_db_manager
        db1 = get_db_manager()
        db2 = get_db_manager()
        assert db1 is db2


class TestCatalogIntegration:
    """Test CatalogService integration with organization_cache"""
    
    def test_catalog_uses_organization_cache(self, test_db):
        """Verify CatalogService delegates to organization_cache"""
        from backend.services.catalog_service import CatalogService
        from backend.core.organization_cache import organization_cache
        
        catalog = CatalogService()
        
        # Should reference the singleton cache
        assert hasattr(catalog, 'organization_cache')
        assert catalog.organization_cache is organization_cache
    
    def test_catalog_methods_work(self, test_db):
        """Verify catalog methods still function correctly"""
        from backend.services.catalog_service import CatalogService
        
        catalog = CatalogService()
        
        # Test get_departments
        departments = catalog.get_departments()
        assert isinstance(departments, list)
        
        # Test get_positions (should handle missing department gracefully)
        positions = catalog.get_positions("NonExistent")
        assert isinstance(positions, list)
    
    def test_organization_cache_singleton(self):
        """Verify organization_cache is a true singleton"""
        from backend.core.organization_cache import organization_cache, OrganizationCacheManager
        
        cache1 = OrganizationCacheManager()
        cache2 = OrganizationCacheManager()
        
        assert cache1 is cache2
        assert cache1 is organization_cache


class TestCleanArchitecture:
    """Test Clean Architecture principles are maintained"""
    
    def test_no_circular_dependencies(self):
        """Verify no circular import dependencies"""
        # These imports should not cause circular dependency errors
        from backend.core.profile_generator import ProfileGenerator
        from backend.core.markdown_service import ProfileMarkdownService
        from backend.core.storage_service import ProfileStorageService
        from backend.services.catalog_service import CatalogService
        from backend.services.auth_service import AuthenticationService
        
        # All should import successfully
        assert ProfileGenerator is not None
        assert ProfileMarkdownService is not None
        assert ProfileStorageService is not None
        assert CatalogService is not None
        assert AuthenticationService is not None
    
    def test_layer_dependencies(self):
        """Verify proper layer dependencies (core should not depend on services)"""
        import ast
        import importlib.util
        
        # Read core modules
        core_files = [
            "backend/core/profile_generator.py",
            "backend/core/markdown_service.py",
            "backend/core/storage_service.py",
        ]
        
        for file_path in core_files:
            full_path = Path(__file__).parent.parent / file_path
            if not full_path.exists():
                continue
                
            with open(full_path, 'r') as f:
                tree = ast.parse(f.read())
            
            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and 'services' in node.module:
                        # Core should not import from services
                        # Exception: profile_generator may import for orchestration
                        if 'profile_generator' not in file_path:
                            pytest.fail(f"{file_path} imports from services layer: {node.module}")


class TestAPIFunctionality:
    """Test that API endpoints still work after refactoring"""
    
    @pytest.fixture
    def client(self, test_db):
        """Create test client"""
        from fastapi.testclient import TestClient
        from backend.main import app
        
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_catalog_endpoints(self, client):
        """Test catalog API endpoints"""
        # Get departments
        response = client.get("/api/catalog/departments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        
        # Get positions for department
        response = client.get("/api/catalog/positions/TestDept")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_auth_endpoint(self, client):
        """Test authentication endpoint"""
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


class TestDataFlow:
    """Test that data flows correctly through the refactored system"""
    
    def test_profile_generation_flow(self):
        """Test complete profile generation flow"""
        from backend.core.profile_generator import ProfileGenerator
        
        generator = ProfileGenerator()
        
        # Mock LLM response
        with patch.object(generator.llm_client, 'generate_completion') as mock_llm:
            mock_llm.return_value = {
                "profile": {
                    "position_title": "Test Position",
                    "department_specific": "Test Department",
                    "grade": "Senior",
                    "description": "Test description",
                    "responsibilities": ["Task 1", "Task 2"],
                    "professional_skills": {
                        "core_skills": ["Skill 1"],
                        "technical_skills": ["Tech 1"]
                    }
                }
            }
            
            # Should not raise any errors
            result = generator.generate_profile("Test Dept", "Test Position")
            assert result is not None
            assert "profile" in result
    
    def test_markdown_generation_flow(self):
        """Test markdown generation from profile data"""
        from backend.core.markdown_service import ProfileMarkdownService
        
        service = ProfileMarkdownService()
        
        test_profile = {
            "position_title": "Test Position",
            "department_specific": "Test Department", 
            "grade": "Senior",
            "description": "Test job description"
        }
        
        md_content = service.generate_from_json(test_profile)
        
        assert md_content is not None
        assert "Test Position" in md_content
        assert "Test Department" in md_content
    
    def test_storage_flow(self):
        """Test file storage flow"""
        from backend.core.storage_service import ProfileStorageService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            service = ProfileStorageService(tmpdir)
            
            # Create profile directory
            profile_dir = service.create_profile_directory(
                "Test Department",
                "Test Position"
            )
            
            assert profile_dir.exists()
            assert "Test_Department" in str(profile_dir)
            assert "Test_Position" in str(profile_dir)
            
            # Save files
            test_data = {"test": "data"}
            test_md = "# Test Markdown"
            
            json_path, md_path = service.save_profile_files(
                profile_dir,
                test_data,
                test_md
            )
            
            assert json_path.exists()
            assert md_path.exists()


class TestPerformanceImpact:
    """Test that refactoring didn't negatively impact performance"""
    
    def test_organization_cache_performance(self):
        """Test organization cache is performant"""
        import time
        from backend.core.organization_cache import organization_cache
        
        # First access might load data
        start = time.time()
        deps1 = organization_cache.get_all_departments()
        first_time = time.time() - start
        
        # Second access should be from cache
        start = time.time()
        deps2 = organization_cache.get_all_departments()
        second_time = time.time() - start
        
        # Cache should be faster (at least not slower)
        assert second_time <= first_time * 1.5  # Allow some variance
        assert deps1 == deps2  # Same data
    
    def test_singleton_initialization_performance(self):
        """Test singleton pattern doesn't cause performance issues"""
        import time
        from backend.core.organization_cache import OrganizationCacheManager
        
        instances = []
        start = time.time()
        
        for _ in range(100):
            instances.append(OrganizationCacheManager())
        
        elapsed = time.time() - start
        
        # Should be very fast since it's returning same instance
        assert elapsed < 0.1  # 100 calls in less than 100ms
        
        # All should be same instance
        assert all(i is instances[0] for i in instances)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])