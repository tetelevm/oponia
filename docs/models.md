# Game models

SQLAlchemy models live in `backend/game/models/game`; shared base models and
mixins live in `backend/game/models`. Import from `models` so Alembic sees all
metadata. Consult the model code for columns, defaults and constraints.

## Domain semantics

- `Base` supplies UUID IDs generated on insert; raw SQL must supply IDs.
- `Image` stores a path/URL and optional ASCII text. Display entities reference
  shared images and icons; deleting an image clears those references.
- `StatsMixin` provides stored health, damage, armor and arbitrary JSON effects
  for characters, enemies and items. Combat calculations are not implemented.
- `LocationConnection` is directed: A to B does not imply B to A.
  `EnemyLocation` and `ItemLocation` place entities in locations. These three
  associations carry `order` and unevaluated `conditions`.
- `Location.sell_multiplier`: null means no shop; zero is a valid coefficient.
- `Item.quantity` means initial uses, not inventory count. `CharacterItem`
  represents an individual inventory entry with remaining uses, durability,
  expiration and equipment state; duplicate character/item pairs are allowed.
- `Item.lifetime` is a duration; inventory `expires_at` is an absolute instant.
  Use timezone-aware datetimes. Copying initial values and computing expiration
  are not implemented.
- `QuestItem` and `CharacterQuestItem` store quest inventory. Visibility and
  lifetime behavior are not implemented.
- A location cannot be deleted while a character references it. Deleting a
  character or item removes its inventory associations, preserving the other side.

`MutableDict` tracks only top-level effect edits. Replace the JSON object after
nested edits. Association conditions use `MutableList` for in-place tracking.

## Migrations

Alembic is configured in `backend/game/alembic.ini` and `migrations/env.py`.
Revision `0001` creates the initial schema. Create further migrations only on
explicit user request.
Startup neither creates tables nor applies migrations.

Apply migrations manually with
`docker compose exec game alembic upgrade head`, or run
`uv run alembic upgrade head` from `backend/game` for a local database.
