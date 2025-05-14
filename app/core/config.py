from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, MySQLDsn

import pandas as pd
from pandas import DataFrame

import json
from pathlib import Path

CORE_DIR = Path("core")
KEYS_DIR = Path("keys")
PRIVATE_KEY_PATH = CORE_DIR / KEYS_DIR / "private.pem"
PUBLIC_KEY_PATH = CORE_DIR / KEYS_DIR / "public.pem"
PATH_DATA = Path("data")

with open(PATH_DATA / "headers.json", "r", encoding="utf-8") as f:
    headers = json.load(f)
    cookies = {
        c.split("=")[0].strip(): c.split("=", 1)[1].strip()
        for c in headers["Cookie"].split("; ")
    }


class PredicatorConfig(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    mean_player: DataFrame = pd.read_csv(PATH_DATA / "mean_player.csv")
    path_dir_models: Path = Path("ml_models")
    headers: dict = headers
    cookies: dict = cookies


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class DatabaseConfig(BaseModel):
    url: MySQLDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class JwtConfig(BaseModel):
    private: str = PRIVATE_KEY_PATH.read_text()
    public: str = PUBLIC_KEY_PATH.read_text()
    algorithm: str = "RS256"


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    balance: str = "/balance"
    models: str = "/models"
    forms: str = "/forms"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    version: ApiV1Prefix = ApiV1Prefix()


class WebConfig(BaseModel):
    title: str = "CSPrediction"


class CeleryConfig(BaseModel):
    broker: str = "redis://localhost:6379/0"
    backend: str = "redis://localhost:6379/0"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="API__",
    )

    run: RunConfig = RunConfig()
    db: DatabaseConfig
    jwt: JwtConfig = JwtConfig()
    api: ApiPrefix = ApiPrefix()
    predict: PredicatorConfig = PredicatorConfig()
    web: WebConfig = WebConfig()
    celery: CeleryConfig = CeleryConfig()


settings = Settings()
