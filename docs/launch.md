# Running locally

Requires Docker Engine and the Docker Compose plugin. Run commands from the
repository root.

1. Prepare `.env` if it does not exist:

   ```bash
   cp .env.example .env
   ```

   If `.env` is empty or incomplete, fill missing entries from `.env.example`.
   Example values work locally. Credentials initialize new volumes only;
   editing `.env` does not update existing database or broker users.

2. Build and start the containers:

   ```bash
   docker compose up --build -d --wait
   ```

3. Create or update tables:

   ```bash
   docker compose exec game alembic upgrade head
   ```

   Repeat after updates; startup does not apply migrations automatically.

4. Load or update test fixtures:

   ```bash
   docker compose exec game python fixtures.py load v-test
   ```

   Create a character in the [admin](admin.md) and select a location; fixtures
   do not create characters. See [fixtures.md](fixtures.md) for import behavior.

5. Open http://localhost:8080/api/docs to inspect the API.
   The [game admin](admin.md) is at http://localhost:8080/api/admin/ when configured.
   The web client at http://localhost:8080 is currently blank.
   RabbitMQ UI: http://localhost:15672, using credentials from `.env`.

Rebuild after source changes. Useful commands:

```bash
docker compose ps
docker compose logs -f game fight
docker compose down
```

Ports bind to `127.0.0.1`; override host ports in `.env`. This Compose setup uses
HTTP for local development. `docker compose down` preserves named volumes;
`docker compose down --volumes` deletes database, broker and uploaded image data.
See [media.md](media.md) for image storage and backups.

## Terminal client

Requires Python 3.12+ and uv. From the repository root:

```bash
cd cli_ent
uv sync --locked
uv run python main.py
```

The client shows a greeting and has no API integration. Press `q` to exit.

## Tests

From `backend/game`:

```bash
uv sync --locked
uv run python -m unittest discover -s tests
```

HTTP tests use mocked database dependencies. Database tests require
`TEST_DATABASE_URL`, a PostgreSQL SQLAlchemy URL using `psycopg`:

```bash
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost/test_db \
  uv run python -m unittest discover -s tests
```

Use a test database whose user can create schemas. Each service test applies
migrations in a unique schema and drops that schema afterward. Without the
variable, database tests are skipped.
