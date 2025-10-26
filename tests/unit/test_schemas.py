"""
Unit tests for Pydantic schema models.

Tests validation, serialization, and type safety for all new typed models
introduced during the type safety refactoring.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.models.schemas import (
    # Profile models
    BasicInfo,
    Responsibility,
    ProfessionalSkill,
    ProfessionalSkillsByCategory,
    EducationExperience,
    CareerPaths,
    ProfileData,
    # Organization models
    OrganizationSearchItem,
    OrganizationPosition,
    OrganizationStructureNode,
    BusinessUnitsStats,
    PositionsStats,
    OrganizationSearchData,
    OrganizationPositionsData,
    OrganizationStructureData,
    OrganizationStatsData,
    # Dashboard models
    DashboardSummary,
    DashboardDepartments,
    DashboardPositions,
    DashboardProfiles,
    DashboardActiveTask,
    DataSources,
    DashboardMetadata,
    RecentProfile,
    DashboardActivitySummary,
    DashboardStatsData,
    DashboardActivityData,
    # Catalog models
    CatalogDepartment,
    CatalogPosition,
    CatalogStatistics,
    CatalogDepartmentDetails,
    CatalogSearchBreakdown,
    CatalogDepartmentsStats,
    CatalogPositionsStats,
    CatalogCacheStatus,
    CatalogDepartmentsData,
    CatalogPositionsData,
    CatalogSearchData,
    CatalogStatsData,
    # Common models
    PaginationInfo,
    FiltersApplied,
    GenerationMetadata,
)


# ================================
# PROFILE MODELS TESTS
# ================================


class TestBasicInfo:
    """Tests for BasicInfo model."""

    def test_valid_basic_info(self):
        """Test valid BasicInfo creation."""
        info = BasicInfo(
            position_title="Software Architect",
            department="IT Department",
            level=4,
            category="technical"
        )
        assert info.position_title == "Software Architect"
        assert info.department == "IT Department"
        assert info.level == 4

    def test_basic_info_optional_fields(self):
        """Test BasicInfo with optional fields."""
        info = BasicInfo(
            position_title="Manager",
            department="HR"
        )
        assert info.business_unit is None
        assert info.level is None


class TestResponsibility:
    """Tests for Responsibility model."""

    def test_valid_responsibility(self):
        """Test valid Responsibility creation."""
        resp = Responsibility(
            title="System Design",
            description="Design scalable systems",
            importance="high"
        )
        assert resp.title == "System Design"
        assert resp.importance == "high"


class TestProfessionalSkillsByCategory:
    """Tests for ProfessionalSkillsByCategory model."""

    def test_empty_skills_by_category(self):
        """Test empty skills categories."""
        skills = ProfessionalSkillsByCategory()
        assert skills.technical == []
        assert skills.management == []

    def test_populated_skills(self):
        """Test populated skills categories."""
        skills = ProfessionalSkillsByCategory(
            technical=[
                ProfessionalSkill(name="Python", level="expert"),
                ProfessionalSkill(name="FastAPI", level="advanced")
            ],
            management=[
                ProfessionalSkill(name="Team Leadership", level="advanced")
            ]
        )
        assert len(skills.technical) == 2
        assert len(skills.management) == 1
        assert skills.technical[0].name == "Python"


class TestEducationExperience:
    """Tests for EducationExperience model."""

    def test_valid_education(self):
        """Test valid EducationExperience."""
        edu = EducationExperience(
            required_education="Bachelor's in CS",
            required_experience_years=5
        )
        assert edu.required_experience_years == 5


class TestCareerPaths:
    """Tests for CareerPaths model."""

    def test_empty_career_paths(self):
        """Test empty career paths."""
        paths = CareerPaths()
        assert paths.vertical == []
        assert paths.horizontal == []

    def test_populated_paths(self):
        """Test populated career paths."""
        paths = CareerPaths(
            vertical=["Senior Architect", "Chief Architect"],
            horizontal=["Technical Lead", "Product Manager"]
        )
        assert len(paths.vertical) == 2
        assert len(paths.horizontal) == 2


# ================================
# ORGANIZATION MODELS TESTS
# ================================


class TestOrganizationSearchItem:
    """Tests for OrganizationSearchItem model."""

    def test_valid_search_item(self):
        """Test valid OrganizationSearchItem creation."""
        item = OrganizationSearchItem(
            display_name="IT / Development",
            full_path="Company / IT / Development",
            positions_count=25,
            hierarchy=["Company", "IT", "Development"]
        )
        assert item.display_name == "IT / Development"
        assert item.positions_count == 25
        assert len(item.hierarchy) == 3


class TestOrganizationPosition:
    """Tests for OrganizationPosition model."""

    def test_valid_position(self):
        """Test valid OrganizationPosition creation."""
        pos = OrganizationPosition(
            position_id="pos_123",
            position_name="Software Engineer",
            business_unit_id="bu_1",
            business_unit_name="IT",
            department_name="Development",
            department_path="IT/Development",
            profile_exists=True,
            profile_id=42
        )
        assert pos.position_id == "pos_123"
        assert pos.profile_exists is True
        assert pos.profile_id == 42


class TestBusinessUnitsStats:
    """Tests for BusinessUnitsStats model."""

    def test_valid_stats(self):
        """Test valid BusinessUnitsStats creation."""
        stats = BusinessUnitsStats(
            total_count=567,
            with_positions=545,
            by_levels={0: 9, 1: 27, 2: 91}
        )
        assert stats.total_count == 567
        assert stats.by_levels[0] == 9


class TestOrganizationSearchData:
    """Tests for OrganizationSearchData model."""

    def test_valid_search_data(self):
        """Test valid OrganizationSearchData creation."""
        data = OrganizationSearchData(
            items=[
                OrganizationSearchItem(
                    display_name="IT",
                    full_path="Company/IT",
                    positions_count=10,
                    hierarchy=["Company", "IT"]
                )
            ],
            total_count=1,
            source="path_based_indexing",
            includes_all_business_units=True
        )
        assert data.total_count == 1
        assert data.source == "path_based_indexing"
        assert len(data.items) == 1


# ================================
# DASHBOARD MODELS TESTS
# ================================


class TestDashboardSummary:
    """Tests for DashboardSummary model."""

    def test_valid_summary(self):
        """Test valid DashboardSummary creation."""
        summary = DashboardSummary(
            departments_count=510,
            positions_count=1487,
            profiles_count=19,
            completion_percentage=1.3,
            active_tasks_count=0
        )
        assert summary.departments_count == 510
        assert summary.completion_percentage == 1.3


class TestDataSources:
    """Tests for DataSources model."""

    def test_default_values(self):
        """Test DataSources default values."""
        sources = DataSources()
        assert sources.catalog == "cached"
        assert sources.profiles == "database"
        assert sources.tasks == "memory"

    def test_custom_values(self):
        """Test DataSources with custom values."""
        sources = DataSources(
            catalog="real-time",
            profiles="cached",
            tasks="redis"
        )
        assert sources.catalog == "real-time"
        assert sources.profiles == "cached"


class TestDashboardMetadata:
    """Tests for DashboardMetadata model."""

    def test_valid_metadata(self):
        """Test valid DashboardMetadata creation."""
        metadata = DashboardMetadata(
            last_updated="2025-10-26T12:00:00",
            data_sources=DataSources()
        )
        assert "2025-10-26" in metadata.last_updated
        assert metadata.data_sources.catalog == "cached"


class TestDashboardActiveTask:
    """Tests for DashboardActiveTask model."""

    def test_valid_active_task(self):
        """Test valid DashboardActiveTask creation."""
        task = DashboardActiveTask(
            task_id="task_123",
            position="Architect",
            department="IT",
            status="processing",
            progress=50,
            created_at="2025-10-26T12:00:00"
        )
        assert task.task_id == "task_123"
        assert task.progress == 50
        assert task.status == "processing"


class TestRecentProfile:
    """Tests for RecentProfile model."""

    def test_valid_recent_profile(self):
        """Test valid RecentProfile creation."""
        profile = RecentProfile(
            department="IT",
            position="Developer",
            employee_name="John Doe",
            created_at="2025-10-26T12:00:00",
            status="completed",
            created_by="admin"
        )
        assert profile.department == "IT"
        assert profile.status == "completed"


# ================================
# CATALOG MODELS TESTS
# ================================


class TestCatalogDepartment:
    """Tests for CatalogDepartment model."""

    def test_valid_catalog_department(self):
        """Test valid CatalogDepartment creation."""
        dept = CatalogDepartment(
            name="IT",
            display_name="Information Technology",
            path="Company/IT",
            positions_count=25,
            last_updated="2025-10-26T12:00:00"
        )
        assert dept.name == "IT"
        assert dept.positions_count == 25


class TestCatalogPosition:
    """Tests for CatalogPosition model."""

    def test_valid_catalog_position(self):
        """Test valid CatalogPosition creation."""
        pos = CatalogPosition(
            name="Software Architect",
            level=4,
            category="technical",
            department="IT",
            last_updated="2025-10-26T12:00:00"
        )
        assert pos.name == "Software Architect"
        assert pos.level == 4


class TestCatalogStatistics:
    """Tests for CatalogStatistics model."""

    def test_valid_statistics(self):
        """Test valid CatalogStatistics creation."""
        stats = CatalogStatistics(
            levels={1: 10, 2: 20, 3: 30},
            categories={"technical": 40, "management": 20}
        )
        assert stats.levels[1] == 10
        assert stats.categories["technical"] == 40


class TestCatalogCacheStatus:
    """Tests for CatalogCacheStatus model."""

    def test_valid_cache_status(self):
        """Test valid CatalogCacheStatus creation."""
        status = CatalogCacheStatus(
            departments_cached=True,
            positions_cached_count=567,
            centralized_cache=True,
            cache_type="organization_cache (path-based)"
        )
        assert status.departments_cached is True
        assert status.positions_cached_count == 567


# ================================
# COMMON MODELS TESTS
# ================================


class TestPaginationInfo:
    """Tests for PaginationInfo model."""

    def test_valid_pagination(self):
        """Test valid PaginationInfo creation."""
        pagination = PaginationInfo(
            page=1,
            limit=20,
            total=100,
            pages=5,
            has_next=True,
            has_prev=False
        )
        assert pagination.page == 1
        assert pagination.total == 100
        assert pagination.has_next is True


class TestFiltersApplied:
    """Tests for FiltersApplied model."""

    def test_empty_filters(self):
        """Test FiltersApplied with no filters."""
        filters = FiltersApplied()
        assert filters.query is None
        assert filters.department is None

    def test_populated_filters(self):
        """Test FiltersApplied with filters."""
        filters = FiltersApplied(
            query="architect",
            department="IT",
            status="completed"
        )
        assert filters.query == "architect"
        assert filters.department == "IT"


class TestGenerationMetadata:
    """Tests for GenerationMetadata model."""

    def test_valid_metadata(self):
        """Test valid GenerationMetadata creation."""
        metadata = GenerationMetadata(
            generation_time_seconds=2.5,
            input_tokens=1000,
            output_tokens=2000,
            total_tokens=3000,
            model_name="gemini-2.5-flash",
            temperature=0.1
        )
        assert metadata.generation_time_seconds == 2.5
        assert metadata.total_tokens == 3000
        assert metadata.temperature == 0.1


# ================================
# COMPLEX INTEGRATION TESTS
# ================================


class TestComplexModels:
    """Tests for complex nested models."""

    def test_dashboard_stats_data_complete(self):
        """Test complete DashboardStatsData creation."""
        data = DashboardStatsData(
            summary=DashboardSummary(
                departments_count=510,
                positions_count=1487,
                profiles_count=19,
                completion_percentage=1.3,
                active_tasks_count=0
            ),
            departments=DashboardDepartments(
                total=510,
                with_positions=488,
                average_positions=2.9
            ),
            positions=DashboardPositions(
                total=1487,
                with_profiles=19,
                without_profiles=1468,
                coverage_percent=1.3
            ),
            profiles=DashboardProfiles(
                total=19,
                percentage_complete=1.3
            ),
            active_tasks=[],
            metadata=DashboardMetadata(
                last_updated="2025-10-26T12:00:00",
                data_sources=DataSources()
            )
        )
        assert data.summary.departments_count == 510
        assert data.metadata.data_sources.catalog == "cached"

    def test_organization_structure_data_with_nodes(self):
        """Test OrganizationStructureData with nested nodes."""
        node = OrganizationStructureNode(
            name="IT Department",
            positions=["Architect", "Developer"],
            is_target=True
        )
        data = OrganizationStructureData(
            target_path="Company/IT",
            total_business_units=567,
            structure={"IT": node}
        )
        assert data.total_business_units == 567
        assert data.structure["IT"].name == "IT Department"
        assert data.structure["IT"].is_target is True


# ================================
# VALIDATION TESTS
# ================================


class TestValidation:
    """Tests for model validation."""

    def test_required_fields_validation(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError):
            # Missing required fields
            BasicInfo()

    def test_type_validation(self):
        """Test that field types are validated."""
        with pytest.raises(ValidationError):
            # Wrong type for positions_count
            OrganizationSearchItem(
                display_name="IT",
                full_path="IT",
                positions_count="not_a_number",  # Should be int
                hierarchy=[]
            )
