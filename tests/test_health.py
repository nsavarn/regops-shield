"""Health and smoke tests for RegOps Shield API."""
import pytest


def test_environment_is_test(set_test_env):
    """Verify test environment is correctly configured."""
    import os
    assert os.environ.get("ENVIRONMENT") == "test"


def test_openai_key_present(set_test_env):
    """Verify OpenAI API key placeholder is set."""
    import os
    assert os.environ.get("OPENAI_API_KEY") is not None


def test_github_token_present(set_test_env):
    """Verify GitHub token placeholder is set."""
    import os
    assert os.environ.get("GITHUB_TOKEN") is not None


def test_sample_repo_url(sample_repo_url):
    """Verify sample repo URL fixture returns a valid GitHub URL."""
    assert sample_repo_url.startswith("https://github.com/")


def test_sample_policy_text(sample_policy_text):
    """Verify sample policy fixture returns non-empty text."""
    assert len(sample_policy_text) > 0
    assert isinstance(sample_policy_text, str)
