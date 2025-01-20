from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str 
    REDIS_URL:str = "redis://localhost:6379/0"
    #  we are directly using redis url we don't need host and port 
    # REDIS_HOST: str = "localhost"
    # REDIS_PORT: int = 6379  
    # email support 
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool  =True
    VALIDATE_CERTS: bool  = True
    DOMAIN: str

    model_config = SettingsConfigDict(
        env_file= ".env",
        extra= "ignore"
    )

Config = Settings()


# broker_url = Config.REDIS_URL
# result_backend = Config.REDIS_URL
# broker_connection_retry_on_startup = True