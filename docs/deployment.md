# Docker environment

See [launch.md](launch.md) for commands. `compose.yaml` defines six services:

- `frontend`: React build served by Nginx; `/api/` proxies to `game:8000/`.
- `game`: FastAPI; PostgreSQL-backed read endpoints.
- `fight`: RabbitMQ consumer for `fight.inbox`. It logs and acknowledges demo
  messages; combat and result publishing are not implemented.
- `postgres`, `redis`, `rabbitmq`: infrastructure. Redis is not used by game code.

Python services use separate uv projects and a shared Dockerfile. Source is
copied into images. Health checks control startup order; the fight worker uses
an expiring heartbeat file and exits on a closed connection or channel.

Published ports bind to `127.0.0.1`: web 8080, PostgreSQL 5432, Redis 6379,
AMQP 5672 and RabbitMQ UI 15672. Override host ports in `.env`; containers use
service names and standard internal ports. Public hosting and HTTPS are not set up.

Named volumes persist database and broker state. `docker compose down` preserves
those volumes; adding `--volumes` deletes their data. Changing `.env` credentials
does not update users in existing PostgreSQL or RabbitMQ volumes.
