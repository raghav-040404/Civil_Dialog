from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    nlp_module_path: str

    llm_service_url: str = "http://127.0.0.1:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()