# Game API

Routes are relative to `/api` in Docker. See `/api/docs` for response schemas
and `/api/openapi.json` for the generated specification.

| GET route | Returns |
| --- | --- |
| `/character` | Current character, stored stats and progression |
| `/location` | Current location and outgoing destinations |
| `/enemies` | Enemies at the current location |
| `/enemies/{slug}` | Local enemy details and stored stats |
| `/shop` | All item categories if the location has a shop |
| `/shop/{item_type}` | Local shop items in the requested category |
| `/shop/{item_type}/{slug}` | Local item details matching the category |

## Shared behavior

- No authentication: `get_current_character()` selects one character without
  ordering. All clients share this temporary selection. No character returns 404.
- Successful responses include `character` and `location`; errors use `detail`.
  Public entity identifiers are slugs, not database IDs.
- `image_format=url|ascii` defaults to `url` and applies to images and icons.
  Representations contain `format` and `value`; absent images or representations
  return null without fallback. ASCII whitespace is preserved. Image hosting
  is not implemented, and stored paths are returned unchanged.
- Transitions, enemies and shop items sort by association `order`, then slug.
  Association conditions are ignored.
- A shop exists when `sell_multiplier` is not null, including zero. Missing
  shops, enemies or items return 404. Unknown categories or image formats return
  422. Prices and stats are stored values, without gameplay calculations.

## Code boundaries

In `backend/game`: `routes/` handles HTTP and builds responses, `services/`
performs game operations and queries, `schemas/` defines API shapes, and `models/`
defines storage. Services take `session` first, return ORM objects with needed
relationships loaded, and do not depend on FastAPI. `dependencies.py` resolves
current character/location; `database.py` supplies a session per request.

See [launch.md](launch.md) for tests and [models.md](models.md) for data semantics.
