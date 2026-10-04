import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DatabaseSettings:
    name: str
    user: str
    password: str
    host: str
    port: int

    @classmethod
    def from_environment(
        cls, environment: Mapping[str, str] | None = None
    ) -> "DatabaseSettings":
        if environment is None:
            load_dotenv(PROJECT_ROOT / ".env")
            environment = os.environ

        values = {
            "name": environment.get("DB_NAME", "").strip(),
            "user": environment.get("DB_USER", "").strip(),
            "password": environment.get("DB_PASSWORD", ""),
            "host": environment.get("DB_HOST", "").strip(),
            "port": environment.get("DB_PORT", "").strip(),
        }
        missing = [key for key, value in values.items() if value == ""]
        if missing:
            variables = ", ".join(f"DB_{key.upper()}" for key in missing)
            raise ValueError(f"Missing database configuration: {variables}")

        try:
            port = int(values["port"])
        except ValueError as error:
            raise ValueError("DB_PORT must be a number") from error

        if not 1 <= port <= 65535:
            raise ValueError("DB_PORT must be between 1 and 65535")

        return cls(
            name=values["name"],
            user=values["user"],
            password=values["password"],
            host=values["host"],
            port=port,
        )

    def connection_parameters(self) -> dict[str, str | int]:
        return {
            "dbname": self.name,
            "user": self.user,
            "password": self.password,
            "host": self.host,
            "port": self.port,
        }
