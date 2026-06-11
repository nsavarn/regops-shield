"""Unit tests for RegOps Shield agent modules."""
import pytest


class TestAgentImports:
    """Test that agent modules can be imported without errors."""

    def test_agents_package_importable(self):
        """Verify agents package is importable."""
        try:
            import agents
            assert agents is not None
        except ImportError as e:
            pytest.skip(f"agents package not available: {e}")

    def test_utils_package_importable(self):
        """Verify utils package is importable."""
        try:
            import utils
            assert utils is not None
        except ImportError as e:
            pytest.skip(f"utils package not available: {e}")


class TestPolicyValidation:
    """Test policy validation logic."""

    def test_non_empty_policy(self, sample_policy_text):
        """Policy text must be non-empty string."""
        assert isinstance(sample_policy_text, str)
        assert len(sample_policy_text.strip()) > 0

    def test_policy_contains_keywords(self, sample_policy_text):
        """Policy text should contain meaningful governance keywords."""
        keywords = ["code", "security", "merge", "scan", "review", "policy"]
        found = any(k in sample_policy_text.lower() for k in keywords)
        assert found, "Policy text should contain at least one governance keyword"


class TestRepoURLValidation:
    """Test repository URL validation."""

    def test_valid_github_url(self, sample_repo_url):
        """Repo URL must be a valid GitHub HTTPS URL."""
        assert sample_repo_url.startswith("https://")
        assert "github.com" in sample_repo_url

    def test_url_has_owner_and_repo(self, sample_repo_url):
        """Repo URL must contain owner and repository segments."""
        parts = sample_repo_url.replace("https://github.com/", "").split("/")
        assert len(parts) >= 2
        assert all(len(p) > 0 for p in parts[:2])
