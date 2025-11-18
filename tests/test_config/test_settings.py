from pytest import MonkeyPatch

from day_play.config.environments import (
    ConfigForTesting,
    DevelopmentSettings,
)
from day_play.config.settings import get_settings


def test_get_settings_defaults_to_development() -> None:
    """Test that get_settings returns DevelopmentSettings by default."""
    settings = get_settings()
    assert isinstance(settings, DevelopmentSettings)
    assert settings.debug is True


def test_get_settings_respects_environment_variable(monkeypatch: MonkeyPatch) -> None:
    """Test that ENVIRONMENT variable selects correct settings class."""
    monkeypatch.setenv("ENVIRONMENT", "testing")
    settings = get_settings()
    assert isinstance(settings, ConfigForTesting)
    # Note: .env file may override the default, so just check it's set
    assert settings.database_url is not None
    assert settings.debug is True


def test_testing_settings_has_memory_database_as_default() -> None:
    """Test that ConfigForTesting class defines in-memory database as default."""
    # Check the class default (before env vars are applied)
    assert ConfigForTesting.model_fields["database_url"].default == "sqlite:///:memory:"
    assert ConfigForTesting.model_fields["debug"].default is True


def test_environment_variable_overrides_default(monkeypatch: MonkeyPatch) -> None:
    """Test that environment variables override default settings."""
    monkeypatch.delenv("APP_DATABASE_URL", raising=False)
    monkeypatch.setenv("APP_DATABASE_URL", "sqlite:///./custom.db")
    # Need to create new instance to pick up the env var
    settings = DevelopmentSettings()
    assert settings.database_url == "sqlite:///./custom.db"
