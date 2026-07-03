# Twenty Docker deployment

Official Docker assets for self-hosting Twenty.

## Quick start

```bash
cp .env.example .env
# Edit .env — set SERVER_URL, ENCRYPTION_KEY, etc.
docker compose up -d
```

See [Twenty self-host docs](https://docs.twenty.com/developers/self-host/self-host).

## Zeabur (split services)

To deploy on [Zeabur](https://zeabur.com) with separated Server and Worker:

- Guide: [ZEABUR.md](./ZEABUR.md)
- Template: [zeabur-template.yaml](../../zeabur-template.yaml)
- Dockerfiles: [Dockerfile.server](../../Dockerfile.server), [Dockerfile.worker](../../Dockerfile.worker)
