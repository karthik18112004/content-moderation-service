# Architecture Document

## Design Decisions

### Event-Driven Architecture

Content submission is decoupled from moderation processing via Redis Pub/Sub. The API service publishes `ContentSubmitted` events after persisting content; the ModerationProcessor consumes these events asynchronously. Benefits:

- **Responsiveness**: API returns 202 immediately without waiting for moderation
- **Scalability**: Multiple processor instances can consume from the same channel
- **Resilience**: If the processor is down, events remain in Redis (note: Pub/Sub does not persist messages; for production, consider Redis Streams or a durable queue like RabbitMQ)

### Rate Limiting: Token Bucket

The Token Bucket algorithm was chosen over Leaky Bucket for:

- **Burst handling**: Allows short bursts up to bucket capacity
- **Simplicity**: Straightforward refill logic (tokens per minute)
- **Per-user isolation**: Each userId has an independent bucket

Configuration via `RATE_LIMIT_TOKENS_PER_MINUTE` and `RATE_LIMIT_BUCKET_CAPACITY` enables tuning without code changes.

### Database Schema

PostgreSQL with two tables:

- **content**: Stores submission metadata (id, user_id, text, created_at)
- **moderation_results**: Stores outcome (content_id, status, moderated_at)

The initial status is `PENDING`; the processor updates to `APPROVED` or `REJECTED`.

### Shared Code (src/common)

Models, config, and database connection logic are shared between the API and Processor to avoid duplication and ensure schema consistency.

## Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Redis Pub/Sub | Fast and simple, but messages are not persisted. For production workloads, Redis Streams or a durable queue is recommended. |
| In-memory rate limiter | Works for single-instance deployment. For horizontal scaling, use Redis-backed rate limiting. |
| Synchronous DB in API | Async SQLAlchemy with asyncpg provides non-blocking I/O and good throughput for moderate load. |

## Deployment

Docker Compose orchestrates four services with health checks and dependency ordering. The database schema is applied via `init.sql` on first startup.
