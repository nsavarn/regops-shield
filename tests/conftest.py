"""Pytest configuration and shared fixtures for RegOps Shield test suite."""
import pytest
import os


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """Ensure safe defaults for all tests."""
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-placeholder")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-test-placeholder")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_placeholder")


@pytest.fixture
def sample_repo_url():
    """Return a sample repository URL for testing."""
    return "https://github.com/example/test-repo"


@pytest.fixture
def sample_policy_text():
    """Return sample policy text for testing."""
    return "All code must pass security scans before merge."
