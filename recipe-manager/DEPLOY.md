# Deploying on the home server

The app runs on a Linux server on the home network, as two rootless Podman containers managed by systemd through [Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html) units:

| Unit | What it runs |
|---|---|
| `recipes-db` | MySQL 8.0; data in the Podman volume `recipes-db`. Not published on any port |
| `recipes-app` | The app, built from this repo, on port **8010**. Restarted automatically if `/healthz` keeps failing |
| `recipes-backup.timer` | Daily backup at 02:00 (see [BACKUP.md](BACKUP.md)) |

Everything lives under the user's home directory:

```
~/pyrecipes/                       this repository
~/recipes/app.env, db.env          settings and passwords (chmod 600)
~/recipes/uploads/                 recipe photos
~/recipes/backups/                 local backups
~/.config/rclone/rclone.conf       Google Drive access for backups
~/.config/containers/systemd/      Quadlet units (from deploy/quadlet/)
~/.config/systemd/user/            backup timer (from deploy/systemd/)
```

The app is meant for the home network only: there is no login. Don't forward port 8010 on the router.

## 1. Install

Requirements: **Podman 5.0 or newer** (`podman --version`; the database unit uses `Notify=healthy`) and git.

```bash
git clone <repo-url> ~/pyrecipes
mkdir -p ~/recipes/uploads ~/recipes/backups ~/.config/rclone ~/.config/containers/systemd ~/.config/systemd/user
```

Create the settings files:

```bash
cp ~/pyrecipes/recipe-manager/deploy/quadlet/db.env.example ~/recipes/db.env
cp ~/pyrecipes/recipe-manager/deploy/quadlet/app.env.example ~/recipes/app.env
chmod 600 ~/recipes/*.env
```

Edit both. **Don't put quotes around values**: Podman reads these files literally, so `AI_MODEL="x"` sets the model to `"x"`, quotes included. Generate the passwords with `openssl rand -hex 24`; hex keeps them safe to use inside `DATABASE_URL`, which would otherwise need special characters URL-encoded. The password in `DATABASE_URL` (`app.env`) must match `MYSQL_PASSWORD` (`db.env`). Add `AI_API_KEY` and `AI_MODEL` for the recipe scanner.

Build the image and install the units:

```bash
podman build -t localhost/recipe-manager:latest ~/pyrecipes/recipe-manager
cp ~/pyrecipes/recipe-manager/deploy/quadlet/*.{container,volume,network} ~/.config/containers/systemd/
cp ~/pyrecipes/recipe-manager/deploy/systemd/recipes-backup.* ~/.config/systemd/user/
sudo loginctl enable-linger "$USER"   # keep the services running when you're logged out
systemctl --user daemon-reload
```

`daemon-reload` turns the Quadlet files into `recipes-db.service` and `recipes-app.service`. They start at boot, but nothing is started yet.

