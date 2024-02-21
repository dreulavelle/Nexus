from pathlib import Path
from pydantic import SecretStr, root_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings class for handling application settings"""
    version: str = "0.1.0"
    root_dir: Path = Path.cwd()
    data_dir: Path = root_dir / "data"
    rd_apitoken: SecretStr
    prowlarr_url: str
    prowlarr_apikey: SecretStr

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

    @root_validator(pre=True)
    def set_default_data_dir(cls, values):
        if values.get('data_dir') is None:
            root_dir = values.get('root_dir', Path.cwd())
            return {**values, 'data_dir': root_dir / 'data'}
        return values


settings = Settings()
