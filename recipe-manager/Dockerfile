# Debian release pinned so rebuilds get the same system packages
FROM python:3.11-slim-trixie

# Log output straight to the container logs
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# rclone (Google Drive backups): a pinned release, checked against the checksums published
# in its PGP-signed SHA256SUMS. To upgrade, change the version and both checksums from
# https://downloads.rclone.org/<version>/SHA256SUMS
ARG RCLONE_VERSION=v1.75.2
ARG RCLONE_SHA256_AMD64=349ac8fba6ff65d6247043f1750cdcb518ec5d500ef91463a10d37c0ccdf3702
ARG RCLONE_SHA256_ARM64=7e1e8d69654941b7b7df84ee74c5f7fb09cce7d5496947fb7bf16b55ff427d10

# mysqldump for backups; curl/unzip only to install rclone, then removed
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-mysql-client ca-certificates curl unzip && \
    arch="$(dpkg --print-architecture)" && \
    case "$arch" in \
        amd64) sha="$RCLONE_SHA256_AMD64" ;; \
        arm64) sha="$RCLONE_SHA256_ARM64" ;; \
        *) echo "No rclone checksum for architecture $arch" >&2; exit 1 ;; \
    esac && \
    curl -fsSLo /tmp/rclone.zip "https://downloads.rclone.org/$RCLONE_VERSION/rclone-$RCLONE_VERSION-linux-$arch.zip" && \
    echo "$sha  /tmp/rclone.zip" | sha256sum -c - && \
    unzip -j /tmp/rclone.zip "rclone-$RCLONE_VERSION-linux-$arch/rclone" -d /usr/local/bin && \
    chmod 755 /usr/local/bin/rclone && \
    rm /tmp/rclone.zip && \
    apt-get purge -y --auto-remove curl unzip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY backup_app.py import_recipes.py alembic.ini ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
