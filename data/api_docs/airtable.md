# Airtable API - Create Records

## Overview
Creates one or more records in an Airtable table. Records are rows in the table, and fields correspond to columns.

## Endpoint
`POST https://api.airtable.com/v0/{baseId}/{tableIdOrName}`

## Authentication
Requires a Personal Access Token or OAuth token with `data.records:write` scope.

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

## Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `baseId` | string | The ID of the base (starts with 'app') |
| `tableIdOrName` | string | Table ID (starts with 'tbl') or table name |

## Request Payload

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `records` | array | Array of record objects to create |

### Record Object
| Field | Type | Description |
|-------|------|-------------|
| `fields` | object | Key-value pairs of field names to values |
| `typecast` | boolean | If true, Airtable auto-converts string values |

## Field Types

### Text Fields
```json
{
  "fields": {
    "Name": "Product Name",
    "Description": "Long text description"
  }
}
```

### Number Fields
```json
{
  "fields": {
    "Price": 99.99,
    "Quantity": 10
  }
}
```

### Single Select
```json
{
  "fields": {
    "Status": "In Progress"
  }
}
```

### Multiple Select
```json
{
  "fields": {
    "Tags": ["urgent", "bug", "frontend"]
  }
}
```

### Checkbox
```json
{
  "fields": {
    "Completed": true
  }
}
```

### Date
```json
{
  "fields": {
    "Due Date": "2024-01-15"
  }
}
```

### URL
```json
{
  "fields": {
    "Website": "https://example.com"
  }
}
```

### Email
```json
{
  "fields": {
    "Contact Email": "user@example.com"
  }
}
```

## Payload Examples

### Create Single Record
```json
{
  "records": [
    {
      "fields": {
        "Name": "Wireless Headphones",
        "Price": 79.99,
        "Category": "Electronics",
        "In Stock": true,
        "URL": "https://store.example.com/p/1001"
      }
    }
  ]
}
```

### Create Multiple Records
```json
{
  "records": [
    {
      "fields": {
        "Name": "Product A",
        "Price": 29.99
      }
    },
    {
      "fields": {
        "Name": "Product B",
        "Price": 49.99
      }
    }
  ],
  "typecast": true
}
```

### Create Record with All Field Types
```json
{
  "records": [
    {
      "fields": {
        "Name": "Task Name",
        "Description": "Detailed task description here",
        "Status": "To Do",
        "Priority": "High",
        "Tags": ["bug", "urgent"],
        "Due Date": "2024-01-20",
        "Estimated Hours": 4,
        "Completed": false,
        "Assignee Email": "dev@company.com"
      }
    }
  ]
}
```

## Response

Returns created records with their IDs:

```json
{
  "records": [
    {
      "id": "rec123456789",
      "createdTime": "2024-01-08T12:00:00.000Z",
      "fields": {
        "Name": "Wireless Headphones",
        "Price": 79.99,
        "Category": "Electronics"
      }
    }
  ]
}
```

## Liquid Template Example

### Single Record
```liquid
{
  "records": [
    {
      "fields": {
        "Name": "{{ product_name }}",
        "Price": {{ price }},
        "URL": "{{ product_url }}"
      }
    }
  ]
}
```

### Multiple Records from Array
```liquid
{
  "records": [{% for item in items %}
    {
      "fields": {
        "Name": "{{ item.name }}",
        "Price": {{ item.price }},
        "URL": "{{ item.url }}"
      }
    }{% unless forloop.last %},{% endunless %}{% endfor %}
  ],
  "typecast": true
}
```

## Rate Limits
- 5 requests per second per base
- Maximum 10 records per request

## Common Errors

| Error | Description |
|-------|-------------|
| 401 | Invalid API key |
| 403 | No access to base or table |
| 404 | Base or table not found |
| 422 | Invalid field name or value type |
| 429 | Rate limit exceeded |
