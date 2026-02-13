# Content Moderation API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### POST /api/v1/content/submit

Submit content for moderation.

**Request**

- **Method:** `POST`
- **Content-Type:** `application/json`
- **Headers (optional):** `X-API-Key: <api-key>` (required if `API_KEY` env is set)

**Request Body**

| Field   | Type   | Required | Description                    |
|---------|--------|----------|--------------------------------|
| text    | string | Yes      | Content text to moderate       |
| userId  | string | Yes      | User identifier (for rate limit)|

**Example**

```json
{
  "text": "Hello world, this is my submission",
  "userId": "user-123"
}
```

**Responses**

| Status | Description                                      |
|--------|--------------------------------------------------|
| 202 Accepted | Content accepted for moderation              |
| 400 Bad Request | Invalid input (empty text or userId)     |
| 429 Too Many Requests | Rate limit exceeded (per userId)  |
| 500 Internal Server Error | Server error                    |
| 401 Unauthorized | Invalid or missing API key (if configured) |

**202 Response Body**

```json
{
  "contentId": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### GET /api/v1/content/{contentId}/status

Retrieve the moderation status of content.

**Request**

- **Method:** `GET`
- **Path Parameter:** `contentId` (UUID)

**Responses**

| Status | Description                    |
|--------|--------------------------------|
| 200 OK | Status retrieved               |
| 404 Not Found | Content ID does not exist |
| 500 Internal Server Error | Server error          |

**200 Response Body**

```json
{
  "contentId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "APPROVED"
}
```

**Status values**

- `PENDING` – Content is queued, moderation not yet complete
- `APPROVED` – Content passed moderation
- `REJECTED` – Content failed moderation

---

### GET /health

Health check endpoint for Docker and load balancers.

**Response**

```json
{
  "status": "healthy",
  "database": "ok",
  "redis": "ok"
}
```

## Rate Limiting

- **Algorithm:** Token Bucket
- **Scope:** Per `userId`
- **Configuration:** `RATE_LIMIT_TOKENS_PER_MINUTE` (default: 5), `RATE_LIMIT_BUCKET_CAPACITY` (default: 5)
- **Response:** 429 Too Many Requests when limit exceeded

## Error Response Format

```json
{
  "detail": "Error message description"
}
```
