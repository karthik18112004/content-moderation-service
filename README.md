# Content Moderation Backend Service

A robust backend service for content moderation featuring dynamic rate limiting, event-driven architecture, and scalable API design.

## Architecture Overview

```
┌─────────────┐     POST /submit      ┌─────────────┐
│   Client    │ ────────────────────► │  API        │
│             │ ◄──────────────────── │  Service    │
│             │     GET /status       │  (FastAPI)  │
└─────────────┘                       └──────┬──────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
             ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
             │ PostgreSQL  │          │   Redis     │          │ Moderation  │
             │  (content,  │          │  Pub/Sub    │          │ Processor   │
             │  results)   │          │  channel    │          │ (worker)    │
             └─────────────┘          └──────┬──────┘          └──────┬──────┘
                                             │                        │
                                             └────────────────────────┘
                                                    consumes events
```

### Components

- **API Service**: RESTful FastAPI service for content submission and status retrieval
- **Moderation Processor**: Worker service that consumes events from Redis and updates moderation results
- **PostgreSQL**: Stores content and moderation results
- **Redis**: Message queue (Pub/Sub) for event-driven processing

### Rate Limiting

Token Bucket algorithm applied per `userId`. Configurable via:
- `RATE_LIMIT_TOKENS_PER_MINUTE` (default: 5)
- `RATE_LIMIT_BUCKET_CAPACITY` (default: 5)

### Moderation Logic

- Content containing `badword` → `REJECTED`
- Otherwise: 80% `APPROVED`, 20% `REJECTED` (random)

## Project Structure

```
karthik/
├── src/
│   ├── api/              # API service
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── rate_limiter.py
│   │   ├── message_queue.py
│   │   ├── repositories.py
│   │   └── schemas.py
│   ├── processor/        # Moderation worker
│   │   ├── main.py
│   │   ├── consumer.py
│   │   └── moderation.py
│   └── common/           # Shared code
│       ├── config.py
│       ├── database.py
│       └── models.py
├── docker/
│   └── init.sql          # Database schema
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── API_DOCS.md
│   └── openapi.yaml
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.processor
├── requirements.txt
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### One-Command Setup (Docker)

```bash
docker-compose up -d
```

This starts:
- API on http://localhost:8000
- PostgreSQL on port 5432
- Redis on port 6379
- Moderation Processor (background worker)

### Verify

```bash
curl http://localhost:8000/health
```

### Submit Content

```bash
curl -X POST http://localhost:8000/api/v1/content/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "userId": "user-123"}'
```

Response (202 Accepted):
```json
{"contentId": "550e8400-e29b-41d4-a716-446655440000"}
```

### Get Status

```bash
curl http://localhost:8000/api/v1/content/{contentId}/status
```

Response (200 OK):
```json
{"contentId": "550e8400-e29b-41d4-a716-446655440000", "status": "APPROVED"}
```

## Local Development

1. Copy `.env.example` to `.env` and adjust values
2. Start PostgreSQL and Redis (e.g. `docker-compose up -d database redis`)
3. Install dependencies: `pip install -r requirements.txt`
4. Run API: `uvicorn src.api.main:app --reload --port 8000`
5. Run Processor: `python -m src.processor.main`

## Testing

### Unit Tests (no external services)

```bash
pytest tests/unit -v
```

### Integration Tests (requires docker-compose)

```bash
docker-compose up -d
pytest tests/integration -v -m integration
```

### All Tests

```bash
pytest tests -v
```

## API Documentation

- [API_DOCS.md](docs/API_DOCS.md) - Detailed endpoint documentation
- [openapi.yaml](docs/openapi.yaml) - OpenAPI 3.0 specification
- Swagger UI: http://localhost:8000/docs (when API is running)

## Environment Variables

See [.env.example](.env.example) for all configuration options.

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | `postgresql+asyncpg://user:password@localhost:5432/moderation_db` |
| REDIS_URL | Redis connection string | `redis://localhost:6379/0` |
| RATE_LIMIT_TOKENS_PER_MINUTE | Tokens per minute (Token Bucket) | 5 |
| RATE_LIMIT_BUCKET_CAPACITY | Bucket capacity | 5 |
| MODERATION_EVENTS_CHANNEL | Redis Pub/Sub channel | `content-moderation-events` |
| API_KEY | Optional API key for submit endpoint | (none) |

## License

MIT
