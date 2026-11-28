# Image storage

Caddy serves `/media/` on the same origin as the web client and API. For manual
files, place `media/locations/city.png` in the repository and store
`/media/locations/city.png` in `Image.image`. Files must be readable by Caddy;
changes need no rebuild or restart. Hidden files and directory listings are not
served. ASCII text is stored separately in `Image.ascii_art`.

## Backend storage

`backend/game/services/images.py` validates JPEG, PNG and WebP files up to 10 MiB
and 20 million pixels. Animated images are rejected; original bytes are retained.
`create_image(session, source, label=..., ascii_art=None)` accepts a binary file
positioned at its start, writes a UUID-named file and flushes an `Image` record.
It does not commit. `save_image_file(...)` saves a file without creating a record.
Callers own cleanup after a later transaction rollback; deleting an image record
does not automatically delete its file. No HTTP upload endpoint is implemented.

## Persistence

Local Python uses `MEDIA_ROOT/uploads/`, defaulting to the repository's
`media/uploads/`. Compose uses the `image_uploads` named volume, writable by
`game` and read-only in Caddy. It owns `/media/uploads/`, so keep manual files in
other subdirectories of `media/`.

Manual files survive `docker compose down --volumes`; uploaded files do not.
Both survive rebuilds and ordinary `docker compose down`. Image files are ignored
by Git. Back up `media/`, the upload volume and the database together; database
backups contain references only.
