# ADR-044: Unified Credentials Management

## Status
Accepted

## Date
2026-01-09

## Context

Credentials are stored in a single messy `keys.txt` file mixing API keys, OAuth tokens, database passwords, and system credentials. Per ADR-039, containers should mount credentials from `/mnt/storage/credentials/`.

## Decision

Organize credentials by **type** in `/mnt/storage/credentials/`:

```
credentials/
├── api-keys/     # .env files (GEMINI_API_KEY, OPENAI_API_KEY, etc.)
├── oauth/google/ # OAuth JSON files (credentials.json, token.json)
├── databases/    # Database .env files
└── system/       # Server/account credentials
```

**Security:** Directories 700, files 600, owned by root.

**Container usage:**
```yaml
volumes:
  - /mnt/storage/credentials/api-keys/gemini.env:/run/secrets/gemini.env:ro
```

## Rationale

- **Type-based over service-based:** Clear what kind of credential is where; services often need multiple types
- **.env format:** Standard, works with Docker, self-documenting
- **Simple for single-admin home lab:** No complex access control needed

## Consequences

**Positive:** Clear organization, container-friendly, standard format
**Negative:** Plaintext storage (accepted risk for home lab)
