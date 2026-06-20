from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_app_id: int
    github_app_private_key: str
    github_app_webhook_secret: str

    model_config = {"env_prefix": ""}
