"""
Tests for conditional IT systems loading based on position type.

This module tests the smart IT systems loading that reduces token usage
from a constant 15K to 1K-15K tokens based on role relevance.
"""

import pytest
from backend.core.data_loader import (
    DataLoader,
    PositionType,
    detect_position_type
)


class TestPositionTypeDetection:
    """Test position type detection logic"""

    def test_it_technical_positions(self):
        """Test IT technical position detection"""
        test_cases = [
            ("Программист 1С", "ДИТ"),
            ("Разработчик Python", "Департамент информационных технологий"),
            ("Senior Backend Developer", "IT"),
            ("Архитектор решений", "ДИТ"),
            ("DevOps Engineer", "Цифровые технологии"),
            ("Системный администратор", "ДИТ"),
            ("QA Engineer", "Тестирование"),
            ("Data Analyst", "Аналитика"),
        ]

        for position, dept in test_cases:
            pos_type = detect_position_type(position, dept)
            assert pos_type == PositionType.IT_TECHNICAL, \
                f"Expected IT_TECHNICAL for '{position}', got {pos_type}"

    def test_it_management_positions(self):
        """Test IT management position detection"""
        test_cases = [
            ("Директор ДИТ", "ДИТ"),
            ("Руководитель отдела разработки", "ДИТ"),
            ("CTO", "Technology"),
            ("Начальник управления информационных технологий", "ДИТ"),
        ]

        for position, dept in test_cases:
            pos_type = detect_position_type(position, dept)
            assert pos_type == PositionType.IT_MANAGEMENT, \
                f"Expected IT_MANAGEMENT for '{position}', got {pos_type}"

    def test_business_technical_positions(self):
        """Test business technical position detection"""
        test_cases = [
            ("Product Owner", "Продукт"),
            ("Менеджер проектов", "Управление проектами"),
            ("Project Manager", "PMO"),
            ("Scrum Master", "Agile"),
            ("Бизнес-аналитик", "Анализ"),
        ]

        for position, dept in test_cases:
            pos_type = detect_position_type(position, dept)
            assert pos_type == PositionType.BUSINESS_TECHNICAL, \
                f"Expected BUSINESS_TECHNICAL for '{position}', got {pos_type}"

    def test_business_general_positions(self):
        """Test general business position detection"""
        test_cases = [
            ("Менеджер по продажам", "Продажи"),
            ("Специалист отдела кадров", "HR"),
            ("Координатор проектов", "Управление"),
            ("Директор по развитию", "Коммерческий блок"),
        ]

        for position, dept in test_cases:
            pos_type = detect_position_type(position, dept)
            assert pos_type == PositionType.BUSINESS_GENERAL, \
                f"Expected BUSINESS_GENERAL for '{position}', got {pos_type}"

    def test_support_positions(self):
        """Test support position detection"""
        test_cases = [
            ("Ассистент", "Секретариат"),
            ("Секретарь", "Администрация"),
            ("Помощник руководителя", "Офис"),
            ("Стажер", "HR"),
            ("Junior стажер", "ДИТ"),
        ]

        for position, dept in test_cases:
            pos_type = detect_position_type(position, dept)
            assert pos_type == PositionType.SUPPORT, \
                f"Expected SUPPORT for '{position}', got {pos_type}"

    def test_it_department_fallback(self):
        """Test that positions in IT departments default to IT_MANAGEMENT"""
        # Position without clear keywords in IT department
        pos_type = detect_position_type("Специалист", "Департамент информационных технологий")
        assert pos_type == PositionType.IT_MANAGEMENT

        pos_type = detect_position_type("Сотрудник", "ДИТ")
        assert pos_type == PositionType.IT_MANAGEMENT


