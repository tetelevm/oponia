# Local Docker environment

This Compose setup runs the current application skeleton and its planned infrastructure.
Docker Engine and the Docker Compose plugin are required.

## Start

From the repository root, copy the example settings if `.env` does not exist:

```bash
cp .env.example .env
docker compose up --build -d --wait
```

The example credentials are for local development. Published ports bind to
`127.0.0.1`. This setup does not configure a public domain or HTTPS.

| Component | Address |
| --- | --- |
| Web client | http://localhost:8080 |
| Game API documentation | http://localhost:8080/api/docs |
| Game OpenAPI schema | http://localhost:8080/api/openapi.json |
| RabbitMQ management UI | http://localhost:15672 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| RabbitMQ AMQP | localhost:5672 |

Ports can be changed in `.env`. RabbitMQ UI credentials are
`RABBITMQ_DEFAULT_USER` and `RABBITMQ_DEFAULT_PASS` from that file.

## Services and networking

- `frontend` builds React with Node.js and serves the resulting files with Nginx.
  Nginx forwards `/api/` to `game`, removing the prefix. WebSocket upgrades are
  forwarded as well. The game server uses `/api` as its external root path so
  Swagger UI loads its schema through the proxy.
- `game` and `fight` use a shared Python Dockerfile with separate application
  directories and lockfiles. Dependencies are installed using `uv sync --locked`.
  Both applications run as a non-root user.
- `game` serves HTTP; `fight` is a Python RabbitMQ consumer with no HTTP server.
  Neither backend publishes a host port. Future combat commands and result
  events will travel through RabbitMQ. `game` can start independently of `fight`.
- PostgreSQL, Redis and RabbitMQ are reachable inside the Compose network using
  the service names `postgres`, `redis` and `rabbitmq` and their standard ports.
  Host port overrides in `.env` only affect connections from your computer.
- Health checks control startup order. The `game` check confirms that FastAPI
  serves its OpenAPI schema. The `fight` check reads a heartbeat file in `/tmp`,
  refreshed every two seconds after consumer registration while its connection
  and channel remain open. It becomes unhealthy if the heartbeat is older than
  ten seconds. The worker removes the file on shutdown.

Connection settings are passed to `game` as environment variables. The game
application does not read them yet: database access, Redis usage and message
publishing will be implemented with the game features. No database migrations
are created yet.

The fight worker uses `aio-pika` to connect to RabbitMQ and declare the durable
`fight.inbox` queue. Its placeholder handler logs and acknowledges each message;
only send demo messages for now. Combat processing and result publishing are
not implemented yet. Prefetch is set to one. This setup runs one worker;
ordering across multiple workers will need to be designed with combat state.

On a closed connection or channel the worker exits and Compose restarts it.
SIGINT and SIGTERM request a shutdown that closes the connection. The readiness
file is a local health signal, not persistent game state.

## Terminal client

The Textual client runs locally on the player's computer, separately from Compose.
From the repository root:

```bash
cd cli_ent
uv sync --locked
uv run python main.py
```

Press `q` or use the Quit button to exit. The client currently shows a greeting.
Future API requests will use the server's public API address (locally,
`http://localhost:8080/api`); API integration is not implemented yet.

## Everyday commands

```bash
docker compose ps
docker compose logs -f game fight
docker compose up --build -d --wait
docker compose down
```

Application source is copied into images. Rebuild after changing Python or
frontend files. For hot reload, use the local uv and Vite commands in the README.

## Persistent data

Named volumes store PostgreSQL data, Redis data (with AOF enabled) and RabbitMQ
state. `docker compose down` preserves them. RabbitMQ uses a stable hostname
so its node identity remains the same across container recreation.

Initialization credentials apply when the corresponding data volume is first
created. Editing `.env` does not change users or passwords in an existing
PostgreSQL or RabbitMQ installation.

To delete all local data and start again, deliberately run:

```bash
docker compose down --volumes
```

Container images use version tags; Python and JavaScript dependencies are
resolved from the committed lockfiles.
