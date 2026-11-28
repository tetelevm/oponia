# Game fixtures

After [applying migrations](launch.md), run from the repository root:

```bash
docker compose exec game python fixtures.py load v-test
docker compose exec game python fixtures.py remove v-test
```

For local Python, run `uv run python fixtures.py <load|remove> v-test` from
`backend/game`. Compose mounts `fixtures/` read-only at `/fixtures`.

## Loading and removal

Loading matches entities by slug and images by label, preserving existing IDs.
Only supplied entity fields are updated; unchanged records and files are kept.
Connection and placement lists are replaced, including clearing omitted lists.
Entities absent from the fixture set are preserved. Duplicate image labels in
the database block loading.

Each command uses one database transaction. Failed loads remove newly written
files. Replaced image files are removed after commit unless another image record
references them. ASCII-only changes preserve the image URL and file.

Removal deletes matching records and their placement/inventory links, then
unreferenced local image files. Missing records and files are ignored; fixture
source files are preserved. Characters are preserved, and an occupied location
blocks removal. If file deletion fails after commit, database changes remain.

## File format

See `fixtures/v-test/` for examples. Loading proceeds in this order:

1. `images.yaml`: labels and image paths relative to the fixture set directory.
   Each image directory has `ascii.json`, mapping filename stems to arrays of
   ASCII rows: 80 x 20 for locations, 25 x 10 for enemies, 8 x 4 for items.
   Whitespace is preserved. Files are copied into [image storage](media.md).
2. `locations.yaml`: locations and directed `outgoing_connections`, with targets
   referenced by slug.
3. `enemies.yaml`: enemies and `location_links`, referencing locations by slug.
4. `items/*.yaml`: items and `location_links`. Empty files are allowed; item types
   use enum values and `lifetime` is a duration in seconds.

Entity `image` and `icon` fields reference image filename stems. Link fields
include `order` and unevaluated `conditions`. The loader does not load characters
or quest items; create a character in the [admin](admin.md) after loading.