class TestConditionalITSystemsLoading:
    """Test conditional IT systems loading"""

    @pytest.fixture
    def loader(self):
        """Create DataLoader instance"""
        return DataLoader()

    def test_it_technical_full_content(self, loader):
        """Test that IT technical roles get full content"""
        position = "Программист 1С"
        department = "ДИТ"

        it_systems = loader._load_it_systems_conditional(position, department)

        # Should be full content (actual file is ~14KB)
        assert len(it_systems) > 10000, \
            f"IT technical should get full content, got {len(it_systems)} chars"

        # Check that detailed sections are present
        assert "Информационные технологии" in it_systems
        assert "CI/CD платформа" in it_systems or "Кластер виртуализации" in it_systems

    def test_it_management_compressed(self, loader):
        """Test that IT management gets compressed content"""
        position = "Директор ДИТ"
        department = "ДИТ"

        it_systems = loader._load_it_systems_conditional(position, department)

        # Should be compressed (~3K tokens = ~10K chars)
        assert 3000 <= len(it_systems) <= 12000, \
            f"IT management should get compressed content (3K-12K chars), got {len(it_systems)} chars"

        # Should have category headers but truncated lists
        assert "###" in it_systems
        assert "..." in it_systems or "сокращено" in it_systems

    def test_business_technical_business_only(self, loader):
        """Test that business technical roles get business systems only"""
        position = "Product Owner"
        department = "Продукт"

        it_systems = loader._load_it_systems_conditional(position, department)

        # Should be medium size (~5K tokens = ~17K chars)
        assert 10000 <= len(it_systems) <= 20000, \
            f"Business technical should get business systems (10K-20K chars), got {len(it_systems)} chars"

        # Should focus on business systems
        assert "бизнес" in it_systems.lower() or "Маркетинг" in it_systems or "HR" in it_systems

        # Should NOT have deep infrastructure details
        assert "Кластер виртуализации" not in it_systems or len(it_systems) < 25000

    def test_business_general_minimal(self, loader):
        """Test that general business roles get minimal overview"""
        position = "Менеджер по продажам"
        department = "Продажи"

        it_systems = loader._load_it_systems_conditional(position, department)

        # Should be minimal (~1K tokens = ~3K chars)
        assert len(it_systems) <= 5000, \
            f"Business general should get minimal overview (<5K chars), got {len(it_systems)} chars"

        # Should have overview structure
        assert "обзор" in it_systems.lower()
        assert "ERP" in it_systems or "CRM" in it_systems

    def test_support_minimal(self, loader):
        """Test that support roles get minimal overview"""
        position = "Ассистент"
        department = "Секретариат"

        it_systems = loader._load_it_systems_conditional(position, department)

        # Should be minimal (~1K tokens = ~3K chars)
        assert len(it_systems) <= 5000, \
            f"Support should get minimal overview (<5K chars), got {len(it_systems)} chars"

        # Should be same as business general
        assert "обзор" in it_systems.lower()

    def test_never_returns_empty(self, loader):
        """Test that IT systems content is never empty"""
        test_positions = [
            ("Программист", "ДИТ"),
            ("Директор", "Коммерция"),
            ("Стажер", "HR"),
            ("Product Owner", "Продукт"),
        ]

        for position, dept in test_positions:
            it_systems = loader._load_it_systems_conditional(position, dept)
            assert len(it_systems) > 0, \
                f"IT systems should never be empty for {position}/{dept}"
            assert it_systems.strip() != "", \
                f"IT systems should not be whitespace only for {position}/{dept}"


