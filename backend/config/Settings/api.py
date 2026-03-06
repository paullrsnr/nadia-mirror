from pydantic_settings import BaseSettings


class ApiSettings(BaseSettings):
    API_PORT: int = 3333
    FRONTEND_ORIGIN: str = "http://localhost:5173"
