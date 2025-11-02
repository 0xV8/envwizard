"""Framework-specific detection and configuration."""

from typing import Dict, List, Optional
from pathlib import Path


class FrameworkDetector:
    """Detect and provide framework-specific configurations."""

    FRAMEWORK_CONFIG = {
        "django": {
            "env_vars": [
                ("SECRET_KEY", "django-insecure-change-this-in-production"),
                ("DEBUG", "True"),
                ("ALLOWED_HOSTS", "localhost,127.0.0.1"),
                ("DATABASE_URL", "sqlite:///db.sqlite3"),
                ("DJANGO_SETTINGS_MODULE", "config.settings"),
            ],
            "description": "Django web framework detected",
        },
        "fastapi": {
            "env_vars": [
                ("APP_NAME", "FastAPI Application"),
                ("DEBUG", "True"),
                ("API_V1_PREFIX", "/api/v1"),
                ("DATABASE_URL", "sqlite:///./app.db"),
                ("SECRET_KEY", "change-this-secret-key"),
                ("ALGORITHM", "HS256"),
                ("ACCESS_TOKEN_EXPIRE_MINUTES", "30"),
            ],
            "description": "FastAPI framework detected",
        },
        "flask": {
            "env_vars": [
                ("FLASK_APP", "app.py"),
                ("FLASK_ENV", "development"),
                ("SECRET_KEY", "change-this-secret-key"),
                ("DATABASE_URL", "sqlite:///app.db"),
            ],
            "description": "Flask framework detected",
        },
        "streamlit": {
            "env_vars": [
                ("STREAMLIT_SERVER_PORT", "8501"),
                ("STREAMLIT_SERVER_ADDRESS", "localhost"),
                ("STREAMLIT_THEME_BASE", "light"),
            ],
            "description": "Streamlit framework detected",
        },
        "celery": {
            "env_vars": [
                ("CELERY_BROKER_URL", "redis://localhost:6379/0"),
                ("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
                ("CELERY_TASK_SERIALIZER", "json"),
                ("CELERY_RESULT_SERIALIZER", "json"),
            ],
            "description": "Celery task queue detected",
        },
    }

    DATABASE_CONFIG = {
        "postgresql": {
            "env_vars": [
                ("POSTGRES_HOST", "localhost"),
                ("POSTGRES_PORT", "5432"),
                ("POSTGRES_DB", "myapp"),
                ("POSTGRES_USER", "postgres"),
                ("POSTGRES_PASSWORD", "changeme"),
            ]
        },
        "mysql": {
            "env_vars": [
                ("MYSQL_HOST", "localhost"),
                ("MYSQL_PORT", "3306"),
                ("MYSQL_DATABASE", "myapp"),
                ("MYSQL_USER", "root"),
                ("MYSQL_PASSWORD", "changeme"),
            ]
        },
        "mongodb": {
            "env_vars": [
                ("MONGO_HOST", "localhost"),
                ("MONGO_PORT", "27017"),
                ("MONGO_DB", "myapp"),
                ("MONGO_USER", "admin"),
                ("MONGO_PASSWORD", "changeme"),
            ]
        },
        "redis": {
            "env_vars": [
                ("REDIS_HOST", "localhost"),
                ("REDIS_PORT", "6379"),
                ("REDIS_DB", "0"),
                ("REDIS_PASSWORD", ""),
            ]
        },
    }

    @classmethod
    def get_framework_config(cls, framework: str) -> Optional[Dict]:
        """Get configuration for a specific framework."""
        return cls.FRAMEWORK_CONFIG.get(framework)

    @classmethod
    def get_all_env_vars(cls, frameworks: List[str]) -> List[tuple]:
        """Get all environment variables for detected frameworks."""
        env_vars = []
        seen = set()

        # Add common variables
        common_vars = [
            ("ENVIRONMENT", "development"),
            ("LOG_LEVEL", "INFO"),
        ]

        for var, value in common_vars:
            if var not in seen:
                env_vars.append((var, value))
                seen.add(var)

        # Add framework-specific variables
        for framework in frameworks:
            config = cls.FRAMEWORK_CONFIG.get(framework)
            if config:
                for var, value in config["env_vars"]:
                    if var not in seen:
                        env_vars.append((var, value))
                        seen.add(var)

        return env_vars

    @classmethod
    def detect_database(cls, project_path: Path) -> Optional[str]:
        """Detect database type from project dependencies."""
        req_file = project_path / "requirements.txt"
        if not req_file.exists():
            return None

        content = req_file.read_text().lower()

        if "psycopg2" in content or "postgresql" in content:
            return "postgresql"
        elif "mysqlclient" in content or "pymysql" in content:
            return "mysql"
        elif "pymongo" in content or "mongoengine" in content:
            return "mongodb"
        elif "redis" in content:
            return "redis"

        return None

    @classmethod
    def get_database_env_vars(cls, db_type: str) -> List[tuple]:
        """Get environment variables for a specific database."""
        db_config = cls.DATABASE_CONFIG.get(db_type)
        if db_config:
            return db_config["env_vars"]
        return []
