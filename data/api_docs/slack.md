# Slack Web API - chat.postMessage

## Overview
Posts a message to a public channel, private channel, or direct message conversation.

## Endpoint
`POST https://slack.com/api/chat.postMessage`

## Authentication
Requires a bot token with `chat:write` scope.

## Request Payload

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `channel` | string | Channel ID or name (e.g., `#general`, `C1234567890`) |
| `text` | string | Message text (required if no blocks/attachments) |

### Optional Fields
| Field | Type | Description |
|-------|------|-------------|
| `blocks` | array | Array of block objects for rich formatting |
| `attachments` | array | Array of attachment objects |
| `thread_ts` | string | Timestamp of parent message (for threading) |
| `reply_broadcast` | boolean | Also post to channel when replying in thread |
| `unfurl_links` | boolean | Enable URL unfurling (default: false) |
| `unfurl_media` | boolean | Enable media unfurling (default: true) |
| `mrkdwn` | boolean | Enable Slack markdown parsing (default: true) |
| `parse` | string | Change how messages are treated (`none`, `full`) |
| `link_names` | boolean | Find and link channel names and usernames |
| `metadata` | object | JSON object with `event_type` and `event_payload` |

## Payload Examples

### Simple Text Message
```json
{
  "channel": "#product-alerts",
  "text": "Hello, world!"
}
```

### Message with Markdown
```json
{
  "channel": "C1234567890",
  "text": "*Bold text* and _italic text_\n• Bullet point 1\n• Bullet point 2",
  "mrkdwn": true
}
```

### Message with Blocks (Rich Formatting)
```json
{
  "channel": "#alerts",
  "text": "Fallback text for notifications",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "New Product Alert"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Product:* Wireless Headphones\n*Price:* $79.99"
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "View product details"
      },
      "accessory": {
        "type": "button",
        "text": {
          "type": "plain_text",
          "text": "View"
        },
        "url": "https://example.com/product"
      }
    }
  ]
}
```

### Reply in Thread
```json
{
  "channel": "C1234567890",
  "text": "This is a threaded reply",
  "thread_ts": "1234567890.123456"
}
```

## Response

### Success Response
```json
{
  "ok": true,
  "channel": "C1234567890",
  "ts": "1234567890.123456",
  "message": {
    "type": "message",
    "text": "Hello, world!",
    "user": "U1234567890",
    "ts": "1234567890.123456"
  }
}
```

### Error Response
```json
{
  "ok": false,
  "error": "channel_not_found"
}
```

## Common Errors
| Error | Description |
|-------|-------------|
| `channel_not_found` | The channel does not exist or bot lacks access |
| `not_in_channel` | Bot is not a member of the channel |
| `is_archived` | Channel has been archived |
| `msg_too_long` | Message text exceeds 40,000 characters |
| `no_text` | No text provided and no blocks/attachments |
| `rate_limited` | Too many requests, wait and retry |

## Liquid Template Example
For a workflow with `summary` and `slack_channel` variables:
```liquid
{
  "channel": "{{ slack_channel }}",
  "text": "{{ summary }}"
}
```
