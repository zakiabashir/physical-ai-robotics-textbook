# RAG API Documentation

## Overview

The Physical AI & Humanoid Robotics textbook implements a sophisticated Retrieval-Augmented Generation (RAG) system to provide accurate, context-aware AI assistance. This document describes all available RAG-related API endpoints.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

Currently, the RAG endpoints do not require authentication. However, rate limiting is applied to prevent abuse.

## Core Endpoints

### Chat API

#### POST /api/v1/chat/
Process a user message and generate an AI response using RAG.

**Request Body:**
```json
{
  "message": "What is Physical AI?",
  "context": {
    "lesson_id": "lesson-1",
    "chapter_id": "chapter-1",
    "section_title": "Introduction",
    "selected_text": "Physical AI integrates AI with physical systems"
  },
  "conversation_id": "optional-conversation-id",
  "user_id": "optional-user-id"
}
```

**Response:**
```json
{
  "message": "Physical AI is the integration of artificial intelligence...",
  "sources": [
    {
      "source": "physical-ai-robotics.org - Chapter 1",
      "title": "Introduction to Physical AI",
      "url": "https://physical-ai-robotics.org/docs/chapter-1/lesson-1",
      "score": 0.92,
      "chunk_id": "0"
    }
  ],
  "related_concepts": ["embodied intelligence", "perception-action loop"],
  "code_examples": [],
  "suggestions": [
    "Learn more about perception-action loops",
    "Try the hands-on lab exercises"
  ],
  "query_id": "uuid-here",
  "response_time": 1.234
}
```

## Ingestion API

### POST /api/v1/ingestion/all
Ingest all content from the sitemap into the vector database.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/all" \
  -H "accept: application/json"
```

**Response:**
```json
{
  "message": "Ingestion started in background",
  "status": "processing",
  "sitemap_url": "https://physical-ai-robotics.org/sitemap.xml",
  "collection_name": "humanoid_ai_book"
}
```

### POST /api/v1/ingestion/url
Ingest content from a single URL.

**Request Body:**
```json
{
  "url": "https://physical-ai-robotics.org/docs/chapter-1/lesson-1",
  "force": false
}
```

**Response:**
```json
{
  "url": "https://physical-ai-robotics.org/docs/chapter-1/lesson-1",
  "success": true,
  "chunks_created": 5,
  "chunks_stored": 5,
  "error": null
}
```

### GET /api/v1/ingestion/status
Get current ingestion status.

**Response:**
```json
{
  "collection_name": "humanoid_ai_book",
  "total_documents": 1250,
  "collections": ["humanoid_ai_book"],
  "sitemap_url": "https://physical-ai-robotics.org/sitemap.xml",
  "qdrant_url": "https://your-qdrant-url"
}
```

### POST /api/v1/ingestion/test
Test ingestion with a limited number of URLs.

**Query Parameters:**
- `limit` (optional): Number of URLs to test (default: 5)

**Response:**
```json
{
  "test_completed": true,
  "total_urls": 5,
  "successful_urls": 4,
  "failed_urls": 1,
  "total_chunks": 20,
  "duration": 12.34,
  "errors": [
    {
      "url": "https://example.com/failed",
      "error": "Connection timeout"
    }
  ]
}
```

### DELETE /api/v1/ingestion/clear
Clear the entire collection.

**Response:**
```json
{
  "message": "Collection humanoid_ai_book cleared successfully",
  "collection_name": "humanoid_ai_book"
}
```

## Health Monitoring API

### GET /api/v1/health
Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "version": "0.1.0"
}
```

