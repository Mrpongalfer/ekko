# File: src/ekko/config.py
"""
Project Ekko - Configuration Loading using Pydantic Settings.
Loads from .env files and environment variables.
"""

import logging
from pathlib import Path

from pydantic import DirectoryPath, Field, FilePath, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class AIServiceConfig(BaseSettings):
    """Configuration for a single AI provider."""

    api_key: str | None = Field(
        None, validation_alias="API_KEY"
    )  # Allow specific API_KEY var
    base_url: HttpUrl | None = None  # Optional base URL for self-hosted/proxied
    default_model: str | None = None


class EkkoSettings(BaseSettings):
    """Main configuration model for Ekko."""

    log_level: str = Field("INFO", validation_alias="EKKO_LOG_LEVEL")
    project_base_dir: DirectoryPath = Field(
        Path.home() / "ekko_projects", validation_alias="EKKO_PROJECT_BASE"
    )

    # AI Provider Config (Examples - adapt as needed)
    gemini_config: AIServiceConfig | None = Field(
        default=None, validation_alias="EKKO_GEMINI"
    )
    claude_config: AIServiceConfig | None = Field(
        default=None, validation_alias="EKKO_CLAUDE"
    )
    openai_config: AIServiceConfig | None = Field(
        default=None, validation_alias="EKKO_OPENAI"
    )
    ollama_config: AIServiceConfig = Field(
        default_factory=lambda: AIServiceConfig(
            base_url="http://localhost:11434", default_model="mistral"
        ),
        validation_alias="EKKO_OLLAMA",
    )

    primary_generator: str = Field(
        "gemini", validation_alias="EKKO_PRIMARY_GENERATOR"
    )  # Provider name
    security_validator: str = Field(
        "claude", validation_alias="EKKO_SECURITY_VALIDATOR"
    )
    docs_generator: str = Field("openai", validation_alias="EKKO_DOCS_GENERATOR")

    # Ansible & Terraform config
    ansible_playbook_dir: DirectoryPath | None = Field(
        None, validation_alias="EKKO_ANSIBLE_DIR"
    )
    terraform_dir: DirectoryPath | None = Field(
        None, validation_alias="EKKO_TERRAFORM_DIR"
    )

    # Scribe Integration (Path to scribe executable)
    scribe_agent_path: FilePath | None = Field(
        None, validation_alias="EKKO_SCRIBE_PATH"
    )

    # Model Config for Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=(
            Path() / "config" / ".env",
            Path.home() / ".config" / "ekko" / ".env",
        ),  # Load .env from project/config then user config
        env_prefix="EKKO_",  # e.g., EKKO_LOG_LEVEL=DEBUG
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars
        env_nested_delimiter="__",  # e.g., EKKO_GEMINI__API_KEY=...
    )


# Global settings instance (cached)
_settings_instance: EkkoSettings | None = None


def get_ekko_settings() -> EkkoSettings:
    """Loads and returns the Ekko settings, caching the instance."""
    if _settings_instance is None:
        logger.debug("Loading Ekko settings...")
        try:
            new_instance = EkkoSettings()
            logger.info("Ekko settings loaded successfully.")
            # Log some loaded settings for verification (avoid logging secrets)
            logger.debug(f"  Log Level: {new_instance.log_level}")
            logger.debug(f"  Project Base: {new_instance.project_base_dir}")
            logger.debug(f"  Primary LLM: {new_instance.primary_generator}")
            update_settings_instance(new_instance)
        except Exception as e:
            logger.error(
                f"FATAL: Failed to load/validate Ekko settings: {e}", exc_info=True
            )
            raise
    return _settings_instance


def update_settings_instance(new_instance):
    """Update the settings instance without using the global statement."""
    # global _settings_instance
    _settings_instance = new_instance


if __name__ == "__main__":
    # Example of loading and printing settings
    try:
        settings = get_ekko_settings()
        print("Ekko Settings Loaded:")
        # Be careful not to print sensitive data here in production
        print(
            settings.model_dump_json(
                indent=2, exclude={"gemini_config", "claude_config", "openai_config"}
            )
        )  # Exclude API keys
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
