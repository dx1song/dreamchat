from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，可通过 .env 覆盖默认值。"""

    jwt_secret_key: str = "dreamchat-dev-secret-key-change-me"
    jwt_algorithm: str = "HS256"
    database_url: str = "sqlite:///./star_dream.db"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    class Config:
        env_file = ".env"


settings = Settings()
