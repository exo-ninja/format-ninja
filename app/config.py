import os
import json
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # App settings
    APP_NAME: str = os.getenv("APP_NAME", "format_ninja")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database settings
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "format_ninja")

    # GCP settings
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "exo-ninja")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")
    GCP_STORAGE_BUCKET: str = os.getenv("GCP_STORAGE_BUCKET", "format-ninja-bucket")
    GCP_TASKS_QUEUE: str = os.getenv("GCP_TASKS_QUEUE", "format-ninja-tasks")

    # Service account key file path (only used in development)
    GCP_SERVICE_ACCOUNT_KEY: str = os.getenv("GCP_SERVICE_ACCOUNT_KEY", "")

    # API Settings
    API_BASE_URL_DEV: str = os.getenv("API_BASE_URL_DEV", "")
    API_BASE_URL_PROD: str = os.getenv("API_BASE_URL_PROD", "")

    # Database URL
    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL database URL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def API_BASE_URL(self) -> str:
        """Get the appropriate base URL based on environment."""
        return (
            self.API_BASE_URL_PROD
            if self.ENVIRONMENT == "production"
            else self.API_BASE_URL_DEV
        )

    @property
    def use_gcp_service_account(self) -> bool:
        """Determine if service account key should be used."""
        return self.ENVIRONMENT == "development" and os.path.exists(
            self.GCP_SERVICE_ACCOUNT_KEY
        )

    def get_gcp_credentials(self):
        """Get GCP credentials if in development mode."""
        if not self.use_gcp_service_account:
            return None

        try:
            with open(self.GCP_SERVICE_ACCOUNT_KEY, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading GCP credentials: {e}")
            return None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()
