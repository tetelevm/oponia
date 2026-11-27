# Running locally

Requires Docker Engine and the Docker Compose plugin. Run commands from the
repository root.

1. Prepare `.env` if it does not exist:

   ```bash
   cp .env.example .env
   ```

   If `.env` is empty or incomplete, fill missing entries from `.env.example`.
   Example values work locally. Change `POSTGRES_PASSWORD`,
   `RABBITMQ_DEFAULT_PASS` and host ports as needed. Credentials initialize new
   volumes only; editing `.env` does not update existing database or broker users.

2. Build and start the containers:

   ```bash
   docker compose up --build -d --wait
   ```

   PostgreSQL creates the database on first initialization.

3. Create or update tables:

   ```bash
   docker compose exec game alembic upgrade head
   ```

   Run this after updates too; only pending migrations are applied.
   Startup does not apply migrations automatically.

4. Load test fixtures into an empty database:

   ```bash
   docker compose exec game python fixtures.py v-test
   ```

   Planned command: the loader and container access to fixture files are not
   implemented yet. Current fixtures do not create a character; game endpoints
   also require a character in the database.

5. Open http://localhost:8080/api/docs to inspect the API.
   The web client at http://localhost:8080 is currently blank.
   RabbitMQ UI: http://localhost:15672, using credentials from `.env`.

Rebuild after source changes. Useful commands:

```bash
docker compose ps
docker compose logs -f game fight
docker compose down
```

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

HTTP tests use mocked database dependencies. Three service tests require
`TEST_DATABASE_URL`, a PostgreSQL SQLAlchemy URL using the `psycopg` driver:

```bash
TEST_DATABASE_URL=postgresql+psycopg://user:password@localhost/test_db \
  uv run python -m unittest discover -s tests
```

Use a test database whose user can create schemas. Each service test applies
migrations in a unique schema and drops that schema afterward. Without the
variable, the three database tests are skipped.
