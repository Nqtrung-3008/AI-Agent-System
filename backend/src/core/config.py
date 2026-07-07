from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SQL_ECHO: bool
    
    OLLAMA_BASE_URL: str
    OLLAMA_LLM_MODEL: str

    model_config = SettingsConfigDict(
        env_file=".env"
    )
        
settings = Settings()