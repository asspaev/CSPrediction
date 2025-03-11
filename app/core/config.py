from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, MySQLDsn

from fastapi.security import OAuth2PasswordBearer

from pathlib import Path

CORE_DIR = Path("core")
KEYS_DIR = Path("keys")
PRIVATE_KEY_PATH = CORE_DIR / KEYS_DIR / "private.pem"
PUBLIC_KEY_PATH = CORE_DIR / KEYS_DIR / "public.pem"


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


class AuthConfig(BaseModel):
    scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="token")
    token_type: str = "bearer"

    class Config:
        arbitrary_types_allowed = True


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


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
    auth: AuthConfig = AuthConfig()
    api: ApiPrefix = ApiPrefix()


settings = Settings()