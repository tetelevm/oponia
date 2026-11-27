# Settings

`backend/game/settings.py` uses pydantic-settings. `get_settings()` loads and
caches configuration on first use. It reads the root `.env` regardless of the
working directory; environment variables override the file. Extra keys are ignored.

Required: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`.
`POSTGRES_HOST` defaults to `localhost`; `POSTGRES_PORT` defaults to `5432`
and must be in 1–65535. The password uses `SecretStr`; unwrap it only when needed.

Compose passes selected variables from `.env` into containers; the file is not
included in images. See `.env.example` and `compose.yaml` for infrastructure
credentials and host port overrides. Do not commit `.env`.

Restart after configuration changes. Tests can disable dotenv loading with
`Settings(_env_file=None)` and reset the cache with `get_settings.cache_clear()`.
