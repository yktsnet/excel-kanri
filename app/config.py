from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    watch_dir: str = ""
    db_path: str = "./kanri.db"
    jwt_secret: str = "dev-insecure-secret-change-me"
    demo_mode: bool = False
    gotenberg_url: str = "http://localhost:3000"
    mapping_dir: str = "examples/mansion/mapping"
    generated_dir: str = "generated"


settings = Settings()
