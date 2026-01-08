# Notion API - Update a Block

## Overview
Updates the content of an existing block in Notion. Used to modify text, toggle lists, callouts, and other block types.

## Endpoint
`PATCH https://api.notion.com/v1/blocks/{block_id}`

## Authentication
Requires a Notion integration token with access to the block's parent page.

Headers:
```
Authorization: Bearer {integration_token}
Notion-Version: 2022-06-28
Content-Type: application/json
```

## Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `block_id` | string | The ID of the block to update |

## Request Payload

The payload varies based on block type. Common block types:

### Paragraph Block
```json
{
  "paragraph": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Updated paragraph content"
        }
      }
    ]
  }
}
```

### Heading Blocks
```json
{
  "heading_2": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Updated Heading"
        }
      }
    ]
  }
}
```

### To-Do Block
```json
{
  "to_do": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Task description"
        }
      }
    ],
    "checked": true
  }
}
```

### Toggle Block
```json
{
  "toggle": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Toggle header text"
        }
      }
    ]
  }
}
```

### Callout Block
```json
{
  "callout": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Important callout message"
        }
      }
    ],
    "icon": {
      "emoji": "💡"
    }
  }
}
```

## Rich Text Options

Rich text supports formatting:

```json
{
  "rich_text": [
    {
      "type": "text",
      "text": {
        "content": "Bold and italic text",
        "link": null
      },
      "annotations": {
        "bold": true,
        "italic": true,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "default"
      }
    }
  ]
}
```

## Payload Examples

### Simple Paragraph Update
```json
{
  "paragraph": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "This paragraph has been updated with new content."
        }
      }
    ]
  }
}
```

### Update To-Do Status
```json
{
  "to_do": {
    "checked": true
  }
}
```

### Callout with Emoji and Link
```json
{
  "callout": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "Check out our ",
          "link": null
        }
      },
      {
        "type": "text",
        "text": {
          "content": "documentation",
          "link": {
            "url": "https://docs.example.com"
          }
        }
      }
    ],
    "icon": {
      "emoji": "📚"
    }
  }
}
```

## Response

Returns the updated block object:

```json
{
  "object": "block",
  "id": "block-id-here",
  "type": "paragraph",
  "paragraph": {
    "rich_text": [...]
  },
  "created_time": "2024-01-01T00:00:00.000Z",
  "last_edited_time": "2024-01-08T12:00:00.000Z"
}
```

## Liquid Template Example

```liquid
{
  "paragraph": {
    "rich_text": [
      {
        "type": "text",
        "text": {
          "content": "{{ new_content }}"
        }
      }
    ]
  }
}
```

## Common Errors

| Error | Description |
|-------|-------------|
| 400 | Invalid block type or malformed payload |
| 401 | Invalid or expired integration token |
| 404 | Block not found or no access |
| 409 | Block has been archived |
