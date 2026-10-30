from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str = ""
    groq_model: str = "qwen/qwen3.6-27b"
    groq_text_model: str = "llama-3.3-70b-versatile"
    pubmed_email: str = "student@example.com"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

settings = Settings()
