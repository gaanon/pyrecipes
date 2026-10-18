# Backups and restore

`backup_app.py` runs inside the app container and writes a timestamped folder to `~/recipes/backups/` on the server (`/code/backups` in the container):

| File | Contents | Restore with |
|---|---|---|
| `database_backup.sql` | Full MySQL dump, including the migration history | `mysql` (complete restore) |
| `image_backup.tar.gz` | All recipe photos (`~/recipes/uploads/`) | `tar` |
| `recipes_export.json` | Recipes, tags and the meal plan as JSON | `import_recipes.py` (update/merge) |

With `--gdrive-remote`, the folder is also copied to Google Drive. With `--days-to-keep N`, older backups are deleted, locally and on Google Drive. If any step fails, the script exits non-zero, so the failure shows up in `systemctl` and the journal.

Server setup is in [DEPLOY.md](DEPLOY.md).

## Daily backup

The `recipes-backup.timer` unit runs a backup every day at 02:00 (or at the next boot, if the server was off). It keeps 14 days of backups. The settings are on the `ExecStart` line of `~/.config/systemd/user/recipes-backup.service`:

- `--days-to-keep 14`: how many days to keep.
- `--gdrive-remote gdrive:recipe-backups`: the rclone remote and folder. Use the same path the Pi used (check `crontab -l` on the Pi). **That folder must hold only these backups**: rotation deletes anything in it older than `--days-to-keep`.

After editing the file, run `systemctl --user daemon-reload`.

```bash
systemctl --user enable --now recipes-backup.timer   # turn on
systemctl --user list-timers recipes-backup.timer    # next and last run
journalctl --user -u recipes-backup -n 30            # output of the last run
systemctl --user start recipes-backup.service        # back up now
```

## Google Drive

rclone runs inside the app container and reads `~/.config/rclone/rclone.conf` on the server.

- **Moving from the Pi:** copy the Pi's `~/.config/rclone/rclone.conf` to the same place on the server. It's already authorised.
- **New setup:** run `podman exec -it recipes-app rclone config`. Add a remote named `gdrive` of type Google Drive, and answer **No** to "Use auto config?". rclone then prints an `rclone authorize "drive" ...` command. Run that on any computer with rclone and a browser, and paste the result back.

Check access with `podman exec recipes-app rclone lsd gdrive:`.

## Restore

To restore from Google Drive, first copy the backup folder back into `~/recipes/backups/`:

```bash
podman exec recipes-app rclone copy gdrive:recipe-backups/<timestamp> /code/backups/<timestamp>
```

### Complete restore (database and photos)

This replaces the whole database with the backup. Recipes added since the backup are lost.

```bash
B=~/recipes/backups/<timestamp>
systemctl --user stop recipes-app
podman exec -i recipes-db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' < "$B/database_backup.sql"
tar -xzf "$B/image_backup.tar.gz" -C ~/recipes/uploads
systemctl --user start recipes-app
```

The dump drops and re-creates every table, including the migration history. When the app starts, it applies any migrations added since the backup was taken.

### Restoring a dump made on the Raspberry Pi

Dumps from before the move have no migration history table. Restore it the same way as above, but **before starting the app**, delete the current migration history:

```bash
podman exec recipes-db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -e "DROP TABLE IF EXISTS alembic_version"'
```

Otherwise the app would believe the restored, older tables are already up to date. Without the table, it recognises them as the baseline schema and upgrades them.

### Restore or update recipes from the JSON export

This updates the recipes in the file (matched by id) and adds missing ones; recipes that aren't in the file are left alone. **If the file has a meal plan, it replaces the current one.** Either everything is imported or nothing is: an invalid file changes nothing, and the command exits with an error naming the bad recipe.

```bash
podman exec recipes-app python import_recipes.py /code/backups/<timestamp>/recipes_export.json
```

Photos aren't in the JSON; restore them from `image_backup.tar.gz` as shown above.

## Restore test

A backup is only good if it restores. Run this after the move and every few months. It loads the latest backup into a throwaway MySQL container and leaves the real database alone:

```bash
B=~/recipes/backups/$(ls -t ~/recipes/backups | head -1)
podman run -d --rm --name restore-test -e MYSQL_ROOT_PASSWORD=test -e MYSQL_DATABASE=recipe_db docker.io/library/mysql:8.0
until podman exec restore-test mysqladmin ping -h 127.0.0.1 -uroot -ptest --silent 2>/dev/null; do sleep 2; done
podman exec -i restore-test mysql -uroot -ptest recipe_db < "$B/database_backup.sql"
podman exec restore-test mysql -uroot -ptest recipe_db -e "SELECT COUNT(*) AS recipes FROM recipes; SELECT version_num FROM alembic_version"
tar -tzf "$B/image_backup.tar.gz" | grep -vc '/$'   # number of photos
podman stop restore-test                              # also deletes it (--rm)
```

The recipe and photo counts should match the app. If the `mysql` import fails, the backup is unusable: check `journalctl --user -u recipes-backup`.

## Local development

With the dev setup in `docker-compose.yml`:

```bash
docker compose exec app python backup_app.py   # writes to ./backups/; no Google Drive (rclone isn't configured in dev)
docker compose exec -T db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' < backups/<timestamp>/database_backup.sql
```