### GET /api/v1/health/detailed
Detailed health check including all components.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "version": "0.1.0",
  "components": {
    "qdrant": {
      "status": "healthy",
      "collections": ["humanoid_ai_book"],
      "total_documents": 1250
    },
    "cohere": {
      "status": "healthy",
      "embedding_dimension": 1024
    },
    "gemini": {
      "status": "healthy",
      "model": "models/gemini-2.0-flash"
    },
    "retrieval": {
      "status": "healthy",
      "collection_name": "humanoid_ai_book",
      "can_retrieve": true
    }
  },
  "overall": "healthy"
}
```

### GET /api/v1/health/rag
RAG-specific health metrics.

**Response:**
```json
{
  "timestamp": 1703123456.789,
  "ingestion": {
    "status": "ready",
    "collection_exists": true,
    "document_count": 1250,
    "last_checked": 1703123456.789
  },
  "retrieval": {
    "status": "healthy",
    "query_time_ms": 45.67,
    "results_count": 5,
    "avg_score": 0.85
  },
  "generation": {
    "status": "healthy",
    "response_time_ms": 1234.56,
    "model": "models/gemini-2.0-flash",
    "max_tokens": 4000
  },
  "overall_status": "healthy"
}
```

### POST /api/v1/health/ingestion/test
Test the complete ingestion pipeline.

**Response:**
```json
{
  "timestamp": 1703123456.789,
  "tests": {
    "url_extraction": {
      "status": "passed",
      "urls_found": 45
    },
    "text_extraction": {
      "status": "passed",
      "url_tested": "https://physical-ai-robotics.org/docs/chapter-1",
      "chars_extracted": 5432,
      "title": "Chapter 1 Introduction"
    },
    "embedding": {
      "status": "passed",
      "embedding_dimension": 1024
    },
    "qdrant_storage": {
      "status": "passed",
      "vector_size": 1024
    }
  },
  "overall": "passed"
}
```

## Analytics API

### GET /api/v1/analytics/dashboard
Get analytics dashboard data.

**Query Parameters:**
- `days` (optional): Number of days to analyze (default: 7)

**Response:**
```json
{
  "period": {
    "start": "2024-01-01",
    "end": "2024-01-07",
    "days": 7
  },
  "daily_stats": [
    {
      "date": "2024-01-01",
      "queries": 150,
      "avg_retrieval_time": 0.045,
      "avg_generation_time": 1.234,
      "cache_hits": 120,
      "cache_misses": 30,
      "fallbacks": 0,
      "error_count": 0
    }
  ],
  "performance_metrics": {
    "total_queries": 1050,
    "avg_response_time": 1.279,
    "p95_response_time": 2.345,
    "p99_response_time": 3.456,
    "cache_hit_rate": 0.8,
    "error_rate": 0.01
  },
  "top_queries": [
    ["what is physical ai", 45],
    ["ros tutorial", 32],
    ["humanoid robot example", 28]
  ],
  "top_sources": [
    ["https://physical-ai-robotics.org/docs/chapter-1", 123],
    ["https://physical-ai-robotics.org/docs/chapter-2", 98]
  ],
  "feedback_distribution": {
    "1": 5,
    "2": 10,
    "3": 45,
    "4": 123,
    "5": 267
  },
  "query_analytics": {
    "avg_query_length": 12.3,
    "avg_retrieval_count": 3.2,
    "avg_relevance_score": 0.82,
    "avg_feedback_score": 4.1
  }
}
```

### POST /api/v1/analytics/feedback
Submit feedback for a query response.

**Request Body:**
```json
{
  "query_id": "uuid-from-chat-response",
  "score": 5,
  "comment": "Very helpful and accurate response",
  "source_clicks": ["https://physical-ai-robotics.org/docs/chapter-1"]
}
```

**Response:**
```json
{
  "message": "Feedback submitted successfully",
  "query_id": "uuid-here"
}
```

### GET /api/v1/analytics/export
Export analytics data.

**Query Parameters:**
- `format` (optional): Export format - json (default: json)

**Response:**
```json
{
  "export_timestamp": "2024-01-07T12:34:56.789Z",
  "performance_metrics": {...},
  "daily_stats": {...},
  "query_analytics": {...},
  "recent_queries": [...]
}
```

## Advanced Features

### Query Expansion
The system automatically expands queries using domain-specific synonyms and related terms to improve retrieval accuracy.

### Context-Aware Retrieval
When context is provided (lesson ID, section title), the system incorporates it into the search to provide more relevant results.

### Source Citation
All responses include sources from the textbook with relevance scores, allowing users to verify information.

### Caching
Frequently asked questions are cached to improve response times and reduce API costs.

### Fallback Mechanism
If RAG components are unavailable, the system gracefully degrades to provide general assistance.

## Rate Limiting

- Chat endpoint: 30 requests per minute per IP
- Ingestion endpoints: 10 requests per minute per IP
- Health endpoints: 100 requests per minute per IP
- Analytics endpoints: 60 requests per minute per IP

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 429 | Rate Limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

## SDK Examples

### Python
```python
import requests
import json

# Chat with RAG
response = requests.post(
    "http://localhost:8000/api/v1/chat/",
    json={
        "message": "What is Physical AI?",
        "context": {"lesson_id": "lesson-1"}
    }
)
data = response.json()
print(data["message"])
print("Sources:", data["sources"])

# Get analytics
response = requests.get(
    "http://localhost:8000/api/v1/analytics/dashboard",
    params={"days": 7}
)
analytics = response.json()
print("Total queries:", analytics["performance_metrics"]["total_queries"])
```

### JavaScript
```javascript
// Chat with RAG
async function chatWithRAG(message) {
  const response = await fetch('/api/v1/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      context: {
        lesson_id: 'lesson-1',
        chapter_id: 'chapter-1'
      }
    })
  });

  const data = await response.json();
  console.log(data.message);
  console.log('Sources:', data.sources);

  return data;
}

// Submit feedback
async function submitFeedback(queryId, score, comment) {
  const response = await fetch('/api/v1/analytics/feedback', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query_id: queryId,
      score: score,
      comment: comment
    })
  });

  return await response.json();
}
```

## Troubleshooting

### Common Issues

1. **No results found**: Check if ingestion has been completed. Use `/api/v1/ingestion/status` to verify.

2. **Slow responses**: Check the health endpoints for component performance. Enable caching for frequent queries.

3. **High error rate**: Verify API keys are correctly configured in the `.env` file.

4. **Fallback mode active**: Check `/api/v1/health/detailed` to identify which components are unhealthy.

### Logs
Check the application logs for detailed error information:
```bash
# View recent logs
tail -f logs/app.log

# Search for specific errors
grep "ERROR" logs/app.log | tail -20
```

## Support

For issues with the RAG API:
1. Check the health endpoints first
2. Review the logs for error details
3. Consult the troubleshooting guide
4. Create an issue with relevant logs and error messages

## Changelog

### v0.1.0
- Initial RAG implementation
- Basic chat with source citation
- Content ingestion pipeline
- Health monitoring endpoints
- Analytics and usage tracking
- Query expansion and reranking
- Caching for performance optimization