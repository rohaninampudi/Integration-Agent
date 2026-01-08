# Notion API - Create a Page

## Overview
Creates a new page in a Notion database or as a child of an existing page.

## Endpoint
`POST https://api.notion.com/v1/pages`

## Authentication
Requires an integration token with access to the parent database or page.

## Headers
```
Authorization: Bearer {integration_token}
Notion-Version: 2022-06-28
Content-Type: application/json
```

## Request Payload

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `parent` | object | Parent database or page reference |
| `properties` | object | Page properties (must match database schema) |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `children` | array | Page content as block objects |
| `icon` | object | Page icon (emoji or external URL) |
| `cover` | object | Page cover image |

### Parent Object
For database parent:
```json
{
  "database_id": "8a3b1c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
}
```

For page parent:
```json
{
  "page_id": "8a3b1c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
}
```

### Property Types

#### Title Property (Required for pages in databases)
```json
{
  "Name": {
    "title": [
      {
        "text": {
          "content": "Page Title"
        }
      }
    ]
  }
}
```

#### Rich Text Property
```json
{
  "Description": {
    "rich_text": [
      {
        "text": {
          "content": "Some description text"
        }
      }
    ]
  }
}
```

#### Number Property
```json
{
  "Price": {
    "number": 79.99
  }
}
```

#### URL Property
```json
{
  "Link": {
    "url": "https://example.com"
  }
}
```

#### Select Property
```json
{
  "Status": {
    "select": {
      "name": "In Progress"
    }
  }
}
```

#### Multi-Select Property
```json
{
  "Tags": {
    "multi_select": [
      { "name": "Product" },
      { "name": "Electronics" }
    ]
  }
}
```

#### Checkbox Property
```json
{
  "Active": {
    "checkbox": true
  }
}
```

#### Date Property
```json
{
  "Due Date": {
    "date": {
      "start": "2024-01-15",
      "end": "2024-01-20"
    }
  }
}
```

## Payload Examples

### Simple Page in Database
```json
{
  "parent": {
    "database_id": "8a3b1c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
  },
  "properties": {
    "Name": {
      "title": [
        {
          "text": {
            "content": "New Product Entry"
          }
        }
      ]
    }
  }
}
```

### Page with Multiple Properties
```json
{
  "parent": {
    "database_id": "8a3b1c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
  },
  "properties": {
    "Name": {
      "title": [
        {
          "text": {
            "content": "Wireless Headphones"
          }
        }
      ]
    },
    "Price": {
      "number": 79.99
    },
    "URL": {
      "url": "https://store.example.com/p/1001"
    },
    "Category": {
      "select": {
        "name": "Electronics"
      }
    },
    "Tags": {
      "multi_select": [
        { "name": "Audio" },
        { "name": "Wireless" }
      ]
    }
  }
}
```

### Page with Content Blocks
```json
{
  "parent": {
    "database_id": "8a3b1c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
  },
  "properties": {
    "Name": {
      "title": [
        {
          "text": {
            "content": "Product Report"
          }
        }
      ]
    }
  },
  "children": [
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "Summary"
            }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "Found 3 products with average price of $91.66"
            }
          }
        ]
      }
    }
  ]
}
```

### Page with Icon and Cover
```json
{
  "parent": {
    "database_id": "8a3b1c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
  },
  "icon": {
    "emoji": "🎧"
  },
  "cover": {
    "external": {
      "url": "https://example.com/cover.jpg"
    }
  },
  "properties": {
    "Name": {
      "title": [
        {
          "text": {
            "content": "Product Launch"
          }
        }
      ]
    }
  }
}
```

## Response

### Success Response (200 OK)
```json
{
  "object": "page",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created_time": "2024-01-08T12:00:00.000Z",
  "last_edited_time": "2024-01-08T12:00:00.000Z",
  "parent": {
    "type": "database_id",
    "database_id": "8a3b1c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
  },
  "properties": {
    "Name": {
      "id": "title",
      "type": "title",
      "title": [
        {
          "type": "text",
          "text": {
            "content": "Wireless Headphones"
          },
          "plain_text": "Wireless Headphones"
        }
      ]
    }
  },
  "url": "https://www.notion.so/Wireless-Headphones-a1b2c3d4e5f67890abcdef1234567890"
}
```

### Error Response
```json
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "Title is not provided"
}
```

## Common Errors
| Status | Code | Description |
|--------|------|-------------|
| 400 | validation_error | Invalid request payload or missing required fields |
| 401 | unauthorized | Invalid or missing authentication token |
| 403 | restricted_resource | Integration doesn't have access to the resource |
| 404 | object_not_found | Parent database or page not found |
| 409 | conflict_error | Page already exists with this title |
| 429 | rate_limited | Too many requests |

## Liquid Template Example
For a workflow with `scraper_results` array and `notion_database_id`:
```liquid
{
  "parent": {
    "database_id": "{{ notion_database_id }}"
  },
  "properties": {
    "Name": {
      "title": [
        {
          "text": {
            "content": "{{ scraper_results[0].name }}"
          }
        }
      ]
    },
    "Price": {
      "number": {{ scraper_results[0].price }}
    },
    "URL": {
      "url": "{{ scraper_results[0].url }}"
    }
  }
}
```

## Notes
- Property names in the request must exactly match the database schema
- The Title property (usually named "Name") is required for database pages
- Rich text fields support formatting (bold, italic, links, etc.)
- Date properties support both start and end dates for date ranges
