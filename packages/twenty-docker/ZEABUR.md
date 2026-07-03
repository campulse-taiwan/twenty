# Twenty on Zeabur — Split Deployment Guide

Deploy Twenty with **four separate Zeabur services**: PostgreSQL, Redis, Server (API + UI), and Worker.

This guide matches the architecture in [`docker-compose.yml`](./docker-compose.yml) but adapted for Zeabur (no native docker-compose support).

## Architecture

```
Browser ──HTTPS──► server (API + frontend static, :3000)
                      ├──► postgresql
                      ├──► redis
worker (queue-worker) ──┬──► postgresql
                      └──► redis
```

## Files added for Zeabur

| File | Purpose |
|------|---------|
| [`Dockerfile.server`](../../Dockerfile.server) | Production build target `twenty` for the **server** service |
| [`Dockerfile.worker`](../../Dockerfile.worker) | Same image, runs `yarn worker:prod` |
| [`.github/workflows/zeabur-docker.yml`](../../.github/workflows/zeabur-docker.yml) | Build once, push to GHCR (Server + Worker share the image) |
| [`zeabur-template.yaml`](../../zeabur-template.yaml) | Optional one-click template |

Zeabur auto-matches `Dockerfile.server` when the service is named **server**, and `Dockerfile.worker` for **worker**.

---

## Option A — One-click template (recommended)

### 1. Publish Docker image to GHCR

1. Push this repo to GitHub.
2. Enable **Settings → Actions → General → Workflow permissions → Read and write packages**.
3. Run workflow **Zeabur Docker Build** (or push to `main`).
4. Note the image tag: `ghcr.io/<your-github-user>/twenty:main`

Make the package public (or configure Zeabur to pull private GHCR with credentials).

### 2. Deploy template

```bash
npx zeabur template deploy -f zeabur-template.yaml
```

Or import `zeabur-template.yaml` from the Zeabur dashboard.

Set variables during deploy:

| Variable | Example |
|----------|---------|
| `PUBLIC_DOMAIN` | Your Zeabur / custom domain |
| `ENCRYPTION_KEY` | Output of `openssl rand -base64 32` |
| `DOCKER_IMAGE` | `ghcr.io/your-user/twenty:main` |

---

## Option B — Manual dashboard setup

### Step 1 — Create project and databases

1. [Zeabur Dashboard](https://zeabur.com) → **New Project**
2. **Deploy New Service → Databases → PostgreSQL**
3. **Deploy New Service → Databases → Redis**
4. In PostgreSQL settings, set database name to **`default`** (matches Twenty compose)

Copy internal connection strings from each service’s **Connect** tab, or use Zeabur reference variables:

- `${POSTGRES_CONNECTION_STRING}` / `${POSTGRES_HOST}` etc.
- `${REDIS_URI}` or `${REDIS_CONNECTION_STRING}`

### Step 2 — Deploy Server

1. **Deploy New Service → Git** → select your fork
2. Service name: **`server`** (must match `Dockerfile.server`)
3. **Root Directory**: leave empty (monorepo builds from repo root)
4. If Zeabur does not pick up `Dockerfile.server`, set:

   ```
   ZBPACK_DOCKERFILE_PATH=Dockerfile.server
   ```

   Fallback (BuildKit include unsupported):

   ```
   ZBPACK_DOCKERFILE_PATH=packages/twenty-docker/twenty/Dockerfile
   ```

   and set **Docker Build Target** to `twenty` if available.

5. **Networking** → bind domain → set `SERVER_URL=https://your-domain`

#### Server environment variables

| Variable | Value |
|----------|-------|
| `NODE_PORT` | `3000` |
| `PORT` | `3000` |
| `PG_DATABASE_URL` | `postgres://USER:PASS@HOST:PORT/default` |
| `REDIS_URL` | `redis://:PASSWORD@HOST:PORT` |
| `SERVER_URL` | `https://your-public-domain` |
| `ENCRYPTION_KEY` | `openssl rand -base64 32` |
| `STORAGE_TYPE` | `local` (or `s3` for production without volumes) |

Do **not** set `DISABLE_DB_MIGRATIONS` or `DISABLE_CRON_JOBS_REGISTRATION` on the server.

#### Persistent storage (local files)

Mount a volume to:

```
/app/packages/twenty-server/.local-storage
```

Or use S3 (`STORAGE_TYPE=s3` + `STORAGE_S3_*` variables).

### Step 3 — Deploy Worker

**Recommended:** use the same GHCR image as Server (no second 20-minute build).

1. **Deploy New Service → Docker Image**
2. Image: `ghcr.io/your-user/twenty:main`
3. Service name: **`worker`**
4. **Start command**: `yarn worker:prod`
5. Set **depends on** Server (optional but recommended)

**Alternative:** Git service named **`worker`** (uses `Dockerfile.worker`; triggers a full rebuild).

#### Worker environment variables

Same as Server, plus:

| Variable | Value |
|----------|-------|
| `DISABLE_DB_MIGRATIONS` | `true` |
| `DISABLE_CRON_JOBS_REGISTRATION` | `true` |

Worker does not need a public domain.

---

## Verification checklist

After all services are running:

- [ ] Server logs show `Successfully migrated DB!`
- [ ] `GET https://<domain>/healthz` returns **200**
- [ ] `https://<domain>` shows the Twenty sign-in page
- [ ] Browser devtools → Network: GraphQL calls go to `https://<domain>/graphql`
- [ ] Worker logs show no PostgreSQL / Redis connection errors
- [ ] Create a test workflow or trigger a background job to confirm Worker processing

---

## Build notes

| Topic | Detail |
|-------|--------|
| Build time | First Git build ~15–30 min (monorepo + frontend) |
| Memory | Frontend build needs **8 GB+** RAM on the builder |
| Avoid double build | Use GHCR image for both Server and Worker |
| Custom zh-TW | Included when building from your fork; run `lingui compile` before commit |
| Include syntax | `Dockerfile.server` uses BuildKit `include`; if Zeabur fails, use `ZBPACK_DOCKERFILE_PATH` + target `twenty` |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Builds `twenty-app-dev` instead of production | Wrong Docker target; use `Dockerfile.server` or `--target twenty` |
| Frontend calls wrong API URL | Set `SERVER_URL` to the public HTTPS domain |
| Worker restarts loop | Ensure Server is healthy first; check `REDIS_URL` / `PG_DATABASE_URL` |
| Uploaded files disappear | Add volume on `.local-storage` or switch to S3 |
| OAuth / email links broken | `SERVER_URL` must match the public URL exactly (https) |

---

## Related documentation

- [Twenty self-host overview](https://docs.twenty.com/developers/self-host/self-host)
- [Docker Compose reference](./docker-compose.yml)
- [Environment variables](./.env.example)
- [Zeabur Dockerfile deploy](https://zeabur.com/docs/en-US/deploy/methods/dockerfile)
