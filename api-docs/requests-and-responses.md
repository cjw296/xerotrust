# Requests and Responses

## Overview

This section covers the general structure of requests and responses for the Xero Accounting API.

## HTTP Methods

| Method | Description |
|--------|-------------|
| **GET** | Retrieve data from the API |
| **POST** | Create new records |
| **PUT** | Update existing records |
| **DELETE** | Delete records |

## HTTP Status Codes

| Code | Description |
|------|-------------|
| **200** | OK - The request was successful |
| **201** | Created - The request was successful and a new resource was created |
| **400** | Bad Request - The request was invalid |
| **401** | Unauthorized - Authentication credentials are missing or invalid |
| **403** | Forbidden - The request is understood but access is denied |
| **404** | Not Found - The requested resource could not be found |
| **500** | Internal Server Error - An error occurred on the server |

## Request Headers

| Header | Description |
|--------|-------------|
| **Authorization** | Bearer token for authentication |
| **Content-Type** | application/json for POST/PUT requests |
| **Accept** | application/json |
| **Xero-tenant-id** | The tenant ID for the organization |

## Response Format

All responses from the Xero API are returned in JSON format.

### Success Response Structure

```json
{
  "Id": "unique-identifier",
  "Status": "OK",
  "ProviderName": "Xero API",
  "DateTimeUTC": "2023-01-01T00:00:00",
  "Data": {
    // Response data here
  }
}
```

### Error Response Structure

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

## Filtering

You can filter results using the `where` parameter:

```
GET /api.xro/2.0/Contacts?where=Name.Contains("ABC")
```

### Supported Operators

| Operator | Description |
|----------|-------------|
| **==** | Equals |
| **!=** | Not equals |
| **>** | Greater than |
| **<** | Less than |
| **>=** | Greater than or equal |
| **<=** | Less than or equal |
| **Contains** | Contains text |
| **StartsWith** | Starts with text |
| **EndsWith** | Ends with text |

## Ordering

You can order results using the `order` parameter:

```
GET /api.xro/2.0/Contacts?order=Name
```

## Pagination

Use the `page` parameter to paginate through results:

```
GET /api.xro/2.0/Contacts?page=2
```

## Modified After

Use the `If-Modified-Since` header to retrieve only records modified after a specific date:

```
If-Modified-Since: 2023-01-01T00:00:00
```

## Rate Limiting

The Xero API has rate limits in place:

- **Per App**: 5000 requests per hour
- **Per User**: 1000 requests per hour
- **Per Tenant**: 1000 requests per hour

## Units Decimal Places

You can specify the number of decimal places for unit amounts using the `unitdp` parameter:

```
GET /api.xro/2.0/Invoices?unitdp=4
```