Set up Google Drive for backups ([BACKUP.md](BACKUP.md#google-drive)), then either start with an empty database (2a) or move the data from the Raspberry Pi (2b).

## 2a. Start with an empty database

```bash
systemctl --user start recipes-app      # also starts recipes-db and waits until it's healthy
systemctl --user enable --now recipes-backup.timer
```

The app creates the tables on first start. Open `http://<server>:8010`.

## 2b. Move the data from the Raspberry Pi (one time)

Do this as a **trial run** first while the Pi keeps running, check everything, then repeat it for the real switch-over (step 6).

**The order matters:** restore the database *before* the app starts for the first time. If the app starts first, it creates empty tables and records them as up to date, and the restored Pi tables would then never be migrated.

1. **On the Pi**, from `~/pyrecipes/recipe-manager` (the Pi still runs the old compose file, with its default passwords):

   ```bash
   docker compose exec -T db mysqldump -u root -prootpassword --single-transaction --no-tablespaces recipe_db > ~/pi-recipe_db.sql
   tar -czf ~/pi-uploads.tar.gz -C uploads .
   docker compose exec -T db mysql -u root -prootpassword recipe_db -e "SELECT COUNT(*) AS recipes FROM recipes; SELECT COUNT(*) AS with_photo FROM recipes WHERE photo_path LIKE 'uploads/%'"
   ls uploads | wc -l
   ```

   Note the counts. The photo count should be at least the `with_photo` count.

2. **Copy to the server.** The files from step 1 are in the Pi user's home folder. Run this on the server; skip the second line if you've already copied `rclone.conf`, which gives backups their Google Drive access:

   ```bash
   scp <pi-user>@<pi-host>:'~/pi-recipe_db.sql ~/pi-uploads.tar.gz' ~/
   scp <pi-user>@<pi-host>:'~/.config/rclone/rclone.conf' ~/.config/rclone/
   chmod 600 ~/.config/rclone/rclone.conf
   ```

3. **On the server**, restore with the app still stopped:

   ```bash
   tar -xzf ~/pi-uploads.tar.gz -C ~/recipes/uploads
   systemctl --user start recipes-db
   podman exec -i recipes-db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' < ~/pi-recipe_db.sql
   ```

4. **Start the app.** On first start it recognises the Pi's database (tables, but no migration history), records it as the baseline schema, and applies the newer migrations:

   ```bash
   systemctl --user start recipes-app
   podman exec recipes-app alembic current   # expect: 0002_meal_plan_date_and_fk (head)
   podman exec recipes-app alembic check     # expect: No new upgrade operations detected.
   ```

   If `alembic check` lists differences, the Pi's tables didn't match the code's models; don't switch over until that's resolved with a migration.

5. **Check it works:**
   - `http://<server>:8010`: the recipe count matches the Pi, photos show, editing a recipe keeps its tags
   - the meal planner shows your planned meals on the right days
   - scan a recipe photo (checks the AI settings in `app.env`)
   - `podman healthcheck run recipes-app && echo healthy`
   - run a backup and check it, then do a restore test ([BACKUP.md](BACKUP.md#restore-test)):

     ```bash
     systemctl --user start recipes-backup.service
     journalctl --user -u recipes-backup -n 30   # expect: Backup process completed successfully!
     ```

6. **Switch over for real.** Stop the Pi's app so nothing changes during the move (`docker compose stop app` on the Pi), wipe the trial data on the server, and repeat steps 1–5 with a fresh dump:

   ```bash
   systemctl --user stop recipes-app recipes-db recipes-db-volume
   podman volume rm recipes-db
   rm -rf ~/recipes/uploads/*
   ```

   Then enable the daily backup: `systemctl --user enable --now recipes-backup.timer`.

7. **Retire the Pi** with `docker compose down`, *without* `-v`, so its data stays as a fallback for a few weeks.

## Updating

```bash
systemctl --user start recipes-backup.service   # take a backup first
cd ~/pyrecipes && git pull
podman build -t localhost/recipe-manager:latest recipe-manager
systemctl --user restart recipes-app
```

Database migrations run automatically when the app starts. If a change touched `deploy/`, copy the units again and run `systemctl --user daemon-reload` first.

## Day to day

```bash
systemctl --user status recipes-app recipes-db
journalctl --user -u recipes-app -f            # app logs
podman healthcheck run recipes-app && echo healthy
systemctl --user list-timers recipes-backup.timer
```

## Troubleshooting

- **`recipes-app.service` doesn't exist after `daemon-reload`.** Quadlet rejected a unit file. See why with `/usr/libexec/podman/quadlet -dryrun -user` (the path can differ by distribution).
- **First start of `recipes-db` takes minutes.** The first time, it downloads the MySQL image (about 600 MB) and creates the database; `systemctl` waits until MySQL is ready. Watch with `journalctl --user -u recipes-db -f`.
- **The recipe scanner fails.** The page shows the reason, and `journalctl --user -u recipes-app | grep -i provider` has the details. Check the values in `app.env` have no quotes (`podman exec recipes-app env | grep ^AI_`).
- **The app keeps restarting.** Look at `journalctl --user -u recipes-app -n 100`. A typo in `DATABASE_URL`, or a password that doesn't match `db.env`, shows up as a database connection error on startup.
- **The database won't start after changing `db.env`.** MySQL only reads `MYSQL_*` on the volume's first start; changing them later doesn't change the existing users. Change the password in MySQL itself, or start over with an empty volume.
- **Port 8010 is already in use.** Change the left side of `PublishPort=8010:8000` in `recipes-app.container`, then reinstall the unit and reload.
- **Photos missing after a restore.** Photos must be in `~/recipes/uploads/` with the file names from the database (`uploads/<name>` in `recipes.photo_path`).