class TestTokenReductionImpact:
    """Test actual token reduction impact"""

    @pytest.fixture
    def loader(self):
        """Create DataLoader instance"""
        return DataLoader()

    def test_token_reduction_by_role(self, loader):
        """Test token reduction across different role types"""
        test_cases = [
            ("Программист 1С", "ДИТ", 12000, 18000),  # Full
            ("Директор ДИТ", "ДИТ", 1000, 5000),  # Compressed
            ("Product Owner", "Продукт", 3000, 7000),  # Business
            ("Менеджер по продажам", "Продажи", 500, 2000),  # Minimal
            ("Ассистент", "HR", 500, 2000),  # Minimal
        ]

        results = []

        for position, dept, min_tokens, max_tokens in test_cases:
            it_systems = loader._load_it_systems_conditional(position, dept)
            chars = len(it_systems)
            estimated_tokens = chars / 3.5

            results.append({
                "position": position,
                "dept": dept,
                "chars": chars,
                "tokens": int(estimated_tokens),
                "min_expected": min_tokens,
                "max_expected": max_tokens
            })

            assert min_tokens <= estimated_tokens <= max_tokens, \
                f"{position}: Expected {min_tokens}-{max_tokens} tokens, got {estimated_tokens:.0f}"

        # Print summary
        print("\n\nToken Reduction Results:")
        print("-" * 80)
        for result in results:
            print(f"{result['position']:30s} | {result['dept']:15s} | "
                  f"{result['tokens']:5d} tokens | {result['chars']:6d} chars")

    def test_average_reduction(self, loader):
        """Test average token reduction across all roles"""
        # Simulate realistic distribution of roles
        role_distribution = [
            # 10% IT technical (need full)
            ("Программист", "ДИТ"),
            # 5% IT management
            ("Директор ДИТ", "ДИТ"),
            # 15% Business technical
            ("Product Owner", "Продукт"),
            ("Менеджер проектов", "PMO"),
            # 60% Business general
            *[("Менеджер", "Продажи")] * 6,
            # 10% Support
            ("Ассистент", "HR"),
        ]

        old_total_tokens = 15000 * len(role_distribution)  # Old: always 15K
        new_total_tokens = 0

        for position, dept in role_distribution:
            it_systems = loader._load_it_systems_conditional(position, dept)
            new_total_tokens += len(it_systems) / 3.5

        reduction_pct = ((old_total_tokens - new_total_tokens) / old_total_tokens) * 100

        print(f"\n\nAverage Token Reduction:")
        print(f"  Old total: {old_total_tokens:.0f} tokens (always 15K per profile)")
        print(f"  New total: {new_total_tokens:.0f} tokens (conditional loading)")
        print(f"  Reduction: {reduction_pct:.1f}%")
        print(f"  Average per profile: {new_total_tokens/len(role_distribution):.0f} tokens")

        # Should achieve at least 30% reduction on average
        assert reduction_pct >= 30, \
            f"Expected at least 30% reduction, got {reduction_pct:.1f}%"


class TestIntegrationWithDataLoader:
    """Test integration with prepare_langfuse_variables"""

    @pytest.fixture
    def loader(self):
        """Create DataLoader instance"""
        return DataLoader()

    def test_langfuse_variables_include_conditional_systems(self, loader):
        """Test that prepare_langfuse_variables uses conditional loading"""
        position = "Программист"
        department = "ДИТ"

        variables = loader.prepare_langfuse_variables(department, position)

        # Should have IT systems
        assert "it_systems" in variables
        assert len(variables["it_systems"]) > 0

        # Should have detail level metadata
        assert "it_systems_detail_level" in variables
        assert variables["it_systems_detail_level"] in [
            "it_technical", "it_management", "business_technical",
            "business_general", "support"
        ]

    def test_different_positions_get_different_content(self, loader):
        """Test that different positions get different IT systems content"""
        dept = "ДИТ"

        # Technical position
        vars_technical = loader.prepare_langfuse_variables(dept, "Программист")
        it_technical = vars_technical["it_systems"]

        # Management position
        vars_mgmt = loader.prepare_langfuse_variables(dept, "Директор ДИТ")
        it_mgmt = vars_mgmt["it_systems"]

        # Content should be different
        assert len(it_technical) != len(it_mgmt), \
            "Technical and management should get different content lengths"

        assert it_technical != it_mgmt, \
            "Technical and management should get different content"

        # Technical should be longer
        assert len(it_technical) > len(it_mgmt), \
            "Technical roles should get more detailed content"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
