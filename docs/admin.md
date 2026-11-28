# Game admin

Open `http://localhost:8080/api/admin/` to edit game records through SQLAdmin.

Set these variables in the root `.env` and recreate the game container:

- `ADMIN_USERNAME`: login name, defaults to `admin`.
- `ADMIN_PASSWORD`: login password. An empty or missing value disables the admin.
- `ADMIN_SECRET_KEY`: session signing secret, required when a password is set.
  Generate one with `openssl rand -hex 32`. Changing it invalidates sessions.

The example environment includes local development credentials. Sessions expire
after one hour. Admin login does not select a game character.

## Editing records

Create a character under Characters and choose an existing location to enable
the game API. Edit location connections, enemy placements and shop items under
World links; edit inventory through its separate sections. Conditions are stored
but not evaluated. Item lifetimes accept durations such as `1 day`; inventory
expiration timestamps use UTC.

For local images, enter a `/media/...` URL; see [media.md](media.md). The admin
does not upload files.

Edits write stored values directly without computing expiration or recalculating
stats. A location occupied by a character cannot be deleted.
