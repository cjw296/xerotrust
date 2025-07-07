# Response Codes

## Overview

This section covers the HTTP response codes returned by the Xero Accounting API and their meanings.

## Success Codes

| Code | Status | Description |
|------|--------|-------------|
| **200** | OK | The request was successful |
| **201** | Created | The request was successful and a new resource was created |
| **204** | No Content | The request was successful but there is no content to return |

## Client Error Codes

| Code | Status | Description |
|------|--------|-------------|
| **400** | Bad Request | The request was invalid or cannot be served |
| **401** | Unauthorized | Authentication credentials are missing or invalid |
| **403** | Forbidden | The request is understood but access is denied |
| **404** | Not Found | The requested resource could not be found |
| **405** | Method Not Allowed | The request method is not supported for the requested resource |
| **409** | Conflict | The request could not be completed due to a conflict |
| **410** | Gone | The requested resource is no longer available |
| **412** | Precondition Failed | One or more conditions given in the request header fields were false |
| **413** | Request Entity Too Large | The request entity is larger than the server is willing to process |
| **415** | Unsupported Media Type | The request entity has a media type that the server does not support |
| **422** | Unprocessable Entity | The request was well-formed but contains semantic errors |
| **429** | Too Many Requests | Too many requests have been sent in a given amount of time |

## Server Error Codes

| Code | Status | Description |
|------|--------|-------------|
| **500** | Internal Server Error | An error occurred on the server |
| **501** | Not Implemented | The server does not support the functionality required to fulfill the request |
| **502** | Bad Gateway | The server received an invalid response from an upstream server |
| **503** | Service Unavailable | The server is currently unavailable |
| **504** | Gateway Timeout | The server did not receive a timely response from an upstream server |

## Error Response Format

When an error occurs, the API returns a JSON response with error details:

```json
{
  "Type": "ValidationException",
  "Title": "A validation exception occurred",
  "Status": 400,
  "Detail": "Validation failed",
  "Instance": "unique-error-id",
  "Elements": [
    {
      "ValidationErrors": [
        {
          "Message": "Error message"
        }
      ]
    }
  ]
}
```

## Common Error Types

| Type | Description |
|------|-------------|
| **ValidationException** | Request contains invalid data |
| **AuthenticationException** | Authentication failed |
| **AuthorizationException** | Access denied |
| **NotFoundException** | Resource not found |
| **RateLimitException** | Rate limit exceeded |
| **SystemException** | Internal system error |

## Rate Limiting

The API enforces rate limits to ensure fair usage:

- **Per App**: 5000 requests per hour
- **Per User**: 1000 requests per hour  
- **Per Tenant**: 1000 requests per hour

When rate limits are exceeded, the API returns a `429 Too Many Requests` response with headers indicating when the limit resets.

## Retry Logic

For transient errors (5xx codes), implement exponential backoff retry logic:

1. Initial retry after 1 second
2. Double the wait time for each subsequent retry
3. Maximum wait time of 60 seconds
4. Maximum of 3 retry attempts

## Best Practices

1. **Handle all error codes appropriately**
2. **Implement proper retry logic for transient errors**
3. **Respect rate limits and implement backoff strategies**
4. **Log error responses for debugging**
5. **Validate requests before sending to reduce 400 errors**